/**
 * Simple Test Suite
 * Run quick tests on individual modules
 */

const { analyzeMessage } = require('./modules/claimExtractor');
const { generateClaimHash, verifyHashMatch } = require('./modules/hashGenerator');

console.log('🧪 Running Simple Tests\n');

async function testClaimExtractor() {
  console.log('Test 1: Claim Extractor');
  console.log('─'.repeat(60));
  
  const testCases = [
    'Government giving ₹5000 to all students! Forward immediately!',
    'Breaking news: New cryptocurrency launched by Elon Musk',
    'Scientists discover cure for common cold',
    'Normal weather report for tomorrow'
  ];

  for (const text of testCases) {
    const result = await analyzeMessage(text);
    console.log(`\nInput: "${text}"`);
    console.log(`Risk Score: ${result.riskScore}%`);
    console.log(`Claims: ${result.claims.join(', ')}`);
  }
  console.log('\n');
}

function testHashGenerator() {
  console.log('Test 2: Hash Generator');
  console.log('─'.repeat(60));
  
  const claim1 = 'Government giving ₹5000 to students';
  const claim2 = 'Government giving ₹5000 to students'; // Same
  const claim3 = 'Government giving Rs 5000 to students'; // Different
  
  const hash1 = generateClaimHash(claim1);
  const hash2 = generateClaimHash(claim2);
  const hash3 = generateClaimHash(claim3);
  
  console.log(`\nClaim 1: "${claim1}"`);
  console.log(`Hash 1: ${hash1}`);
  console.log(`\nClaim 2: "${claim2}"`);
  console.log(`Hash 2: ${hash2}`);
  console.log(`\nSame hash? ${hash1 === hash2 ? '✅ YES' : '❌ NO'}`);
  
  console.log(`\nClaim 3: "${claim3}"`);
  console.log(`Hash 3: ${hash3}`);
  console.log(`Same as hash1? ${hash1 === hash3 ? '✅ YES' : '❌ NO'}\n`);
}

async function runTests() {
  await testClaimExtractor();
  testHashGenerator();
  console.log('✅ All tests completed!\n');
}

runTests().catch(console.error);
