"""Test script for chatbot API endpoints."""

import urllib.request
import json

BASE_URL = "http://127.0.0.1:10000"

def test_endpoint(method, path, data=None):
    """Test an API endpoint."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if data else {}
    
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, method=method)
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        return {"success": True, "status": response.status, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

print("=" * 60)
print("CHATBOT API TEST SUITE")
print("=" * 60)

# Test 1: Root endpoint
print("\n1. Testing GET /")
result = test_endpoint("GET", "/")
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 2: Health endpoint
print("\n2. Testing GET /health")
result = test_endpoint("GET", "/health")
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 3: Chat endpoint
print("\n3. Testing POST /chat")
result = test_endpoint("POST", "/chat", {"question": "What are your business hours?"})
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 4: Chat endpoint with different question
print("\n4. Testing POST /chat (tracking)")
result = test_endpoint("POST", "/chat", {"question": "How do I track my order?"})
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 5: Validate endpoint
print("\n5. Testing POST /validate")
result = test_endpoint("POST", "/validate", {"question": "What payment methods do you accept?"})
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 6: Validate endpoint with low confidence question
print("\n6. Testing POST /validate (low confidence)")
result = test_endpoint("POST", "/validate", {"question": "xyzabc unknown question"})
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

# Test 7: Logs endpoint
print("\n7. Testing GET /logs")
result = test_endpoint("GET", "/logs")
print(f"   Status: {result.get('status', 'N/A')}")
data = result.get('data', result)
if isinstance(data, dict):
    print(f"   Log count: {data.get('returned_count', 0)}")
    print(f"   Statistics: {json.dumps(data.get('statistics', {}), indent=2)}")

# Test 8: Integration prepare endpoint
print("\n8. Testing POST /integration/prepare")
result = test_endpoint("POST", "/integration/prepare", {"message": "Test message for integration"})
print(f"   Status: {result.get('status', 'N/A')}")
print(f"   Response: {json.dumps(result.get('data', result), indent=2)}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
