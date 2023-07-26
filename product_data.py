import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging

# Set up logging
logging.basicConfig(filename='amazon_product_scraping.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

headers = 'YOUR_USER_AGENT'

# Read the URLs from the CSV file
df = pd.read_csv("output/amazon_data.csv", encoding='utf-8-sig')

# Set the maximum number of URLs to process
max_urls = 200

# Delay between requests in seconds
delay = 5

# Create a list to store the extracted data
product_data_list = []

# Loop through the URLs
for index, row in df.iterrows():
    if index >= max_urls:
        break

    # Get the functional_url from the dataframe
    functional_url = row['Functional URL']

    # Send the request to the URL and fetch the HTML content
    response = requests.get(functional_url, headers=headers)
    response.encoding = "utf-8"
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding="utf-8")

        # Initialize variables to store extracted data
        bullet_points = "None"
        asin_value = "None"
        manufacturer_value = "None"
        product_description = "None"

        # ----------Description-----------------------------------
        # Find the <div> element with id="feature-bullets"
        feature_bullets_div = soup.find(id="feature-bullets")

        # Check if there are bullet points
        if feature_bullets_div:
            # Extract the bullet points
            bullet_points = [span.get_text(strip=True) for span in feature_bullets_div.find_all("span", class_="a-list-item")]


        # ----------ASIN-----------------------------------
        # standard product details
        product_details_div = soup.find(id="detailBullets_feature_div")
        # if product tables is there
        asin_tr = soup.find_all('th', class_='a-color-secondary a-size-base prodDetSectionEntry')

        if product_details_div:
            # Find all <li> elements inside the <div>
            li_elements = product_details_div.find_all('li')

            # Loop through the <li> elements to find the ASIN value
            asin_value = "None"
            for li in li_elements:
                if 'ASIN' in li.get_text():
                    asin_span = li.find('span', class_='a-text-bold')
                    if asin_span:
                        asin_value = asin_span.find_next('span').get_text(strip=True)
                        break

        elif asin_tr:
            for th in asin_tr:
                # Check if 'ASIN' is in the text of the <th> element
                if 'ASIN' in th.get_text():
                    # Find the <td> element within the same <tr> element
                    asin_td = th.find_next_sibling('td', class_='a-size-base prodDetAttrValue')
                    if asin_td:
                        # Extract the ASIN from the <td> element
                        asin_value = asin_td.get_text(strip=True)
                    else:
                        asin_value = "None"
                    break  # Stop the loop since we found the ASIN
            else:
                    asin_value = "None"


        # --------------Manufacturer-------------------------------------
        # Standard Product Details
        product_details_div = soup.find(id="detailBullets_feature_div")
        # if Product Details is present
        manufacturer_tr = soup.find_all('th', class_='a-color-secondary a-size-base prodDetSectionEntry')

        if product_details_div:
            # Find all <li> elements inside the <div>
            li_elements = product_details_div.find_all('li')

            # Loop through the <li> elements to find the ASIN value
            manufacturer_value = "None"
            for li in li_elements:
                if 'Manufacturer' in li.get_text():
                    manufacturer_span = li.find('span', class_='a-text-bold')
                    if manufacturer_span:
                        manufacturer_value = manufacturer_span.find_next('span').get_text(strip=True)
                        break

        elif manufacturer_tr:
            for th in manufacturer_tr:
                # Check if 'Manufacturer' is in the text of the <th> element
                if 'Manufacturer' in th.get_text():
                    # Find the <td> element within the same <tr> element
                    manufacturer_td = th.find_next_sibling('td', class_='a-size-base prodDetAttrValue')
                    if manufacturer_td:
                        # Extract the manufacturer from the <td> element
                        manufacturer_value = manufacturer_td.get_text(strip=True)
                        
                    else:
                        manufacturer_value = "None"
                    break  # Stop the loop since we found the manufacturer
            else:
                manufacturer_value = "None"

        # --------------Product Description-------------------------------------
        product_description_div = soup.find(id="productDescription")
        if product_description_div and product_description_div.get_text(strip=True):
            product_description = product_description_div.get_text(strip=True)

        # Append extracted data to the list
        product_data_list.append({
            'functional_url': functional_url,
            'bullet_points': bullet_points,
            'ASIN': asin_value,
            'Manufacturer': manufacturer_value,
            'Product_Description': product_description
        })

        # Log success message
        logging.info(f"Successfully scraped data from {functional_url}")

    else:
        # Log error message
        logging.error(f"Failed to fetch data from {functional_url}")

    # Introduce delay before the next request
    time.sleep(delay)

# Convert the list of dictionaries to a DataFrame
product_data_df = pd.DataFrame(product_data_list)

# Save the DataFrame to a new CSV file
product_data_df.to_csv("output/amazon_products.csv", index=False, encoding='utf-8-sig')

# Log completion message
logging.info("Scraping completed. Data saved to amazon_products.csv.")


