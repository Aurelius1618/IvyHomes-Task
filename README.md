#Autocomplete API Name Extractor

This project extracts all possible names from an undocumented autocomplete API running at http://35.200.185.69:8000. The solution is part of an assignment demonstrating a systematic approach to reverse-engineering API behavior, handling rate limiting, and exploring complex search spaces using a depth-first search (DFS) algorithm.
Project Overview
Task: Extract all possible names available through the autocomplete system.

Challenges:

There is no official API documentation.
API rate limits (v1: 100/min, v2: 50/min, v3: 80/min).
Different character sets and maximum result counts:

v1: Lowercase alphabets only, max 10 results per query.
v2: Alphanumeric (digits then letters), max 12 results per query.
v3: Alphanumeric plus special characters (space, +, -, .) in lexicographic order, max 15 results per query.

Approach:

Use DFS to recursively explore the search space by testing prefixes.
Stop expanding a branch when fewer than the maximum results are returned (indicating the full set for that prefix has been reached).
Incorporate checkpointing and logging for progress and debugging.

Note on Proxy Manager: The project contains a proxy_manager.py module, which is an interesting approach to bypass IP-based rate limiting by rotating proxies. Although it is not used by default, it can be activated if you need to distribute your requests across multiple IPs.

Directory Structure
```
IvyHomes Task/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── api_client.py         # Handles API requests, response parsing, and rate limit handling.
│   ├── extractors/  
│   │   ├── __init__.py
│   │   ├── base_extractor.py # The base class implements DFS, checkpointing, and logging.
│   │   ├── v1_extractor.py   # Extractor for v1 (alphabets only)
│   │   ├── v2_extractor.py   # Extractor for v2 (alphanumeric)
│   │   └── v3_extractor.py   # Extractor for v3 (alphanumeric + special characters)
│   ├── utils/    
│   │   ├── __init__.py
│   │   ├── logger.py         # Logging configuration.
│   │   ├── rate_limiter.py   # Rate limiter using a sliding-window approach.
│   │   └── proxy_manager.py  # (Optional) Manages proxy rotation to bypass IP rate limits.
│   └── main.py               # Main entry point; sets up parallel execution of extractors.
├── tests/                    # (Optional) Unit tests for API clients and extractors.
│   └── test_api_client.py
└── data/                     # Contains checkpoints, results, and logs.
    ├── checkpoints/   
    ├── results/    
    └── logs/
  ```  

Installation
Clone the Repository

bash
```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

Set Up the Environment
Make sure you have installed Python 3.8 or later.

Install Dependencies
```
bash
pip install -r requirements.txt
```
(Optional) Configure Proxies

If you wish to experiment with proxy rotation to bypass IP-based rate limits, create a .env file in the root directory and add your proxy list:

text
```
PROXY_LIST=http://user:pass@proxy1.example.com:8080,http://user:pass@proxy2.example.com:8080
```
Usage
Run the extraction script from the project root:

bash
```
python -m src.main --versions v1,v2,v3 --parallel
```
Options:
```
--versions: Comma-separated API versions (default: v1,v2,v3).
--parallel: Run the extractors concurrently using threads.
```
Checkpoints, logs, and final results will be stored in the data/ directory.

Implementation Details

DFS-Based Extraction
The DFS algorithm systematically explores the search space of prefixes.
Each extractor (v1, v2, v3) uses its own character set and defined maximum result count per query.
When a query returns the maximum number of results, the algorithm assumes that more matches might exist under a longer prefix, and the search continues deeper.

Rate Limiting and Checkpointing

Rate Limiter: Implemented in utils/rate_limiter.py using a sliding window to ensure API limits are not exceeded.
Checkpointing: After a set number of requests, the current state (visited prefixes and extracted names) is saved so that the extraction process can be resumed if interrupted.

Proxy Manager (Optional)
The utils/proxy_manager.py module offers a strategy to rotate proxies to bypass IP-based rate limits. Although this module is not used by default, it represents an interesting approach for cases where rate limiting becomes a significant bottleneck.

Logging 
Detailed logging is set up via utils/logger.py to help track progress, debug issues, and save checkpoints.

Findings & Metrics

Total Requests: The project logs include the number of API requests made.
Total Records: The final results include all unique names extracted from the API.
Performance: The logs detail the elapsed time and rate at which names were extracted.

Future Improvements

Enhance error handling and proxy rotation if the API’s rate limitations severely impact performance.
Add unit and integration tests to further ensure reliability.

Conclusion

This project showcases a systematic reverse-engineering approach where we explore an undocumented API, implement an efficient DFS-based extraction strategy, handle rate limiting through careful pacing and checkpointing, and log every step for transparency. The proxy rotation option, while optional here, provides room for scalability and bypassing IP-based rate limits if necessary.

Feel free to reach out or open issues if you have any questions or feedback.
