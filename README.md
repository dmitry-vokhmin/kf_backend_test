# Outage Data Processor

## Features
- Fetch outage data from a configurable API endpoint.
- Filter outages based on predefined criteria.
- Save the filtered outage data back to an API endpoint.
- Retry mechanism for robust API interactions.

## Installation

### Prerequisites
- Python 3.11

### Libraries
This script uses external libraries. To install these libraries, run:
```
pip install -r requirements.txt
```

## Configuration
Before running the script, create `.env` file at the root of the project and configure the following environment variables:
- `BASE_URL`: The base URL of the API endpoint.
- `API_KEY`: The API key for authentication.

Example `.env` file:
```
BASE_URL=https://api.example.com
API_KEY=your_api_key_here
```

## Usage
To run the script, simply execute it with Python from the command line:
```
python main.py
```

## How It Works
1. **Session Initialization**: Initializes a `requests.Session` with a retry strategy for resilient API calls.
2. **Data Fetching**: Fetches outage data and site information from configured API endpoints.
3. **Data Filtering**: Filters the fetched outage data based on predefined criteria and the site information.
4. **Data Saving**: Saves the filtered outages back to a specified API endpoint.

## Testing

This project includes tests to ensure the functionality works as expected.  You can run the tests by executing the following command in the terminal from the root of the project:
```
python -m pytest tests/
```

## Logging
The script uses Python's built-in `logging` module to log its operation. Errors and information messages will be logged accordingly, aiding in troubleshooting and monitoring.
