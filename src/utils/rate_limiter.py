import time
import logging
from typing import Dict
from collections import deque

class RateLimiter:
    """
    Rate limiter to respect API constraints.
    Uses a sliding window approach to track requests.
    """
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.request_timestamps = deque()
        self.logger = logging.getLogger(__name__)
    
    def wait_if_needed(self):
        """
        Wait if necessary to respect the rate limit.
        """
        current_time = time.time()
        
        # Remove timestamps older than the window size
        while self.request_timestamps and self.request_timestamps[0] < current_time - self.window_size:
            self.request_timestamps.popleft()
        
        # If we've reached the limit, wait until we can make another request
        if len(self.request_timestamps) >= self.requests_per_minute:
            wait_time = self.request_timestamps[0] + self.window_size - current_time
            if wait_time > 0:
                self.logger.debug(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
        
        # Add the current request timestamp
        self.request_timestamps.append(time.time())

class VersionedRateLimiter:
    """
    Manages rate limiters for different API versions.
    """
    
    def __init__(self):
        self.limiters = {
            "v1": RateLimiter(100),  # 100 requests per minute
            "v2": RateLimiter(50),   # 50 requests per minute
            "v3": RateLimiter(80)    # 80 requests per minute
        }
    
    def wait_if_needed(self, version: str):
        """
        Wait if necessary to respect the rate limit for a specific API version.
        """
        if version in self.limiters:
            self.limiters[version].wait_if_needed()
        else:
            # Default to the most restrictive rate limit
            self.limiters["v2"].wait_if_needed()
