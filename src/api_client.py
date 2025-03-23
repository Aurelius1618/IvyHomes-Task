import requests
import time
import logging
import urllib.parse
from typing import Dict, List, Optional, Union

class AutocompleteAPIClient:
    """Client for interacting with the autocomplete API."""
    
    def __init__(self, base_url: str = "http://35.200.185.69:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def get_autocomplete_suggestions(self,
                                   query: str, 
                                   version: str = "v1",
                                   max_retries: int = 3,
                                   retry_delay: int = 60) -> List[str]:
        """
        Get autocomplete suggestions for a query.
        
        Args:
            query: The query string to autocomplete
            version: API version (v1, v2, or v3)
            max_retries: Maximum number of retries on rate limit
            retry_delay: Delay in seconds before retrying after rate limit
            
        Returns:
            List of autocomplete suggestions
        """
        url = f"{self.base_url}/{version}/autocomplete"
        # Properly encode the query parameter
        params = {"query": query}
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    # Handle different response formats
                    if isinstance(data, list):
                        return data  # Direct list of names
                    elif isinstance(data, dict):
                        # Try common fields for results
                        if 'results' in data:
                            return data['results']
                        elif 'suggestions' in data:
                            return data['suggestions']
                        elif 'names' in data:
                            return data['names']
                        else:
                            # If we can't find a specific field, log and return empty
                            self.logger.warning(f"Unknown response format: {data}")
                            return []
                    else:
                        self.logger.warning(f"Unexpected response type: {type(data)}")
                        return []
                
                if response.status_code == 429:  # Rate limit exceeded
                    self.logger.warning(f"Rate limit exceeded for {version}: {response.text}")
                    if attempt < max_retries:
                        # Calculate retry delay based on response headers if available
                        retry_after = response.headers.get('Retry-After')
                        if retry_after and retry_after.isdigit():
                            wait_time = int(retry_after)
                        else:
                            wait_time = retry_delay
                        
                        self.logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        self.logger.error(f"Max retries reached for {query}")
                        return []
                
                self.logger.error(f"Error {response.status_code}: {response.text}")
                return []
                
            except Exception as e:
                self.logger.error(f"Exception during API call: {str(e)}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                return []
        
        return []
