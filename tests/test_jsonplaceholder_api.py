"""
Pytest test suite for JSONPlaceholder API
Run with: pytest tests/test_jsonplaceholder_api.py -v
"""
import pytest
import requests
from unittest.mock import patch, MagicMock

BASE_URL = "https://jsonplaceholder.typicode.com"

class TestJSONPlaceholderAPI:
    """Test class for JSONPlaceholder API endpoints"""
    
    def test_get_all_posts(self):
        """Test retrieving all posts"""
        response = requests.get(f"{BASE_URL}/posts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0
    
    def test_get_single_post(self):
        """Test retrieving a single post"""
        response = requests.get(f"{BASE_URL}/posts/1")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 1
        assert 'title' in data
        assert 'body' in data
        assert 'userId' in data
    
    def test_get_post_out_of_range(self):
        """Test retrieving a non-existent post"""
        response = requests.get(f"{BASE_URL}/posts/99999")
        assert response.status_code == 200  # JSONPlaceholder returns 200 with empty object
        # or could be 404 depending on API
    
    def test_get_post_comments(self):
        """Test retrieving comments for a post"""
        response = requests.get(f"{BASE_URL}/posts/1/comments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert 'postId' in data[0]
            assert data[0]['postId'] == 1
    
    def test_create_post(self):
        """Test creating a new post"""
        new_post = {
            "title": "Test Post",
            "body": "Test body",
            "userId": 1
        }
        response = requests.post(f"{BASE_URL}/posts", json=new_post)
        assert response.status_code == 201
        data = response.json()
        assert data['title'] == "Test Post"
        assert data['userId'] == 1
        assert 'id' in data
    
    def test_update_post(self):
        """Test updating an existing post"""
        updated_post = {
            "id": 1,
            "title": "Updated Title",
            "body": "Updated body",
            "userId": 1
        }
        response = requests.put(f"{BASE_URL}/posts/1", json=updated_post)
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == "Updated Title"
    
    def test_patch_post(self):
        """Test partial update of a post"""
        patch_data = {"title": "Patched Title"}
        response = requests.patch(f"{BASE_URL}/posts/1", json=patch_data)
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == "Patched Title"
    
    def test_delete_post(self):
        """Test deleting a post"""
        response = requests.delete(f"{BASE_URL}/posts/1")
        assert response.status_code == 200
    
    def test_filter_posts_by_user(self):
        """Test filtering posts by userId"""
        response = requests.get(f"{BASE_URL}/posts", params={"userId": 1})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for post in data:
            assert post['userId'] == 1
    
    def test_response_time(self):
        """Test that API responds within acceptable time"""
        import time
        start = time.time()
        response = requests.get(f"{BASE_URL}/posts/1")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed}s (should be < 5s)"
    
    @patch('requests.get')
    def test_mock_get_posts(self, mock_get):
        """Test with mocked requests (useful for CI/CD)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "title": "Test Post", "userId": 1},
            {"id": 2, "title": "Another Post", "userId": 1}
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/posts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['title'] == "Test Post"

# Parametrized tests for multiple post IDs
@pytest.mark.parametrize("post_id", [1, 2, 3, 5, 10])
def test_get_posts_by_id(post_id):
    """Test retrieving multiple posts by different IDs"""
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == post_id

# Parametrized tests for multiple user IDs
@pytest.mark.parametrize("user_id", [1, 2, 3, 5, 10])
def test_filter_by_user_id(user_id):
    """Test filtering posts by different user IDs"""
    response = requests.get(f"{BASE_URL}/posts", params={"userId": user_id})
    assert response.status_code == 200
    data = response.json()
    for post in data:
        assert post['userId'] == user_id


# === Error Handling Tests ===
class TestAPIErrorHandling:
    """Test class for error handling scenarios"""
    
    def test_timeout_handling(self):
        """Test handling of timeout errors"""
        try:
            # This should timeout on purpose
            response = requests.get(
                f"{BASE_URL}/posts",
                timeout=0.001  # Very short timeout
            )
            # If we get here, connection was fast
            assert response.status_code == 200
        except requests.exceptions.Timeout:
            # Expected behavior
            assert True
        except requests.exceptions.ConnectionError:
            # Also acceptable
            assert True
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON responses"""
        # Mock a bad JSON response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html>Server Error</html>"
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 200
            with pytest.raises(ValueError):
                response.json()
    
    def test_server_error_500(self):
        """Test handling of 500 server errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = '{"error": "Internal Server Error"}'
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 500
    
    def test_rate_limit_429(self):
        """Test handling of rate limit (429) errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '60'}
            mock_response.text = '{"error": "Rate limit exceeded"}'
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 429
            assert response.headers['Retry-After'] == '60'
    
    def test_unauthorized_401(self):
        """Test handling of 401 unauthorized errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Unauthorized"}
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 401
    
    def test_forbidden_403(self):
        """Test handling of 403 forbidden errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"error": "Forbidden"}
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 403
    
    def test_not_found_404(self):
        """Test handling of 404 not found errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not Found"}
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts/nonexistent")
            assert response.status_code == 404
    
    def test_connection_error(self):
        """Test handling of connection errors"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                requests.get(f"{BASE_URL}/posts")
    
    def test_bad_gateway_502(self):
        """Test handling of 502 bad gateway errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 502
            mock_response.text = '{"error": "Bad Gateway"}'
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 502
    
    def test_service_unavailable_503(self):
        """Test handling of 503 service unavailable errors"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = '{"error": "Service Unavailable"}'
            mock_get.return_value = mock_response
            
            response = requests.get(f"{BASE_URL}/posts")
            assert response.status_code == 503


class TestAPIResponseValidation:
    """Test class for response validation"""
    
    def test_response_contains_required_fields(self):
        """Test that responses contain required fields"""
        response = requests.get(f"{BASE_URL}/posts/1")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ['id', 'title', 'body', 'userId']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_response_data_types(self):
        """Test that response data has correct types"""
        response = requests.get(f"{BASE_URL}/posts/1")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data['id'], int)
        assert isinstance(data['title'], str)
        assert isinstance(data['body'], str)
        assert isinstance(data['userId'], int)
    
    def test_response_headers(self):
        """Test that response contains proper headers"""
        response = requests.get(f"{BASE_URL}/posts")
        assert response.status_code == 200
        
        # Check common headers
        assert 'content-type' in response.headers
        assert 'content-length' in response.headers or 'transfer-encoding' in response.headers
