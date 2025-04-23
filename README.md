# Google Maps Data Scraper

A Python utility to scrape location data from Google Maps search results and structure it into a usable format.

## Features

- Automated scraping of Google Maps search results
- Extraction of place details including:
  - Name
  - Address
  - Phone number
  - Website
  - Opening hours
- AI-powered data extraction using OpenRouter API
- Fallback to regex-based extraction when AI fails
- Results saved as structured JSON files

## Requirements

- Python 3.8+
- Playwright 
- OpenAI client library
- OpenRouter API key

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install playwright openai python-dotenv markdownify pydantic
   ```
3. Install Playwright browsers:
   ```
   playwright install
   ```
4. Copy `.env.example` to `.env` and add your OpenRouter API key

## Usage

### Running the scraper

```bash
python main.py
```

### Testing AI extraction separately

To test the AI extraction with existing data without running the scraper:

```bash
python test_extraction.py sample_data.txt
```

## How it works

1. Uses Playwright to automate a browser and navigate to Google Maps
2. Searches for the configured query
3. Scrolls through results to load all places
4. Extracts the HTML content of each listing
5. Attempts to parse the data with AI
6. Falls back to regex extraction if AI fails
7. Saves structured results to a JSON file

## Configuration

Edit the `.env` file to customize:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `MAPS_BASE_URL`: Google Maps URL with region settings
- `MAPS_SEARCH_QUERY`: The search query to perform

## Output

Results are saved to the `results` directory with timestamped filenames.

## Troubleshooting

If you encounter extraction errors:
1. Check the console output for debugging information
2. Make sure your OpenRouter API key is correct
3. Try using the fallback extraction which might work better for certain data patterns# maps-scrapper-2
