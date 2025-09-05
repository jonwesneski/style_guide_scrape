from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import time

from rate_limit_downloader import RateLimitedDownloader


def build_parser(driver: webdriver.Chrome, url: str) -> BeautifulSoup:
    '''Buils BeautifulSoup parser'''

    driver.get(url)
    time.sleep(5)  # Wait for JS to load

    # Scroll to bottom to load all products
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extract HTML after rendering
    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')

def get_images(soup: BeautifulSoup, dir_name: str, partial_url_path='shop/files', min_size_kb=100, file_extension='.jpg') -> None:
    '''Find and download product images'''
    
    min_size_b = min_size_kb * 1024
    img_tags = soup.find_all('img')

    downloader = RateLimitedDownloader(max_workers=3, rate_limit=5)
    downloader.download_all(img_tags, partial_url_path, file_extension, dir_name, min_size_b)
    # for img in img_tags:
    #     src = img.get('src') or img.get('data-src')
    #     if src and partial_url_path in src and file_extension in src:
    #     #if src and 'mercury' in src.lower():
    #         src = 'https:' + src if src and src.startswith('//') else src
    #         filename = src.split('/')[-1].split('?')[0]
    #         img_data = requests.get(src).content
    #         if len(img_data) > min_size_b:
    #             with open(os.path.join(dir_name, filename), 'wb') as f:
    #                 f.write(img_data)

def main(url: str, dir_name: str, partial_url_path='shop/files', min_size_kb=100, file_extension='.jpg') -> None:
    # Setup headless browser
    options = Options()
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # Load page and parser
    soup = build_parser(driver, url)
    
    # Create folder to store images
    os.makedirs(dir_name, exist_ok=True)

    get_images(soup, dir_name, partial_url_path, min_size_kb, file_extension)
    
    # Traverse through website
    # a_tags = soup.find_all('a')
    # for a in a_tags:
    #     href = a.get('href')
    #     if href and href.startswith('/'):
    #         url = base_url + href
    #         soup_a = build_parser(driver, url)
    #         get_images(soup_a)

    driver.quit()
    print("✅ Download complete.")

if __name__ == "__main__":
    from ui import get_inputs
    import sys

    inputs = get_inputs()
    try:
        main(inputs.url,
             inputs.output_folder,
             inputs.image_url_sub_path,
             int(inputs.min_image_size_kb), 
             inputs.file_extensions)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
