# API Error Handling & Debugging Guide

## 🚨 Common API Issues & Solutions

### 1. **Network Connectivity Issues**

#### Problem: Connection Timeout
```
Error: requests.exceptions.ConnectionError: Connection aborted
```

**What happens:**
- API is unreachable (network down, firewall blocking, etc.)
- Request hangs and eventually times out

**Current behavior in tests:**
```python
try:
    response = requests.get(f"{BASE_URL}/posts")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

**Solution:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def requests_with_retries():
    session = requests.Session()
    retry = Retry(
        total=3,           # Retry 3 times
        connect=3,
        backoff_factor=0.5  # 0.5s, 1s, 2s delays
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Usage
session = requests_with_retries()
response = session.get(f"{BASE_URL}/posts", timeout=5)
```

---

### 2. **API Server Down (5xx Errors)**

#### Problem: 500 Internal Server Error
```
Status Code: 500
Response: {"error": "Internal Server Error"}
```

**What happens:**
- API server crashed or encountered an unexpected error
- Your request is valid but server can't process it
- Tests fail with assertion error

**Current code:**
```python
assert response.status_code == 200  # ❌ Fails when status is 500
```

**Better approach with error handling:**
```python
response = requests.get(f"{BASE_URL}/posts")

if response.status_code >= 500:
    print(f"❌ Server error (status {response.status_code})")
    print(f"Response: {response.text}")
    # Retry or escalate
    
elif response.status_code >= 400:
    print(f"❌ Client error (status {response.status_code})")
    print(f"Details: {response.json().get('error', 'Unknown error')}")
    
else:
    print(f"✅ Success (status {response.status_code})")
```

---

### 3. **Invalid Response (Malformed JSON)**

#### Problem: Invalid JSON Response
```
json.decoder.JSONDecodeError: Expecting value
```

**What happens:**
- API returns non-JSON response (HTML error page, plain text, etc.)
- `response.json()` call fails
- Test crashes with JSONDecodeError

**Failing code:**
```python
data = response.json()  # ❌ Crashes if response isn't JSON
```

**Safe approach:**
```python
try:
    data = response.json()
except ValueError as e:
    print(f"❌ Invalid JSON response: {e}")
    print(f"Response text: {response.text[:200]}")  # Show first 200 chars
    data = None
```

---

### 4. **Rate Limiting (429 Too Many Requests)**

#### Problem: Rate Limit Exceeded
```
Status Code: 429
Response: {"error": "Rate limit exceeded. Try again after 60 seconds"}
```

**What happens:**
- API throttles requests (too many in short time)
- Tests fail intermittently
- Production requests get blocked

**Handle it:**
```python
import time

response = requests.get(f"{BASE_URL}/posts")

if response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    print(f"⏸️  Rate limited. Waiting {retry_after}s...")
    time.sleep(int(retry_after))
    # Retry request
    response = requests.get(f"{BASE_URL}/posts")
```

---

### 5. **Timeout Issues**

#### Problem: Request Takes Too Long
```
requests.exceptions.Timeout: HTTPSConnectionPool(host='jsonplaceholder.typicode.com', port=443): Read timed out
```

**What happens:**
- API is slow or unresponsive
- Request hangs indefinitely
- Eventually fails with timeout error

**Without timeout:**
```python
response = requests.get(f"{BASE_URL}/posts")  # ❌ Could hang forever
```

**With timeout:**
```python
try:
    response = requests.get(
        f"{BASE_URL}/posts",
        timeout=5  # Fail after 5 seconds
    )
except requests.exceptions.Timeout:
    print("❌ Request timed out (> 5 seconds)")
```

---

### 6. **Unexpected Status Codes**

#### Problem: Got 404 Instead of 200
```
Status Code: 404
Response: {"error": "Not Found"}
```

**What happens:**
- Endpoint changed or was removed
- URL is incorrect
- API doesn't support that operation
- Tests fail

**Better assertion:**
```python
response = requests.get(f"{BASE_URL}/posts/invalid-id")

if response.status_code == 404:
    print("❌ Resource not found (404)")
    
elif response.status_code == 403:
    print("❌ Access forbidden (403)")
    
elif response.status_code == 401:
    print("❌ Authentication required (401)")
    
elif 200 <= response.status_code < 300:
    print("✅ Success")
    
else:
    print(f"❌ Unexpected status: {response.status_code}")
```

---

## 📊 **Test Behavior in Different Scenarios**

### Scenario 1: API is Down
```
$ python3 test_api.py

============================================================
🚀 JSONPlaceholder API Test Suite
============================================================

🔍 Testing: GET /posts
❌ Error: Connection refused

============================================================
❌ All tests FAILED!
============================================================
```

**Exit code:** 1 (failure)

### Scenario 2: API Returns Invalid JSON
```
$ python3 test_api.py

🔍 Testing: GET /posts
Status Code: 200
❌ Invalid JSON: Expecting value at line 1 column 1
Response text: <html><body>Server Error</body></html>

❌ Test failed
```

### Scenario 3: Rate Limited
```
🔍 Testing: POST /posts (Create new post)
Status Code: 429
⏸️  Rate limited. Waiting 60s...
[After 60 seconds...]
Status Code: 201
✅ Created post with ID: 101
```

---

## 🛡️ **Enhanced Test with Full Error Handling**

Here's what a robust test looks like:

