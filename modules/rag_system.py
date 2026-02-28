"""
RAG (Retrieval Augmented Generation) System for Government Records
Hackathon-optimized: Fast setup with ChromaDB + Sentence Transformers
"""

import json
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import requests


class GovernmentRecordRAG:
    """Simple RAG system for government records verification"""
    
    def __init__(self, data_path: str = "data/government_records.json"):
        """Initialize RAG system with ChromaDB and sentence transformer"""
        
        # Initialize ChromaDB (in-memory for fast hackathon demo)
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="government_records",
            metadata={"description": "Government records for claim verification"}
        )
        
        # Initialize embedding model (fast, lightweight)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 80MB, fast
        
        # Load government records
        self.data_path = data_path
        self.records = []
        
        print("RAG system initialized!")
    
    def load_records(self) -> int:
        """Load government records from JSON file"""
        
        if not os.path.exists(self.data_path):
            print(f"⚠️  Data file not found: {self.data_path}")
            return 0
        
        with open(self.data_path, 'r') as f:
            self.records = json.load(f)
        
        print(f"✅ Loaded {len(self.records)} government records")
        
        # Add records to ChromaDB
        self._index_records()
        
        return len(self.records)
    
    def _index_records(self):
        """Create embeddings and store in ChromaDB"""
        
        if not self.records:
            print("⚠️  No records to index")
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for record in self.records:
            # Create text representation for embedding
            doc_text = self._record_to_text(record)
            documents.append(doc_text)
            
            # Store metadata
            metadatas.append({
                "type": record.get("type", "unknown"),
                "full_name": record.get("full_name", ""),
                "status": record.get("status", ""),
            })
            
            ids.append(record["id"])
        
        # Add to ChromaDB (it handles embeddings automatically, but we use custom model)
        embeddings = self.embedding_model.encode(documents).tolist()
        
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Indexed {len(documents)} records into vector database")
    
    def _record_to_text(self, record: Dict) -> str:
        """Convert record to searchable text"""
        
        # Create rich text representation
        parts = []
        
        for key, value in record.items():
            if key != "id" and value:
                if isinstance(value, list):
                    parts.append(f"{key}: {', '.join(map(str, value))}")
                else:
                    parts.append(f"{key}: {value}")
        
        return " | ".join(parts)
    
    def search_records(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant government records"""
        
        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        relevant_records = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                # Find full record
                record = next((r for r in self.records if r['id'] == doc_id), None)
                if record:
                    # Add similarity score
                    record['similarity_score'] = 1 - results['distances'][0][i] if 'distances' in results else 1.0
                    relevant_records.append(record)
        
        return relevant_records
    
    def verify_claim(self, claim_text: str, top_k: int = 3) -> Dict:
        """Verify a claim against government records"""
        
        # Search for relevant records
        relevant_records = self.search_records(claim_text, top_k=top_k)
        
        # Check for fraud indicators
        fraud_records = [r for r in relevant_records if r.get('type') == 'fraud_case']
        
        # Build context for LLM
        context = self._build_context(relevant_records)
        
        return {
            "relevant_records": relevant_records,
            "fraud_indicators": len(fraud_records),
            "context": context,
            "risk_level": "high" if fraud_records else "low"
        }
    
    def _build_context(self, records: List[Dict]) -> str:
        """Build context string for LLM"""
        
        if not records:
            return "No relevant government records found."
        
        context_parts = ["RELEVANT GOVERNMENT RECORDS:\n"]
        
        for i, record in enumerate(records, 1):
            context_parts.append(f"\n{i}. {record.get('type', 'Unknown').upper()}")
            context_parts.append(f"   Name: {record.get('full_name', 'N/A')}")
            context_parts.append(f"   Status: {record.get('status', 'N/A')}")
            
            # Add specific details based on type
            if record.get('type') == 'fraud_case':
                context_parts.append(f"   ⚠️ FRAUD CASE")
                context_parts.append(f"   Claim Type: {record.get('claim_type', 'N/A')}")
                context_parts.append(f"   Amount: ${record.get('amount_claimed', 0):,}")
                if 'fraud_indicators' in record:
                    context_parts.append(f"   Red Flags: {', '.join(record['fraud_indicators'])}")
            else:
                # Valid record
                context_parts.append(f"   ✅ VERIFIED RECORD")
                if 'certificate_number' in record:
                    context_parts.append(f"   Certificate: {record['certificate_number']}")
            
            context_parts.append(f"   Details: {record.get('metadata', 'N/A')}")
        
        return "\n".join(context_parts)
    
    def chat_with_rag(self, user_message: str, max_words: int = 100) -> str:
        """Query Ollama with RAG context"""
        
        # Get relevant records
        verification = self.verify_claim(user_message)
        
        # Build prompt with context
        prompt = f"""You are a government records verification assistant. Use the following records to answer the user's question.

{verification['context']}

RISK LEVEL: {verification['risk_level'].upper()}

User question: {user_message}

Instructions:
- Answer based on the government records provided
- If fraud indicators are found, clearly warn the user
- Be direct and concise (max {max_words} words)
- If no records match, say "No records found"

Answer:"""
        
        # Call Ollama
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower for more factual responses
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "Error generating response")
                
                # Truncate if needed
                words = answer.split()
                if len(words) > max_words:
                    answer = " ".join(words[:max_words]) + "..."
                
                return answer
            else:
                return f"Error: Ollama returned status {response.status_code}"
        
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def add_record(self, record: Dict) -> bool:
        """Add new government record to the system"""
        
        # Validate record
        if 'id' not in record:
            print("⚠️  Record must have 'id' field")
            return False
        
        # Add to records list
        self.records.append(record)
        
        # Index the new record
        doc_text = self._record_to_text(record)
        embedding = self.embedding_model.encode(doc_text).tolist()
        
        self.collection.add(
            embeddings=[embedding],
            documents=[doc_text],
            metadatas=[{
                "type": record.get("type", "unknown"),
                "full_name": record.get("full_name", ""),
                "status": record.get("status", ""),
            }],
            ids=[record["id"]]
        )
        
        print(f"✅ Added record: {record['id']}")
        return True
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        
        total_records = len(self.records)
        fraud_cases = len([r for r in self.records if r.get('type') == 'fraud_case'])
        valid_records = total_records - fraud_cases
        
        return {
            "total_records": total_records,
            "valid_records": valid_records,
            "fraud_cases": fraud_cases,
            "collection_count": self.collection.count()
        }


# Quick test function
def test_rag():
    """Test RAG system"""
    print("\n=== Testing RAG System ===\n")
    
    rag = GovernmentRecordRAG()
    rag.load_records()
    
    # Test queries
    test_queries = [
        "Check John Doe birth certificate",
        "Verify Michael Chen death benefit claim",
        "Is there a marriage record for Emily Davis?",
        "Search for fraud cases with identity theft"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 60)
        
        verification = rag.verify_claim(query)
        print(f"Risk Level: {verification['risk_level'].upper()}")
        print(f"Fraud Indicators: {verification['fraud_indicators']}")
        print(f"\nTop {len(verification['relevant_records'])} matches:")
        
        for record in verification['relevant_records']:
            print(f"  - {record.get('type')}: {record.get('full_name')} (similarity: {record.get('similarity_score', 0):.2f})")
    
    # Test with Ollama
    print("\n\n=== Testing with Ollama ===\n")
    answer = rag.chat_with_rag("Is Michael Chen's death benefit claim legitimate?", max_words=50)
    print(f"Answer: {answer}")
    
    # Stats
    print("\n\n=== System Stats ===")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_rag()
