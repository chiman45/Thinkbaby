"""
RAG System for Government Schemes with Web Scraping and Credibility Scoring
Loads government schemes from CSV, creates embeddings, searches web if needed, and scores credibility.
"""

import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json
import csv
from typing import List, Dict, Any, Tuple
import re
import random
from datetime import datetime
import os


class GovernmentSchemesRAG:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize RAG system with ChromaDB and SentenceTransformer."""
        print("Initializing Government Schemes RAG system...")
        
        # Initialize ChromaDB client with PERSISTENT storage
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        # Create/get collection for government schemes
        self.collection = self.chroma_client.get_or_create_collection(
            name="government_schemes",
            metadata={"description": "Government welfare schemes and programs"}
        )
        
        # Initialize sentence transformer for embeddings
        print("Loading embedding model: all-MiniLM-L6-v2...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Ollama URL
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3.2"
        
        # Store loaded schemes
        self.schemes = []
        
    def load_schemes_from_csv(self, csv_path: str = "data/updated_data.csv", force_reindex: bool = False):
        """Load government schemes from CSV file and create embeddings only if needed."""
        # Check if embeddings already exist
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_reindex:
            print(f"✓ Found existing embeddings: {existing_count} schemes")
            print("✓ Skipping embedding generation (already exists)")
            print("💡 To regenerate embeddings, delete the 'chroma_db' folder or restart with force_reindex=True")
            
            # Still load schemes data for queries
            print(f"Loading scheme metadata from {csv_path}...")
            schemes = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    schemes.append(row)
            self.schemes = schemes
            print(f"✓ Loaded {len(schemes)} schemes metadata")
            return len(schemes)
        
        # No existing embeddings or force reindex - create new ones
        print(f"Loading schemes from {csv_path}...")
        
        schemes = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                schemes.append(row)
        
        print(f"Loaded {len(schemes)} schemes")
        self.schemes = schemes
        
        # Index all schemes
        self._index_schemes()
        
        print(f"✓ Indexed {len(schemes)} government schemes")
        return len(schemes)
    
    def _scheme_to_text(self, scheme: Dict) -> str:
        """Convert scheme dictionary to searchable text format."""
        parts = []
        
        if scheme.get('scheme_name'):
            parts.append(f"Scheme: {scheme['scheme_name']}")
        
        if scheme.get('level'):
            parts.append(f"Level: {scheme['level']}")
        
        if scheme.get('schemeCategory'):
            parts.append(f"Category: {scheme['schemeCategory']}")
        
        if scheme.get('details'):
            # Truncate details to avoid too long text
            details = scheme['details'][:500]
            parts.append(f"Details: {details}")
        
        if scheme.get('benefits'):
            benefits = scheme['benefits'][:300]
            parts.append(f"Benefits: {benefits}")
        
        if scheme.get('eligibility'):
            eligibility = scheme['eligibility'][:300]
            parts.append(f"Eligibility: {eligibility}")
        
        if scheme.get('tags'):
            parts.append(f"Tags: {scheme['tags']}")
        
        return " | ".join(parts)
    
    def _index_schemes(self):
        """Create embeddings for all schemes and store in ChromaDB."""
        if not self.schemes:
            print("No schemes to index")
            return
        
        print("Creating embeddings for schemes...")
        
        # Convert schemes to text
        documents = [self._scheme_to_text(scheme) for scheme in self.schemes]
        
        # Create embeddings
        print(f"Generating embeddings for {len(documents)} schemes...")
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Prepare metadata and IDs
        metadatas = []
        ids = []
        for i, scheme in enumerate(self.schemes):
            metadatas.append({
                "scheme_name": scheme.get('scheme_name', '')[:500],  # ChromaDB metadata limit
                "level": scheme.get('level', ''),
                "category": scheme.get('schemeCategory', '')[:200],
                "slug": scheme.get('slug', '')
            })
            ids.append(f"scheme_{i}")
        
        # Clear existing collection only if it has data
        if self.collection.count() > 0:
            print("Clearing old embeddings...")
            try:
                self.chroma_client.delete_collection("government_schemes")
                self.collection = self.chroma_client.create_collection(
                    name="government_schemes",
                    metadata={"description": "Government welfare schemes and programs"}
                )
            except:
                pass
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✓ Indexed {len(self.schemes)} schemes into vector database")
    
    def search_schemes(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant schemes using semantic similarity."""
        # Create query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        relevant_schemes = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                scheme_id = results['ids'][0][i]
                scheme_index = int(scheme_id.split('_')[1])
                
                relevant_schemes.append({
                    'scheme': self.schemes[scheme_index],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'text': results['documents'][0][i]
                })
        
        return relevant_schemes
    
    def webscrape_info(self, query: str) -> Dict[str, Any]:
        """Scrape web for additional information from TRUSTED SOURCES ONLY (government/official sites)."""
        print(f"🌐 Webscraping trusted sources for: {query}")
        
        # List of trusted government and official domains
        TRUSTED_DOMAINS = [
            'gov.in', 'nic.in', 'india.gov.in',  # Indian government
            'pib.gov.in',  # Press Information Bureau
            'niti.gov.in',  # NITI Aayog
            'makeinindia.com',  # Make in India
            'digitalindia.gov.in',  # Digital India
            'mygov.in',  # MyGov India
            'pmjdy.gov.in',  # PM Jan Dhan Yojana
            'pmjay.gov.in',  # Ayushman Bharat
            'uidai.gov.in',  # UIDAI (Aadhaar)
            'epfindia.gov.in',  # EPFO
            'esic.nic.in',  # ESIC
            'wikipedia.org',  # Wikipedia (for general info)
            'govt',  # Generic government sites
        ]
        
        try:
            # Strategy 1: Try DuckDuckGo with site-specific search for government sites
            gov_query = f"{query} site:gov.in OR site:nic.in"
            ddg_url = f"https://api.duckduckgo.com/?q={gov_query}&format=json&pretty=1"
            
            response = requests.get(ddg_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                abstract = data.get('Abstract', '')
                source = data.get('AbstractSource', '')
                url = data.get('AbstractURL', '')
                
                # Verify source is from trusted domain
                is_trusted = False
                if url:
                    for domain in TRUSTED_DOMAINS:
                        if domain in url.lower():
                            is_trusted = True
                            break
                
                if abstract and is_trusted:
                    print(f"✅ Found trusted source: {source}")
                    return {
                        'found': True,
                        'content': abstract,
                        'source': source,
                        'url': url,
                        'credibility': 0.75,  # High credibility for government sites
                        'is_government': True
                    }
                elif abstract:
                    # Found info but not from trusted source
                    print(f"⚠️ Found info but source not verified: {source}")
                    return {
                        'found': True,
                        'content': abstract,
                        'source': source,
                        'url': url,
                        'credibility': 0.4,  # Low credibility for unverified
                        'is_government': False
                    }
            
            # Strategy 2: Try general search with government keywords
            gov_keywords_query = f"{query} government scheme india official"
            ddg_url2 = f"https://api.duckduckgo.com/?q={gov_keywords_query}&format=json&pretty=1"
            
            response2 = requests.get(ddg_url2, timeout=5)
            
            if response2.status_code == 200:
                data2 = response2.json()
                abstract2 = data2.get('Abstract', '')
                source2 = data2.get('AbstractSource', '')
                url2 = data2.get('AbstractURL', '')
                
                # Check if this result is from trusted source
                is_trusted2 = False
                if url2:
                    for domain in TRUSTED_DOMAINS:
                        if domain in url2.lower():
                            is_trusted2 = True
                            break
                
                if abstract2 and is_trusted2:
                    print(f"✅ Found trusted source (attempt 2): {source2}")
                    return {
                        'found': True,
                        'content': abstract2,
                        'source': source2,
                        'url': url2,
                        'credibility': 0.7,
                        'is_government': True
                    }
                elif abstract2:
                    print(f"⚠️ Found info but not from government source")
                    return {
                        'found': True,
                        'content': abstract2,
                        'source': source2,
                        'url': url2,
                        'credibility': 0.35,
                        'is_government': False
                    }
                    
        except Exception as e:
            print(f"❌ Webscrape error: {e}")
        
        # No results found
        print(f"❌ No trusted sources found for: {query}")
        return {
            'found': False,
            'content': 'No information found from government or trusted official sources.',
            'source': 'None',
            'url': '',
            'credibility': 0.0,
            'is_government': False
        }
    
    def calculate_credibility(self, query: str, schemes: List[Dict], web_result: Dict = None) -> float:
        """Calculate credibility score (0.0 to 1.0) based on match quality and source."""
        if not schemes and not (web_result and web_result.get('found')):
            return 0.0
        
        # Start with base credibility
        credibility = 0.0
        
        # From database schemes (high credibility - official government data)
        if schemes:
            best_similarity = max([s['similarity'] for s in schemes])
            
            # Base credibility from government database: 0.7-1.0
            db_credibility = 0.7 + (best_similarity * 0.3)
            credibility = max(credibility, db_credibility)
        
        # From web scraping - PRIORITIZE GOVERNMENT SOURCES
        if web_result and web_result.get('found'):
            web_credibility = web_result.get('credibility', 0.5)
            is_government = web_result.get('is_government', False)
            
            # If web source is government, give it higher weight
            if is_government:
                # Government web source: 0.7-0.85 credibility
                if schemes:
                    # Both DB and gov web: weighted average (80% DB, 20% web)
                    credibility = (credibility * 0.8) + (web_credibility * 0.2)
                else:
                    # Only gov web source
                    credibility = web_credibility
            else:
                # Non-government web source: lower credibility
                if schemes:
                    # Both DB and non-gov web: mostly ignore web (90% DB, 10% web)
                    credibility = (credibility * 0.9) + (web_credibility * 0.1)
                else:
                    # Only non-gov web source: low credibility
                    credibility = web_credibility * 0.6  # Reduce further
        
        return min(credibility, 1.0)
    
    def generate_response(self, query: str, context: str, max_words: int = 65) -> str:
        """Generate AI response using Ollama with word limit."""
        prompt = f"""Based on the following government schemes information, provide a concise answer to the query.

IMPORTANT: Your response must be EXACTLY 60-70 words. Count carefully.

Context:
{context}

Query: {query}

Provide a helpful, accurate response in 60-70 words only. If information is from web sources, mention it briefly:"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 100  # Limit tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                # Enforce word limit (60-70 words)
                words = ai_response.split()
                if len(words) > max_words:
                    ai_response = ' '.join(words[:max_words]) + '...'
                elif len(words) < 60:
                    # Pad if too short
                    ai_response = ai_response + f" Check eligibility criteria carefully."
                
                return ai_response
            
        except Exception as e:
            print(f"Ollama error: {e}")
        
        # Fallback response
        return f"Based on available data, relevant schemes may exist. Please verify from official government sources before applying. Check eligibility and required documents carefully."
    
    def query_with_credibility(self, user_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Main query function: Search schemes, webscrape if needed, calculate credibility, generate response.
        Returns: Full response with credibility score and breakdown.
        """
        print(f"\n🔍 Processing query: {user_query}")
        
        # Step 1: Search in database
        relevant_schemes = self.search_schemes(user_query, top_k=top_k)
        
        # Step 2: Check if we need web scraping (low similarity threshold)
        best_similarity = max([s['similarity'] for s in relevant_schemes]) if relevant_schemes else 0.0
        web_result = None
        
        if best_similarity < 0.4:  # Threshold for web search
            print("⚠ Low similarity, initiating web search...")
            web_result = self.webscrape_info(user_query)
        
        # Step 3: Build context
        context_parts = []
        
        if relevant_schemes:
            context_parts.append("📋 GOVERNMENT SCHEMES:")
            for i, item in enumerate(relevant_schemes[:2], 1):  # Top 2 schemes
                scheme = item['scheme']
                context_parts.append(f"\n{i}. {scheme.get('scheme_name', 'Unknown')}")
                context_parts.append(f"   Benefits: {scheme.get('benefits', 'N/A')[:150]}...")
                context_parts.append(f"   Eligibility: {scheme.get('eligibility', 'N/A')[:150]}...")
        
        if web_result and web_result.get('found'):
            context_parts.append(f"\n🌐 WEB INFO: {web_result['content'][:300]}")
            context_parts.append(f"   Source: {web_result['source']}")
        
        context = '\n'.join(context_parts)
        
        # Step 4: Calculate credibility
        credibility_score = self.calculate_credibility(user_query, relevant_schemes, web_result)
        
        # Step 5: Generate AI response (60-70 words)
        ai_response = self.generate_response(user_query, context, max_words=70)
        
        # Step 6: Create breakdown (concise)
        breakdown_parts = []
        if relevant_schemes:
            breakdown_parts.append(f"✓ {len(relevant_schemes)} scheme(s) found")
            breakdown_parts.append(f"Top: {relevant_schemes[0]['scheme'].get('scheme_name', 'N/A')[:50]}")
        if web_result and web_result.get('found'):
            breakdown_parts.append(f"+ Web: {web_result['source']}")
        
        breakdown = " | ".join(breakdown_parts) if breakdown_parts else "No direct match found"
        
        # Return complete response
        return {
            'query': user_query,
            'response': ai_response,
            'credibility_score': round(credibility_score, 2),
            'credibility_label': self._get_credibility_label(credibility_score),
            'breakdown': breakdown,
            'schemes_found': len(relevant_schemes),
            'web_searched': web_result is not None,
            'relevant_schemes': relevant_schemes,
            'web_result': web_result
        }
    
    def _get_credibility_label(self, score: float) -> str:
        """Convert credibility score to human-readable label."""
        if score >= 0.8:
            return "High (Verified Government)"
        elif score >= 0.6:
            return "Medium (Multiple Sources)"
        elif score >= 0.4:
            return "Low (Limited Info)"
        else:
            return "Very Low (Unverified)"
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded schemes."""
        return {
            'total_schemes': len(self.schemes),
            'collection_count': self.collection.count()
        }


def test_system():
    """Test the RAG system with sample queries."""
    print("="*60)
    print("GOVERNMENT SCHEMES RAG SYSTEM TEST")
    print("="*60)
    
    # Initialize
    rag = GovernmentSchemesRAG()
    
    # Load CSV data
    count = rag.load_schemes_from_csv("data/updated_data.csv")
    print(f"\n✓ Loaded {count} schemes")
    
    # Test queries
    test_queries = [
        "farmer insurance scheme",
        "financial assistance for women entrepreneurs",
        "education scholarship for SC/ST students",
        "completely unrelated random topic xyz123"  # Should trigger web search
    ]
    
    print("\n" + "="*60)
    print("TESTING QUERIES")
    print("="*60)
    
    for query in test_queries:
        result = rag.query_with_credibility(query)
        
        print(f"\n📌 Query: {result['query']}")
        print(f"💬 Response: {result['response']}")
        print(f"📊 Credibility: {result['credibility_score']} ({result['credibility_label']})")
        print(f"📋 Breakdown: {result['breakdown']}")
        print(f"   - Schemes found: {result['schemes_found']}")
        print(f"   - Web searched: {result['web_searched']}")
        print("-"*60)
    
    # Stats
    stats = rag.get_stats()
    print(f"\n📈 SYSTEM STATS:")
    print(f"   Total schemes: {stats['total_schemes']}")
    print(f"   Indexed: {stats['collection_count']}")
    print("\n✓ All tests completed!")


if __name__ == "__main__":
    test_system()
