import os, sys
os.chdir(r'D:\PROJECT_FODOWA\backend')
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient
from app.main import app

def test():
    print("=" * 60)
    print("FODOWA CHATBOT - AUTOMATED TESTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Use TestClient which properly handles lifespan events
    with TestClient(app) as c:
        # Test 1: Health endpoint
        print("\n1. Testing GET /health...")
        try:
            r = c.get('/health')
            assert r.status_code == 200
            data = r.json()
            assert data["status"] == "healthy"
            assert data["fixed_faq_count"] == 4
            print(f"   ✅ PASSED: {data}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 2: Fixed FAQ Question 1 - ما هي منصة فودوا
        print("\n2. Testing Fixed FAQ: ما هي منصة فودوا...")
        try:
            r = c.post('/chat', json={'question': 'ما هي منصة فودوا'})
            assert r.status_code == 200
            data = r.json()
            assert data['confidence'] >= 0.5
            assert 'فودوا' in data['answer'] or 'منصة' in data['answer']
            print(f"   ✅ PASSED: confidence={data['confidence']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 3: Fixed FAQ Question 2 - اللغات
        print("\n3. Testing Fixed FAQ: ما هي اللغات المتوفرة...")
        try:
            r = c.post('/chat', json={'question': 'ما هي اللغات المتوفرة'})
            assert r.status_code == 200
            data = r.json()
            assert data['confidence'] >= 0.5
            print(f"   ✅ PASSED: confidence={data['confidence']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 4: Fixed FAQ Question 3 - الأمان
        print("\n4. Testing Fixed FAQ: هل الموقع آمن...")
        try:
            r = c.post('/chat', json={'question': 'هل الموقع آمن'})
            assert r.status_code == 200
            data = r.json()
            assert data['confidence'] >= 0.5
            print(f"   ✅ PASSED: confidence={data['confidence']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 5: Fixed FAQ Question 4 - كيف أبدأ
        print("\n5. Testing Fixed FAQ: كيف أبدأ...")
        try:
            r = c.post('/chat', json={'question': 'كيف أبدأ'})
            assert r.status_code == 200
            data = r.json()
            assert data['confidence'] >= 0.5
            print(f"   ✅ PASSED: confidence={data['confidence']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 6: Empty question
        print("\n6. Testing POST /chat (empty)...")
        try:
            r = c.post('/chat', json={'question': ''})
            # Pydantic validation returns 422, our custom validation returns 400
            assert r.status_code in [400, 422]
            print("   ✅ PASSED: Rejects empty question")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 7: Root endpoint
        print("\n7. Testing GET / (root)...")
        try:
            r = c.get('/')
            assert r.status_code == 200
            assert 'chat' in r.text.lower()
            print("   ✅ PASSED: Returns HTML chat UI")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        
        # Test 8: Validate endpoint
        print("\n8. Testing POST /validate...")
        try:
            r = c.post('/validate', json={'question': 'كيف أبدأ'})
            assert r.status_code == 200
            data = r.json()
            print(f"   ✅ PASSED: confidence={data['confidence_score']:.2f}")
            passed += 1
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Ready for deployment!")
    return failed == 0

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
