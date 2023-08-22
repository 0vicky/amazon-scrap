import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape product details from a single product listing page
def scrape_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_list = []

    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    for product in products:
        product_dict = {}

        # Extract product data
        product_name = product.find('span', {'class': 'a-text-normal'}).text.strip()
        product_price = product.find('span', {'class': 'a-offscreen'}).text.strip()

        rating_element = product.find('span', {'class': 'a-icon-alt'})
        if rating_element:
            product_rating = rating_element.text.split()[0]
        else:
            product_rating = 'N/A'

        reviews_element = product.find('span', {'class': 'a-size-base'})
        if reviews_element:
            product_reviews = reviews_element.text.replace(',', '')
        else:
            product_reviews = 'N/A'

        product_url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']

        # Append to product_list
        product_dict['Product Name'] = product_name
        product_dict['Product Price'] = product_price
        product_dict['Rating'] = product_rating
        product_dict['Number of Reviews'] = product_reviews
        product_dict['Product URL'] = product_url

        product_list.append(product_dict)

    return product_list

# Scraping 20 pages of product listing
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
page_limit = 20

all_product_list = []

for page_num in range(1, page_limit + 1):
    page_url = f"{base_url}{page_num}"
    product_list = scrape_product_details(page_url)
    all_product_list.extend(product_list)

# Create a DataFrame from the list of dictionaries
product_df = pd.DataFrame(all_product_list)

# Export the DataFrame to CSV
product_df.to_csv('product_list.csv', index=False)
# Function to scrape additional details from a product page
def scrape_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_details = {}

    description_element = soup.find('div', {'id': 'productDescription'})
    if description_element:
        product_description = description_element.get_text().strip()
    else:
        product_description = 'N/A'

    asin_element = soup.find('th', text='ASIN')
    if asin_element:
        asin = asin_element.find_next('td').get_text().strip()
    else:
        asin = 'N/A'

    manufacturer_element = soup.find('th', text='Manufacturer')
    if manufacturer_element:
        manufacturer = manufacturer_element.find_next('td').get_text().strip()
    else:
        manufacturer = 'N/A'

    # Add the scraped details to the dictionary
    product_details['Description'] = product_description
    product_details['ASIN'] = asin
    product_details['Manufacturer'] = manufacturer

    return product_details

# Update DataFrame with additional details
def update_product_df(df):
    for index, row in df.iterrows():
        product_url = row['Product URL']
        additional_details = scrape_product_page(product_url)

        for key, value in additional_details.items():
            df.at[index, key] = value

    return df

# Update DataFrame with additional details
updated_product_df = update_product_df(product_df)

# Export the updated DataFrame to CSV
updated_product_df.to_csv('product_details.csv', index=False)
