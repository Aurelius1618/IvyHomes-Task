from typing import List
from .base_extractor import BaseExtractor

class V2Extractor(BaseExtractor):
    """Extractor for v2 API (alphanumeric)."""
    
    def __init__(self, checkpoint_dir: str, results_dir: str):
        super().__init__("v2", checkpoint_dir, results_dir)
    
    def get_character_set(self) -> List[str]:
        """Get the character set for v2 API."""
        # Numbers first, then lowercase letters
        return [str(i) for i in range(10)] + [chr(i) for i in range(ord('a'), ord('z') + 1)]
    
    def get_max_results(self) -> int:
        """Get the maximum number of results returned by v2 API."""
        return 12
