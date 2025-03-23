import os
import json
import logging
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import concurrent.futures


from src.utils.logger import setup_logger
from src.extractors import V1Extractor, V2Extractor, V3Extractor

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Extract names from autocomplete API')
    parser.add_argument('--checkpoint-dir', type=str, default='data/checkpoints',
                        help='Directory to store checkpoints')
    parser.add_argument('--results-dir', type=str, default='data/results',
                        help='Directory to store results')
    parser.add_argument('--log-dir', type=str, default='data/logs',
                        help='Directory to store logs')
    parser.add_argument('--versions', type=str, default='v1,v2,v3',
                        help='API versions to extract from (comma-separated)')
    parser.add_argument('--parallel', action='store_true',
                        help='Run extractors in parallel')
    return parser.parse_args()

def run_extractor(extractor_class, checkpoint_dir, results_dir):
    extractor = extractor_class(checkpoint_dir, results_dir)
    extractor.extract_names()

def main():
    args = parse_args()
    logger = setup_logger(args.log_dir)
    
    extractors = {
        'v1': V1Extractor,
        'v2': V2Extractor,
        'v3': V3Extractor
    }
    
    versions = args.versions.split(',')
    
    # Add proper KeyboardInterrupt handling
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(versions)) as executor:
            futures = []
            for version in versions:
                if version in extractors:
                    future = executor.submit(run_extractor, extractors[version], args.checkpoint_dir, args.results_dir)
                    futures.append(future)
            
            concurrent.futures.wait(futures)
    except KeyboardInterrupt:
        logger.info("Extraction stopped by user. Saving progress...")
        # Let the program exit gracefully
        
    # Aggregate results
    total_names = set()
    total_requests = 0
    for version in versions:
        if version in extractors:
            results_path = os.path.join(args.results_dir, f"{version}_names.json")
            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    data = json.load(f)
                    total_names.update(data['names'])
                    total_requests += data['request_count']
    
    logger.info(f"Total unique names across all versions: {len(total_names)}")
    logger.info(f"Total API requests across all versions: {total_requests}")

if __name__ == "__main__":
    main()
