# API Error Handling - Quick Reference

## 🎯 What Happens When API Fails - Quick Guide

### 1️⃣ **Timeout Error** ⏱️
```
❌ requests.exceptions.Timeout: HTTPSConnectionPool(host='...') Read timed out
```
**When:** API takes too long to respond (> timeout value)
**What to do:** Set timeout, retry with backoff
```bash
./run_tests.sh  # Will timeout on very slow connections
```

---

### 2️⃣ **Connection Error** 🌐
```
❌ requests.exceptions.ConnectionError: Connection refused
```
**When:** Cannot reach API server (network down, firewall, etc.)
**What to do:** Check network, verify API URL, retry with backoff

---

### 3️⃣ **Invalid JSON** 📄
```
❌ json.decoder.JSONDecodeError: Expecting value at line 1
Response: <html><body>Internal Server Error</body></html>
```
**When:** API returns HTML instead of JSON
**What to do:** Check `content-type` header, wrap in try/except

---

### 4️⃣ **Rate Limiting (429)** 🚫
```
⏸️  Rate limited. Waiting 60 seconds...
Status: 429 Too Many Requests
Retry-After: 60
```
**When:** Too many requests in short time
**What to do:** Wait for `Retry-After` header, then retry

---

### 5️⃣ **Server Error (500)** ❌
```
❌ Status Code: 500
Response: {"error": "Internal Server Error"}
```
**When:** API server crashed or had unexpected error
**What to do:** Retry with exponential backoff (1s, 2s, 4s, 8s...)

---

### 6️⃣ **Not Found (404)** 📍
```
❌ Status Code: 404
Response: {"error": "Not Found"}
```
**When:** Endpoint or resource doesn't exist
**What to do:** Check URL, don't retry

---

### 7️⃣ **Unauthorized (401)** 🔐
```
❌ Status Code: 401
Response: {"error": "Authentication required"}
```
**When:** API key/token missing or invalid
**What to do:** Add auth headers, check credentials

---

### 8️⃣ **Forbidden (403)** 🚫
```
❌ Status Code: 403
Response: {"error": "Access denied"}
```
**When:** Authenticated but no permission
**What to do:** Check permissions, contact admin

---

### 9️⃣ **Bad Gateway (502)** 🔗
```
❌ Status Code: 502
Response: {"error": "Bad Gateway"}
```
**When:** API gateway/proxy had issue
**What to do:** Retry with exponential backoff

---

### 🔟 **Service Unavailable (503)** 🔌
```
❌ Status Code: 503
Response: {"error": "Service Unavailable"}
```
**When:** API server is down for maintenance
**What to do:** Retry with exponential backoff, notify user

---

## 📊 Quick Decision Tree

```
Error Occurred?
│
├─→ 4xx Error?
│   ├─→ 404 Not Found? → ❌ DON'T RETRY (fix URL)
│   ├─→ 401 Unauthorized? → ❌ DON'T RETRY (fix auth)
│   ├─→ 403 Forbidden? → ❌ DON'T RETRY (check permissions)
│   ├─→ 429 Rate Limited? → ✅ RETRY (wait Retry-After)
│   └─→ Other 4xx? → ❌ DON'T RETRY (fix request)
│
├─→ 5xx Error?
│   └─→ ✅ RETRY with exponential backoff (1s, 2s, 4s, 8s)
│
├─→ Timeout?
│   └─→ ✅ RETRY with exponential backoff
│
├─→ Connection Error?
│   └─→ ✅ RETRY with exponential backoff
│
└─→ Invalid JSON?
    └─→ ❌ DON'T RETRY (likely server crash, log it)
```

---

## 🧪 Test Error Handling

```bash
# See all error scenarios
python test_error_scenarios.py

# Run tests that validate error handling
pytest tests/test_jsonplaceholder_api.py::TestAPIErrorHandling -v

# Run tests that validate response structure
pytest tests/test_jsonplaceholder_api.py::TestAPIResponseValidation -v
```

---

## 💻 Code Example: Proper Error Handling

```python
import requests
import time

BASE_URL = "https://jsonplaceholder.typicode.com"

def safe_api_call(endpoint, max_retries=3):
    """Make API call with proper error handling"""
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            # Make request with timeout
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                timeout=5  # Fail after 5 seconds
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                print(f"⏸️  Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Handle server errors (5xx) - retry
            if response.status_code >= 500:
                print(f"⚠️  Server error {response.status_code}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
            
            # Handle client errors (4xx) - don't retry
            if response.status_code >= 400:
                print(f"❌ Client error {response.status_code}")
                return None
            
            # Handle success
            if 200 <= response.status_code < 300:
                print(f"✅ Success! Status {response.status_code}")
                return response.json()
            
        except requests.exceptions.Timeout:
            print("⏱️  Timeout!")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"🔄 Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return None
        
        except requests.exceptions.ConnectionError as e:
            print(f"🌐 Connection error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"🔄 Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return None
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    return None

# Usage
posts = safe_api_call("/posts")
if posts:
    print(f"Retrieved {len(posts)} posts")
else:
    print("Failed to retrieve posts")
```

---

## ✅ Best Practices

1. **Always set timeout**
   ```python
   requests.get(url, timeout=5)
   ```

2. **Handle different error types**
   ```python
   try:
       response = requests.get(url)
   except requests.exceptions.Timeout:
       # Handle timeout
   except requests.exceptions.ConnectionError:
       # Handle connection error
   except Exception as e:
       # Handle unexpected
   ```

3. **Use exponential backoff**
   ```python
   wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s...
   ```

4. **Don't retry 4xx errors (except 429)**
   ```python
   if 400 <= status < 500 and status != 429:
       don't_retry()
   ```

5. **Validate response structure**
   ```python
   if response.status_code == 200:
       data = response.json()
       assert 'expected_field' in data
   ```

---

## 📚 Full Documentation

See `API_ERROR_HANDLING.md` for comprehensive guide with:
- Detailed error descriptions
- Full code examples
- Debugging tips
- HTTP status code reference table
- Mocking strategies for testing
