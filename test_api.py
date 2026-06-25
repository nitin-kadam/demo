"""
Simple API test script for JSONPlaceholder
Tests GET, POST, PUT, DELETE operations on the /posts endpoint
Includes comprehensive error handling for various failure scenarios
"""
import requests
import json
import time
from typing import Optional, Dict, Any

BASE_URL = "https://jsonplaceholder.typicode.com"

# === Error Handling Helper ===
def safe_request(method: str, endpoint: str, json_data: Optional[Dict] = None, timeout: int = 5) -> Optional[requests.Response]:
    """
    Make API request with error handling and retry logic
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (e.g., '/posts')
        json_data: JSON data for POST/PUT requests
        timeout: Request timeout in seconds
    
    Returns:
        Response object if successful, None if failed
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"   Making {method} request to {endpoint}...")
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=json_data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, timeout=timeout)
        else:
            print(f"   ❌ Unknown HTTP method: {method}")
            return None
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"   ⏸️  Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return safe_request(method, endpoint, json_data, timeout)
        
        # Handle server errors (5xx) - can retry
        if response.status_code >= 500:
            print(f"   ⚠️  Server error (HTTP {response.status_code})")
            print(f"   Response: {response.text[:100]}")
            return None
        
        # Handle client errors (4xx) - don't retry
        if response.status_code >= 400:
            print(f"   ⚠️  Client error (HTTP {response.status_code})")
            try:
                error_msg = response.json()
                print(f"   Error details: {error_msg}")
            except:
                print(f"   Response: {response.text[:100]}")
            return None
        
        return response
    
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Request timed out (>{timeout}s)")
        return None
    
    except requests.exceptions.ConnectionError as e:
        print(f"   🌐 Connection error: {str(e)[:100]}")
        return None
    
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)[:100]}")
        return None

def test_get_all_posts():
    """Test: GET all posts"""
    print("\n🔍 Testing: GET /posts")
    response = requests.get(f"{BASE_URL}/posts")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"✅ Retrieved {len(data)} posts")
    return data

def test_get_single_post():
    """Test: GET a single post by ID"""
    print("\n🔍 Testing: GET /posts/1")
    response = requests.get(f"{BASE_URL}/posts/1")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['id'] == 1, "Post ID should be 1"
    print(f"✅ Post 1: {data['title'][:50]}...")
    return data

def test_get_post_comments():
    """Test: GET comments for a specific post"""
    print("\n🔍 Testing: GET /posts/1/comments")
    response = requests.get(f"{BASE_URL}/posts/1/comments")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"✅ Retrieved {len(data)} comments for post 1")
    return data

def test_create_post():
    """Test: POST - Create a new post"""
    print("\n➕ Testing: POST /posts (Create new post)")
    new_post = {
        "title": "Test Post from Python",
        "body": "This is a test post created via API",
        "userId": 1
    }
    response = requests.post(f"{BASE_URL}/posts", json=new_post)
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    print(f"✅ Created post with ID: {data['id']}")
    print(f"   Title: {data['title']}")
    return data

def test_update_post():
    """Test: PUT - Update an existing post"""
    print("\n✏️  Testing: PUT /posts/1 (Update post)")
    updated_post = {
        "id": 1,
        "title": "Updated Title",
        "body": "This post has been updated",
        "userId": 1
    }
    response = requests.put(f"{BASE_URL}/posts/1", json=updated_post)
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"✅ Updated post 1")
    print(f"   New title: {data['title']}")
    return data

def test_patch_post():
    """Test: PATCH - Partially update a post"""
    print("\n🔧 Testing: PATCH /posts/1 (Partial update)")
    patch_data = {"title": "Partially Updated Title"}
    response = requests.patch(f"{BASE_URL}/posts/1", json=patch_data)
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"✅ Patched post 1")
    print(f"   New title: {data['title']}")
    return data

def test_delete_post():
    """Test: DELETE - Delete a post"""
    print("\n🗑️  Testing: DELETE /posts/1 (Delete post)")
    response = requests.delete(f"{BASE_URL}/posts/1")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"✅ Deleted post 1")
    return response.status_code

def test_filter_posts_by_user():
    """Test: GET posts filtered by user ID"""
    print("\n🔍 Testing: GET /posts?userId=1 (Filter by user)")
    response = requests.get(f"{BASE_URL}/posts", params={"userId": 1})
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"✅ Retrieved {len(data)} posts for userId=1")
    return data

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 JSONPlaceholder API Test Suite")
    print("=" * 60)
    
    try:
        test_get_all_posts()
        test_get_single_post()
        test_get_post_comments()
        test_filter_posts_by_user()
        test_create_post()
        test_update_post()
        test_patch_post()
        test_delete_post()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_all_tests()