```python
import requests
import time
from typing import Optional, Dict, Any

def safe_api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    timeout: int = 5,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Make API call with comprehensive error handling
    """
    url = f"https://jsonplaceholder.typicode.com{endpoint}"
    
    for attempt in range(max_retries):
        try:
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Check status code
            if response.status_code == 429:
                # Rate limited - retry with backoff
                wait_time = int(response.headers.get('Retry-After', 60))
                print(f"⏸️  Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            elif response.status_code >= 500:
                # Server error - might be temporary
                print(f"❌ Server error: {response.status_code}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
            
            elif response.status_code >= 400:
                # Client error - don't retry
                print(f"❌ Client error: {response.status_code}")
                try:
                    error_msg = response.json().get('error', response.text)
                except:
                    error_msg = response.text[:100]
                print(f"   Details: {error_msg}")
                return None
            
            elif 200 <= response.status_code < 300:
                # Success
                print(f"✅ Status {response.status_code}")
                try:
                    return response.json()
                except ValueError:
                    print(f"❌ Invalid JSON response")
                    print(f"   Response: {response.text[:100]}")
                    return None
            
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print(f"⏱️  Request timed out (>{timeout}s)")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying...")
                time.sleep(2 ** attempt)
                continue
            else:
                return None
        
        except requests.exceptions.ConnectionError as e:
            print(f"🌐 Connection error: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying...")
                time.sleep(2 ** attempt)
                continue
            else:
                return None
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    return None

# Usage example
if __name__ == "__main__":
    result = safe_api_call("GET", "/posts/1")
    if result:
        print(f"Result: {result}")
    else:
        print("Failed to fetch data")
```

---

## 🔍 **Debugging Tips**

### 1. **Enable Request Logging**
```python
import logging
import http.client

http.client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
```

### 2. **Check Response Headers**
```python
response = requests.get(f"{BASE_URL}/posts")
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Content-Type: {response.headers.get('content-type')}")
```

### 3. **Inspect Full Response**
```python
response = requests.get(f"{BASE_URL}/posts")
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text[:500]}")  # First 500 chars
print(f"Response URL: {response.url}")
print(f"Response History: {response.history}")  # Any redirects
```

### 4. **Use HTTPie for Manual Testing**
```bash
# Install: pip install httpie

# GET request
http GET https://jsonplaceholder.typicode.com/posts/1

# POST request
http POST https://jsonplaceholder.typicode.com/posts \
    title="Test" body="Body" userId:=1

# With headers
http GET https://jsonplaceholder.typicode.com/posts \
    Authorization:"Bearer token"
```

---

## ✅ **Testing with Expected Failures**

Use pytest to test error scenarios:

```python
import pytest

class TestAPIErrors:
    
    def test_404_error(self):
        """Test handling of 404 errors"""
        response = requests.get(
            f"{BASE_URL}/posts/99999999"
        )
        # JSONPlaceholder returns 200 with empty object
        assert response.status_code in [200, 404]
    
    def test_malformed_request(self):
        """Test handling of bad requests"""
        response = requests.post(
            f"{BASE_URL}/posts",
            json={"invalid": "data"}  # Missing required fields
        )
        # Most APIs still accept this
        assert response.status_code in [200, 201, 400]
    
    @pytest.mark.timeout(10)
    def test_timeout(self):
        """Test timeout handling"""
        # This endpoint is extremely slow on purpose
        try:
            response = requests.get(
                "https://httpbin.org/delay/20",
                timeout=5
            )
            assert False, "Should have timed out"
        except requests.exceptions.Timeout:
            assert True  # Expected
```

---

## 📋 **Quick Reference: Status Codes**

| Code | Meaning | Retry? | Action |
|------|---------|--------|--------|
| 200 | OK | ✅ | Use response |
| 201 | Created | ✅ | Success (POST) |
| 204 | No Content | ✅ | Success (DELETE) |
| 400 | Bad Request | ❌ | Fix request |
| 401 | Unauthorized | ❌ | Add auth |
| 403 | Forbidden | ❌ | Check permissions |
| 404 | Not Found | ❌ | Check URL |
| 429 | Rate Limited | ✅ | Wait & retry |
| 500 | Server Error | ✅ | Retry with backoff |
| 502 | Bad Gateway | ✅ | Retry with backoff |
| 503 | Service Unavailable | ✅ | Retry with backoff |
| Timeout | Request Too Slow | ✅ | Retry with backoff |

---

## 🎯 **Best Practices**

1. **Always set timeouts**
   ```python
   requests.get(url, timeout=5)
   ```

2. **Catch specific exceptions**
   ```python
   try:
       response = requests.get(url)
   except requests.exceptions.Timeout:
       # Handle timeout
   except requests.exceptions.ConnectionError:
       # Handle connection error
   except Exception as e:
       # Handle unexpected errors
   ```

3. **Use exponential backoff for retries**
   ```python
   wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s...
   ```

4. **Log everything for debugging**
   ```python
   print(f"📊 {method} {url}")
   print(f"   Status: {response.status_code}")
   print(f"   Time: {response.elapsed.total_seconds()}s")
   ```

5. **Validate response structure**
   ```python
   if isinstance(response.json(), list):
       print(f"✅ Got {len(response.json())} items")
   ```

---

For production systems, consider using:
- **Circuit breaker pattern** (fail fast if service is down)
- **Caching** (avoid repeated API calls)
- **Monitoring** (alert on errors)
- **Fallback mechanisms** (return cached/default data)
