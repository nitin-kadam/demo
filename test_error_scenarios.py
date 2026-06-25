"""
Error Scenario Tester - Simulate various API failure scenarios
Shows what happens when APIs fail and how to handle them
"""
import requests
from unittest.mock import patch, MagicMock
import time

BASE_URL = "https://jsonplaceholder.typicode.com"

def simulate_timeout():
    """Simulate timeout error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 1: API Timeout")
    print("="*60)
    print("📝 What happens: Request takes too long (> timeout)")
    print("   Error: requests.exceptions.Timeout")
    print("\n🔧 Testing...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/posts",
            timeout=0.001  # Extremely short timeout to trigger error
        )
        print(f"Status: {response.status_code}")
    except requests.exceptions.Timeout:
        print("✅ Caught Timeout error!")
        print("💡 Solution: Set reasonable timeout (5-30s) and retry with backoff")
    except requests.exceptions.ConnectionError:
        print("✅ Got ConnectionError (also timeout-related)")

def simulate_connection_error():
    """Simulate connection error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 2: Connection Error")
    print("="*60)
    print("📝 What happens: Cannot reach API server")
    print("   Error: requests.exceptions.ConnectionError")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Connection refused - server unreachable"
        )
        
        try:
            response = requests.get(f"{BASE_URL}/posts")
        except requests.exceptions.ConnectionError as e:
            print(f"✅ Caught error: {e}")
            print("💡 Solution: Check network, verify API URL, retry with backoff")

def simulate_invalid_json():
    """Simulate invalid JSON response"""
    print("\n" + "="*60)
    print("❌ SCENARIO 3: Invalid JSON Response")
    print("="*60)
    print("📝 What happens: API returns non-JSON (HTML error page)")
    print("   Error: json.decoder.JSONDecodeError")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Internal Server Error</body></html>"
        mock_response.json.side_effect = ValueError("Expecting value")
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        print(f"Status Code: {response.status_code}")
        print(f"Response Type: HTML (not JSON)")
        print(f"Response Text: {response.text[:50]}...")
        
        try:
            data = response.json()
        except ValueError as e:
            print(f"✅ Caught error: {e}")
            print("💡 Solution: Check response.headers['content-type']")
            print("           or wrap response.json() in try/except")

def simulate_rate_limiting():
    """Simulate rate limit (429) error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 4: Rate Limiting (429)")
    print("="*60)
    print("📝 What happens: Too many requests, API throttles you")
    print("   Status Code: 429 Too Many Requests")
    print("   Header: Retry-After: 60")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.json()['error']}")
        print(f"Retry After: {response.headers['Retry-After']} seconds")
        print("✅ Error detected")
        print("💡 Solution: Sleep for Retry-After seconds, then retry")

def simulate_server_error_500():
    """Simulate 500 server error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 5: Server Error (500)")
    print("="*60)
    print("📝 What happens: API server crashed or had unexpected error")
    print("   Status Code: 500 Internal Server Error")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_response.text = '{"error": "Internal Server Error"}'
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.json()['error']}")
        print("✅ Error detected")
        print("💡 Solution: Retry with exponential backoff (1s, 2s, 4s, 8s...)")

def simulate_not_found_404():
    """Simulate 404 not found error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 6: Not Found (404)")
    print("="*60)
    print("📝 What happens: Endpoint or resource doesn't exist")
    print("   Status Code: 404 Not Found")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not Found"}
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts/invalid")
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.json()['error']}")
        print("✅ Error detected")
        print("💡 Solution: Check URL, validate endpoint exists")
        print("           Don't retry 404 errors")

def simulate_unauthorized_401():
    """Simulate 401 unauthorized error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 7: Unauthorized (401)")
    print("="*60)
    print("📝 What happens: Authentication required/failed")
    print("   Status Code: 401 Unauthorized")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Authentication required"}
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.json()['error']}")
        print("✅ Error detected")
        print("💡 Solution: Add API key or Bearer token to headers")
        print("           Check authentication credentials")

def simulate_forbidden_403():
    """Simulate 403 forbidden error"""
    print("\n" + "="*60)
    print("❌ SCENARIO 8: Forbidden (403)")
    print("="*60)
    print("📝 What happens: Authenticated but no permission")
    print("   Status Code: 403 Forbidden")
    print("\n🔧 Testing (mocked)...")
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "Access denied"}
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.json()['error']}")
        print("✅ Error detected")
        print("💡 Solution: Check user permissions")
        print("           Verify you have access to resource")

def print_error_handling_summary():
    """Print summary of error handling strategies"""
    print("\n" + "="*60)
    print("📊 Error Handling Strategy Summary")
    print("="*60)
    
    strategies = {
        "Timeout": {
            "Retry": True,
            "Action": "Set timeout, retry with backoff",
            "Example": "timeout=5, backoff=[1s, 2s, 4s]"
        },
        "Connection Error": {
            "Retry": True,
            "Action": "Check network, retry with backoff",
            "Example": "Exponential backoff up to 3 times"
        },
        "Invalid JSON (200)": {
            "Retry": False,
            "Action": "Check content-type, log response",
            "Example": "Likely server issue, log for debugging"
        },
        "Rate Limit (429)": {
            "Retry": True,
            "Action": "Wait Retry-After seconds, then retry",
            "Example": "time.sleep(int(retry_after))"
        },
        "Server Error (5xx)": {
            "Retry": True,
            "Action": "Retry with exponential backoff",
            "Example": "Backoff: 1s, 2s, 4s, 8s (max 3-5 times)"
        },
        "Not Found (404)": {
            "Retry": False,
            "Action": "Check URL, fix request",
            "Example": "Don't waste resources retrying"
        },
        "Unauthorized (401)": {
            "Retry": False,
            "Action": "Fix credentials, add auth headers",
            "Example": "Add Authorization header"
        },
        "Forbidden (403)": {
            "Retry": False,
            "Action": "Check permissions, verify access",
            "Example": "Contact admin for access"
        },
    }
    
    for error, details in strategies.items():
        retry_icon = "✅ YES" if details['Retry'] else "❌ NO"
        print(f"\n{error}:")
        print(f"  Retry: {retry_icon}")
        print(f"  Action: {details['Action']}")
        print(f"  Example: {details['Example']}")

def main():
    """Run all error simulations"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  API Error Handling Scenarios - What Happens & Solutions".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run all scenarios
    simulate_timeout()
    simulate_connection_error()
    simulate_invalid_json()
    simulate_rate_limiting()
    simulate_server_error_500()
    simulate_not_found_404()
    simulate_unauthorized_401()
    simulate_forbidden_403()
    
    # Print summary
    print_error_handling_summary()
    
    print("\n" + "="*60)
    print("✅ All error scenarios demonstrated!")
    print("="*60)
    print("\n📖 For more details, see: API_ERROR_HANDLING.md\n")

if __name__ == "__main__":
    main()
