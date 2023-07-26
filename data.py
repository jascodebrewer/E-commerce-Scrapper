from itertools import zip_longest
import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib.parse
import csv
import logging

# Configure logging
logging.basicConfig(filename='scraping_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lists to store data
titles_list = []
ratings_list = []
reviews_list = []
prices_list = []
functional_url_list = []

# Process multiple HTML files
for page_number in range(1, 21):  # Replace 21 with the total number of HTML files (amazon1.html to amazon20.html)
    file_name = f"data/amazon{page_number}.html"
    try:
        # Read the HTML file
        with open(file_name, "r") as f:
            html_doc = f.read()

        soup = BeautifulSoup(html_doc, 'html.parser', from_encoding='utf-8')
        # Find all elements that contain both the title and the rating
        items = soup.find_all('div', class_='a-section a-spacing-small a-spacing-top-small')

        # Loop through the items and extract the titles, ratings, reviews, and URLs
        for item in items:
            title = item.find('span', class_=["a-size-medium a-color-base a-text-normal", "a-size-base-plus a-color-base a-text-normal"])
            rating = item.find(class_='a-popover-trigger a-declarative')
            review = item.find(class_='a-size-base s-underline-text')
            url = item.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')

            if title:
                titles_list.append(title.get_text().strip())
            else:
                titles_list.append(None)

            if rating:
                ratings_list.append(rating.get_text().strip())
            else:
                ratings_list.append(None)

            if review:
                reviews_list.append(review.get_text().strip())
            else:
                reviews_list.append(None)

            if url:
                href_value = url.get('href')
                if href_value:
                    if 'url=' in href_value:
                        parsed_url = urllib.parse.parse_qs(urllib.parse.urlsplit(href_value).query)
                        url_parameter = parsed_url.get('url', [''])[0]
                        functional_url = "https://www.amazon.in" + url_parameter
                    elif href_value.startswith('https://'):
                        functional_url = href_value
                    else:
                        functional_url = "https://www.amazon.in" + href_value
                else:
                    functional_url = None
            else:
                functional_url = None

            functional_url_list.append(functional_url)

            # Find the corresponding price element for the current product
            price_element = item.find('span', class_='a-price-whole')
            if price_element:
                price_text = price_element.get_text().strip()
                if "_bGlmZ_price_23Ix_" not in price_element.get("class", ""):
                    prices_list.append(price_text)
                else:
                    prices_list.append(None)
            else:
                prices_list.append(None)

    except FileNotFoundError:
        logging.warning(f"File {file_name} not found. Skipping.")
    except Exception as e:
        logging.error(f"Error occurred while processing file {file_name}. {e}")

logging.info(f"titles_list: {len(titles_list)}")
logging.info(f"ratings_list: {len(ratings_list)}")
logging.info(f"reviews_list: {len(reviews_list)}")
logging.info(f"prices_list: {len(prices_list)}")
logging.info(f"functional_url_list: {len(functional_url_list)}")

# Create a dictionary with the combined data
data_dict = {
    "Title": titles_list,
    "Rating": ratings_list,
    "Price": prices_list,
    "Review": reviews_list,
    "Functional URL": functional_url_list
}

# Convert the dictionary to a pandas DataFrame
df = pd.DataFrame(data_dict)

# Remove rows where all values are None
df.dropna(how='all', inplace=True)

# Write the DataFrame to a single CSV file
try:
    df.to_csv("output/amazon_data.csv", index=False, encoding='utf-8-sig')
    logging.info("Data written to CSV successfully.")
except Exception as e:
    logging.error("Error writing to CSV:", e)

logging.info("Scraping and writing to CSV completed.")