from typing import List
from .base_extractor import BaseExtractor

class V3Extractor(BaseExtractor):
    """Extractor for v3 API (alphanumeric + special characters)."""
    
    def __init__(self, checkpoint_dir: str, results_dir: str):
        super().__init__("v3", checkpoint_dir, results_dir)
    
    def get_character_set(self) -> List[str]:
        """Get the character set for v3 API."""
        # Special characters, then numbers, then lowercase letters
        # Deliberately put space last to avoid issues with space-prefixed queries
        numbers = [str(i) for i in range(10)]
        letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        special_chars = ['+', '-', '.']  # Space moved to end
        return numbers + letters + special_chars + ['']
    
    def get_max_results(self) -> int:
        """Get the maximum number of results returned by v3 API."""
        return 15
