import requests
from bs4 import BeautifulSoup
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_all_category_links(website: str):
    # Send a GET request to the URL
    response = requests.get(website)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        return []

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all divs with class 'category-block grid'
    divs = soup.find_all('div', class_='category-block grid')

    # Initialize an empty list to store the href links
    links = []

    # Loop through each div and find 'a' tags with class 'link'
    for div in divs:
        a_tags = div.find_all('a', class_='link')
        for a in a_tags:
            # Get the href attribute and store it in the links list
            href = a.get('href')
            if href:
                links.append(href)

    # Construct complete URLs
    complete_links = [website + link for link in links]
    return complete_links


def get_article_links(base_url: str, category_url: str):
    # Configure Selenium to use Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a UI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Update this path to where your ChromeDriver is located
    service = Service('/Users/faiz/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Store the extracted hrefs
    hrefs = []

    try:
        driver.get(category_url)

        while True:
            # Wait for the article blocks to load
            WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.CLASS_NAME, 'article-block'))
            )

            # Extract hrefs from article blocks
            article_blocks = driver.find_elements(By.CLASS_NAME, 'article-block')
            for block in article_blocks:
                links = block.find_elements(By.CLASS_NAME, 'link')
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        hrefs.append(href)

            # Try to find the "Next" button and click it
            try:
                next_button = WebDriverWait(driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH, "//button[@title='next']"))
                )
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except Exception as e:
                print("No more pages or error:", e)
                break

    finally:
        driver.quit()

    # Return the list of extracted hrefs
    return hrefs


def get_article_links_for_all_cat_urls(base_url: str, list_of_category_links: list):
    all_article_links = []
    for link in list_of_category_links:
        all_article_links_for_link = get_article_links(base_url, link)
        print(len(all_article_links_for_link))
        all_article_links += all_article_links_for_link  # Combine lists
    return all_article_links  # Moved return outside the loop


def extract_paragraphs_from_article(url: str):
    # Fetch the webpage content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        return []

    web_content = response.content

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(web_content, 'html.parser')

    # Find all content blocks with the class 'content-block'
    content_blocks = soup.find_all('div', class_='content-block')

    paragraphs = []  # List to store extracted paragraphs

    # Check if content_blocks exist
    if content_blocks:
        for content_block in content_blocks:
            # Find all 'div' elements within the content-block that have class 'paragraph-block'
            paragraph_blocks = content_block.find_all('div', class_='paragraph-block')

            # Iterate over paragraph blocks and extract the <p> tags
            for block in paragraph_blocks:
                paragraphs_in_block = block.find_all('p')
                for p in paragraphs_in_block:
                    paragraphs.append(p.text.strip())  # Append the text inside each <p> tag
    else:
        print("No content blocks found.")

    # Create the 'article_data_regie' folder if it doesn't exist
    os.makedirs('article_data_regie', exist_ok=True)

    # Generate a safe filename from the URL
    filename = url.split('/')[-1].replace('-', '_') + '.txt'
    file_path = os.path.join('article_data_regie', filename)  # Updated folder name

    # Write the extracted paragraphs to a text file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(paragraphs))  # Write paragraphs, each on a new line

    print(f"Extracted paragraphs saved to: {file_path}")

    return paragraphs


def get_paragraphs_for_all_article_links(list_of_article_links: list):
    for current_article in list_of_article_links:
        extract_paragraphs_from_article(current_article)


def all_workflow(website_base_url: str):
    cat_links = get_all_category_links(website_base_url)
    article_links = get_article_links_for_all_cat_urls(website_base_url, cat_links)
    get_paragraphs_for_all_article_links(article_links)


# Example usage
if __name__ == "__main__":
    base_url = "https://help.regie.ai"
    all_workflow(base_url)
