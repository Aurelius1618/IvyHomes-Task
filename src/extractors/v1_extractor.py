from typing import List
from .base_extractor import BaseExtractor

class V1Extractor(BaseExtractor):
    """Extractor for v1 API (alphabets only)."""
    
    def __init__(self, checkpoint_dir: str, results_dir: str):
        super().__init__("v1", checkpoint_dir, results_dir)
    
    def get_character_set(self) -> List[str]:
        """Get the character set for v1 API."""
        return [chr(i) for i in range(ord('a'), ord('z') + 1)]
    
    def get_max_results(self) -> int:
        """Get the maximum number of results returned by v1 API."""
        return 10
