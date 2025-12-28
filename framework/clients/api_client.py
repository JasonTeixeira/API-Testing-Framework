"""
API Client - HTTP Request Wrapper
Comprehensive API testing client with authentication, retry logic, and logging
"""

from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger
import time


class APIClient:
    """
    Enterprise-grade API testing client.
    
    Features:
    - Automatic retry with exponential backoff
    - Request/response logging
    - Authentication token management
    - Response time tracking
    - Custom headers support
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        verify_ssl: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            max_retries: Maximum number of retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.token: Optional[str] = None
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"API Client initialized: {base_url}")
    
    def set_token(self, token: str) -> None:
        """
        Set authentication token.
        
        Args:
            token: JWT or Bearer token
        """
        self.token = token
        logger.info("Authentication token set")
    
    def clear_token(self) -> None:
        """Clear authentication token."""
        self.token = None
        logger.info("Authentication token cleared")
    
    def _get_headers(self, custom_headers: Optional[Dict] = None) -> Dict:
        """
        Build request headers.
        
        Args:
            custom_headers: Additional headers
            
        Returns:
            Complete headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Add custom headers
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with logging and error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add headers
        headers = self._get_headers(kwargs.pop('headers', None))
        
        # Log request
        logger.info(f"{method} {url}")
        if 'json' in kwargs:
            logger.debug(f"Request body: {kwargs['json']}")
        
        # Make request with timing
        start_time = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            response_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {response_time:.3f}s"
            )
            
            # Add response time to response object
            response.response_time = response_time
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # ============= HTTP Methods =============
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Custom headers
            
        Returns:
            Response object
        """
        return self._make_request("GET", endpoint, params=params, headers=headers)
    
    def post(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        POST request.
        
        Args:
            endpoint: API endpoint
            json: JSON body
            data: Form data
            headers: Custom headers
            
        Returns:
            Response object
        """
        return self._make_request("POST", endpoint, json=json, data=data, headers=headers)
    
    def put(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        PUT request.
        
        Args:
            endpoint: API endpoint
            json: JSON body
            headers: Custom headers
            
        Returns:
            Response object
        """
        return self._make_request("PUT", endpoint, json=json, headers=headers)
    
    def patch(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        PATCH request.
        
        Args:
            endpoint: API endpoint
            json: JSON body
            headers: Custom headers
            
        Returns:
            Response object
        """
        return self._make_request("PATCH", endpoint, json=json, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Custom headers
            
        Returns:
            Response object
        """
        return self._make_request("DELETE", endpoint, headers=headers)
    
    # ============= Authentication Methods =============
    
    def login(self, username: str, password: str) -> Dict:
        """
        Login and get JWT token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Token response dictionary
            
        Raises:
            Exception: If login fails
        """
        logger.info(f"Logging in as: {username}")
        
        response = self.post(
            "/api/v1/auth/login",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.set_token(token_data["access_token"])
            logger.info("Login successful")
            return token_data
        else:
            logger.error(f"Login failed: {response.status_code}")
            raise Exception(f"Login failed: {response.text}")
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> Dict:
        """
        Register new user.
        
        Args:
            username: Username
            email: Email
            password: Password
            full_name: Full name (optional)
            
        Returns:
            User response dictionary
        """
        logger.info(f"Registering user: {username}")
        
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        
        if full_name:
            payload["full_name"] = full_name
        
        response = self.post("/api/v1/auth/register", json=payload)
        
        if response.status_code == 201:
            logger.info("Registration successful")
            return response.json()
        else:
            logger.error(f"Registration failed: {response.status_code}")
            raise Exception(f"Registration failed: {response.text}")
    
    # ============= Assertion Helpers =============
    
    def assert_status_code(self, response: requests.Response, expected: int) -> None:
        """
        Assert response status code.
        
        Args:
            response: Response object
            expected: Expected status code
            
        Raises:
            AssertionError: If status codes don't match
        """
        actual = response.status_code
        assert actual == expected, (
            f"Expected status {expected}, got {actual}. "
            f"Response: {response.text}"
        )
    
    def assert_response_time(
        self,
        response: requests.Response,
        max_time: float
    ) -> None:
        """
        Assert response time is within limit.
        
        Args:
            response: Response object
            max_time: Maximum allowed time in seconds
            
        Raises:
            AssertionError: If response time exceeds limit
        """
        actual = getattr(response, 'response_time', 0)
        assert actual <= max_time, (
            f"Response time {actual:.3f}s exceeds limit of {max_time}s"
        )
    
    def close(self) -> None:
        """Close session and cleanup resources."""
        self.session.close()
        logger.info("API Client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
