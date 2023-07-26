import requests
import time
import logging

# Configure logging
logging.basicConfig(filename='scraping_html.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetchAndSaveToFile(url, path, headers):
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Raise an exception if the request was not successful (status code >= 400)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(r.text)

        logging.info(f"Successfully fetched and saved {url} to {path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Failed to fetch {url}. {e}")

# Define the base URL and the number of pages you want to scrape
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
num_pages = 20

# Headers for your request (include any necessary headers like User-Agent)
headers = 'YOUR_USER_AGENT'

# Loop through each page and scrape
for page_number in range(1, num_pages + 1):
    url = base_url + str(page_number)
    file_path = f"data/amazon{page_number}.html"

    fetchAndSaveToFile(url, file_path, headers)
    time.sleep(30)  # Add a delay of 5 seconds between each request (adjust the delay as needed)

logging.info("Scraping completed.")
