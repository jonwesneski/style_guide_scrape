import os
import time
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

def download_image(img, partial_url_path, file_extension, dir_name, min_size_b):
    """Download a single image - thread-safe function"""
    src = img.get('src') or img.get('data-src')
    if not (src and partial_url_path in src and file_extension in src):
        return None
    
    src = 'https:' + src if src and src.startswith('//') else src
    filename = src.split('/')[-1].split('?')[0]
    
    try:
        response = requests.get(src, timeout=10)
        response.raise_for_status()
        img_data = response.content
        if len(img_data) > min_size_b:
            filepath = os.path.join(dir_name, filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            return filename
    except Exception as e:
        print(f"Error downloading {src}: {e}")
        return None
    

class RateLimitedDownloader:
    def __init__(self, max_workers=5, rate_limit=10):
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(max_workers)
        self.last_request_time = 0
        self.lock = Lock()
    
    def download_with_rate_limit(self, img, partial_url_path, file_extension, dir_name, min_size_b):
        """Download with rate limiting"""
        acquired = self.semaphore.acquire()
        if not acquired:
            print("Failed to acquire semaphore within timeout!")
            return None
        try:
            with self.lock:
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                min_interval = 1.0 / self.rate_limit
                
                if time_since_last < min_interval:
                    time.sleep(min_interval - time_since_last)
                
                self.last_request_time = time.time()
            return download_image(img, partial_url_path, file_extension, dir_name, min_size_b)
        finally:
            self.semaphore.release()
    
    def download_all(self, img_tags, partial_url_path, file_extension, dir_name, min_size_b):
        """Download all images with rate limiting"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_img = {
                executor.submit(self.download_with_rate_limit, img, partial_url_path, file_extension, dir_name, min_size_b): img 
                for img in img_tags
            }

            for future in as_completed(future_to_img):
                result = future.result()
                if result:
                    print(f"Downloaded: {result}")
