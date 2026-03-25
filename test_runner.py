"""Direct test runner - run this file to execute all tests."""
import sys
import os

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# Import and run tests manually
print("=" * 60)
print("FAQ CHATBOT - AUTOMATED TESTS")
print("=" * 60)

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

passed = 0
failed = 0

async def run_all_tests():
    global passed, failed
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        
        # Test 1: Health endpoint
        print("\n1. Testing GET /health...")
        try:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["faq_loaded"] is True
            print("   ✅ PASSED: Health check returns 200 OK")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 2: Chat endpoint with known question
        print("\n2. Testing POST /chat (known question)...")
        try:
            response = await client.post("/chat", json={"question": "What are your business hours?"})
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "confidence" in data
            assert data["confidence"] > 0
            print(f"   ✅ PASSED: Got answer with confidence {data['confidence']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 3: Chat endpoint with unknown question
        print("\n3. Testing POST /chat (unknown question)...")
        try:
            response = await client.post("/chat", json={"question": "xyzabc random unknown"})
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            print("   ✅ PASSED: Returns fallback response")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 4: Chat rejects empty question
        print("\n4. Testing POST /chat (empty question)...")
        try:
            response = await client.post("/chat", json={"question": ""})
            assert response.status_code == 400
            print("   ✅ PASSED: Rejects empty question with 400")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 5: Root endpoint returns HTML
        print("\n5. Testing GET / (root)...")
        try:
            response = await client.get("/")
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            assert "chat" in response.text.lower()
            print("   ✅ PASSED: Returns HTML chat UI")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 6: Validate endpoint
        print("\n6. Testing POST /validate...")
        try:
            response = await client.post("/validate", json={"question": "How do I track my order?"})
            assert response.status_code == 200
            data = response.json()
            assert "confidence_score" in data
            assert "confidence_label" in data
            print(f"   ✅ PASSED: Returns detailed validation")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 7: Logs endpoint
        print("\n7. Testing GET /logs...")
        try:
            response = await client.get("/logs")
            assert response.status_code == 200
            data = response.json()
            assert "logs" in data
            assert "statistics" in data
            print("   ✅ PASSED: Returns logs and statistics")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1

# Run tests
asyncio.run(run_all_tests())

print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if failed == 0:
    print("✅ ALL TESTS PASSED - Ready for deployment!")
else:
    print("⚠️ Some tests failed - review errors above")

sys.exit(0 if failed == 0 else 1)
