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
    response = requests.get(website)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    divs = soup.find_all('div', class_='category-block grid')

    links = []

    for div in divs:
        a_tags = div.find_all('a', class_='link')
        for a in a_tags:
            href = a.get('href')
            if href:
                links.append(href)

    complete_links = [website + link for link in links]
    return complete_links


def get_article_links(category_url: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service('/Users/faiz/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    hrefs = []

    try:
        driver.get(category_url)

        while True:
            WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.CLASS_NAME, 'article-block'))
            )
            article_blocks = driver.find_elements(By.CLASS_NAME, 'article-block')
            for block in article_blocks:
                links = block.find_elements(By.CLASS_NAME, 'link')
                for link in links:
                    href = link.get_attribute('href')
                    if href:
                        hrefs.append(href)

            try:
                next_button = WebDriverWait(driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH, "//button[@title='next']"))
                )
                next_button.click()
                time.sleep(2)
            except Exception as e:
                print("No more pages or error:", e)
                break

    finally:
        driver.quit()

    return hrefs


def get_article_links_for_all_cat_urls(list_of_category_links: list):
    all_article_links = []
    for link in list_of_category_links:
        all_article_links_for_link = get_article_links(link)
        print(len(all_article_links_for_link))
        all_article_links += all_article_links_for_link
    return all_article_links


def extract_paragraphs_from_article(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {response.status_code}")
        return []

    web_content = response.content

    soup = BeautifulSoup(web_content, 'html.parser')

    content_blocks = soup.find_all('div', class_='content-block')

    paragraphs = []
    if content_blocks:
        for content_block in content_blocks:
            paragraph_blocks = content_block.find_all('div', class_='paragraph-block')
            for block in paragraph_blocks:
                paragraphs_in_block = block.find_all('p')
                for p in paragraphs_in_block:
                    paragraphs.append(p.text.strip())
    else:
        print("No content blocks found.")

    os.makedirs('article_data_regie', exist_ok=True)

    filename = url.split('/')[-1].replace('-', '_') + '.txt'
    file_path = os.path.join('article_data_regie', filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(paragraphs))

    print(f"Extracted paragraphs saved to: {file_path}")

    return paragraphs


def get_paragraphs_for_all_article_links(list_of_article_links: list):
    for current_article in list_of_article_links:
        extract_paragraphs_from_article(current_article)


def all_workflow(website_base_url: str):
    cat_links = get_all_category_links(website_base_url)
    article_links = get_article_links_for_all_cat_urls(cat_links)
    get_paragraphs_for_all_article_links(article_links)

if __name__ == "__main__":
    base_url = "https://help.regie.ai"
    all_workflow(base_url)
