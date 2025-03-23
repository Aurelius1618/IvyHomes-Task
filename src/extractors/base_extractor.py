import os
import json
import logging
import time
from typing import List, Set, Dict, Optional
from abc import ABC, abstractmethod

from src.api_client import AutocompleteAPIClient
from src.utils.rate_limiter import VersionedRateLimiter

class BaseExtractor(ABC):
    """Base class for name extractors."""
    
    def __init__(self, 
                 version: str,
                 checkpoint_dir: str,
                 results_dir: str):
        self.version = version
        self.api_client = AutocompleteAPIClient()
        self.rate_limiter = VersionedRateLimiter()
        self.checkpoint_dir = checkpoint_dir
        self.results_dir = results_dir
        self.logger = logging.getLogger(__name__)
        
        # Create directories if they don't exist
        os.makedirs(checkpoint_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize state
        self.names: Set[str] = set()
        self.visited_prefixes: Set[str] = set()
        self.request_count: int = 0
        
        # Load checkpoint if exists
        self._load_checkpoint()
    
    def _get_checkpoint_path(self) -> str:
        """Get the path to the checkpoint file."""
        return os.path.join(self.checkpoint_dir, f"{self.version}_checkpoint.json")
    
    def _get_results_path(self) -> str:
        """Get the path to the results file."""
        return os.path.join(self.results_dir, f"{self.version}_names.json")
    
    def _load_checkpoint(self):
        """Load state from checkpoint if it exists."""
        checkpoint_path = self._get_checkpoint_path()
        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, 'r') as f:
                    checkpoint = json.load(f)
                    self.names = set(checkpoint.get('names', []))
                    self.visited_prefixes = set(checkpoint.get('visited_prefixes', []))
                    self.request_count = checkpoint.get('request_count', 0)
                    self.logger.info(f"Loaded checkpoint for {self.version}: {len(self.names)} names, {len(self.visited_prefixes)} visited prefixes")
            except Exception as e:
                self.logger.error(f"Failed to load checkpoint: {str(e)}")
    
    def _save_checkpoint(self):
        """Save current state to checkpoint."""
        checkpoint_path = self._get_checkpoint_path()
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump({
                    'names': list(self.names),
                    'visited_prefixes': list(self.visited_prefixes),
                    'request_count': self.request_count
                }, f)
            self.logger.debug(f"Saved checkpoint for {self.version}")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def _save_results(self):
        """Save extracted names to results file."""
        results_path = self._get_results_path()
        try:
            with open(results_path, 'w') as f:
                json.dump({
                    'version': self.version,
                    'names': list(self.names),
                    'request_count': self.request_count,
                    'total_names': len(self.names)
                }, f, indent=2)
            self.logger.info(f"Saved {len(self.names)} names for {self.version}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def get_suggestions(self, query: str) -> List[str]:
        """
        Get autocomplete suggestions for a query with rate limiting.

       Args:
            query: The query string

        Returns:
            List of autocomplete suggestions
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed(self.version)

        # Make the API request
        response = self.api_client.get_autocomplete_suggestions(query, self.version)

        # Debug logging
        self.logger.debug(f"Query: {query}, Got {len(response)} suggestions")
        if response and len(response) > 0:
            self.logger.debug(f"Sample results: {response[:3]}")

        # Update state
        self.request_count += 1
        self.visited_prefixes.add(query)
        self.names.update(response)

        # Save checkpoint periodically
        if self.request_count % 20 == 0:  # Increased frequency for debugging
           self._save_checkpoint()
           self.logger.info(f"{self.version}: {self.request_count} requests, {len(self.names)} names found")

        return response

    
    @abstractmethod
    def get_character_set(self) -> List[str]:
        """Get the character set for this API version."""
        pass
    
    @abstractmethod
    def get_max_results(self) -> int:
        """Get the maximum number of results returned by this API version."""
        pass
    
    def extract_names(self):
        """Extract all names using DFS approach."""
        self.logger.info(f"Starting extraction for {self.version}")
        start_time = time.time()
        
        # Start DFS with each character in the character set
        for char in self.get_character_set():
            if char not in self.visited_prefixes:
                self._dfs(char)
        
        # Save final results
        self._save_checkpoint()
        self._save_results()
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Completed extraction for {self.version}")
        self.logger.info(f"Total requests: {self.request_count}")
        self.logger.info(f"Total names: {len(self.names)}")
        self.logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    
    def _dfs(self, prefix: str):
        """
        Perform depth-first search starting with the given prefix.

        Args:
            prefix: The current prefix to explore
        """
        if prefix in self.visited_prefixes:
            return
        
        self.visited_prefixes.add(prefix)

        # Skip consecutive spaces - they cause traversal problems
        if '  ' in prefix:
            return
        
        # Skip if prefix has leading/trailing spaces (except single space prefix)
        if (prefix.startswith(' ') or prefix.endswith(' ')) and len(prefix) > 1:
            return
        
        #
        suggestions = self.get_suggestions(prefix)


        # If we got the maximum number of results, there might be more names with this prefix
        if len(suggestions) >= self.get_max_results():
            # Explore deeper by appending each character
            for char in self.get_character_set():
                next_prefix = prefix + char
                # Skip if the resulting prefix is too long or problematic
                if len(next_prefix) <= 10:
                    self._dfs(next_prefix)
        else:
            # If we got fewer than max results, we've found all names with this prefix
            # No need to explore deeper from this prefix
            self.logger.debug(f"Prefix '{prefix}' returned {len(suggestions)} results (< max). Not exploring deeper.")

