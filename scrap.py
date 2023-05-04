import os
import time

import urllib.request

from selenium import webdriver

import signal
from selenium.webdriver.common.by import By
from glob import glob

number_of_images = 10
GET_IMAGE_TIMEOUT = 2
SLEEP_BETWEEN_INTERACTIONS = 0.1
SLEEP_BEFORE_MORE = 5
IMAGE_QUALITY = 85

search_terms = [
    'dog',
    'cat',
]


wd = webdriver.Chrome()

class timeout:
    def __init__(self, seconds=1, error_message="Timeout"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def image_urls_to_file(filename,x):
    with open(filename, 'w') as f:
        for row in x:
            f.write(str(row) + '\n')
def image_urls_from_file(filename):
    with open(filename, 'r') as f:
        s = [line.strip() for line in f]
    return set(s)
def fetch_image_urls(
    filename:str,
    query: str,
    max_links_to_fetch: int,
    wd: webdriver,
    sleep_between_interactions: int = 1,
):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    wd.get(search_url.format(q=query))

    image_urls_main = image_urls_from_file(filename)
    image_urls=image_urls_from_file(filename)    
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        thumbnail_results = wd.find_elements(By.CSS_SELECTOR,"img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(
            f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}"
        )

        for img in thumbnail_results[results_start:number_results]:
            if(len(image_urls)-len(image_urls_main)>=max_links_to_fetch):
                break
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            actual_images = wd.find_elements(By.CSS_SELECTOR,"img.Q4LuWd")
            for actual_image in actual_images:
                if actual_image.get_attribute(
                    "src"
                ) and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))
            image_count = len(image_urls)-len(image_urls_main)

        if len(image_urls)-len(image_urls_main) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)-len(image_urls_main)} image links, done!")
            break
        else:
            print("Found:", len(image_urls)-len(image_urls_main), "image links, looking for more ...")
            time.sleep(SLEEP_BEFORE_MORE)

            not_what_you_want_button = ""
            try:
                not_what_you_want_button = wd.find_element(By.CSS_SELECTOR,".r0zKGf")
            except:
                pass

            if not_what_you_want_button:
                print("No more images available.")
                return image_urls

            load_more_button = wd.find_element(By.CSS_SELECTOR,".mye4qd")
            if load_more_button and not not_what_you_want_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        results_start = len(thumbnail_results)
    return image_urls


def persist_image(folder_path: str,search_term, url: str,index):
    try:
        print("Getting image")
        image_content = urllib.request.urlopen(url)

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        file_path = os.path.join(
            folder_path, search_term+str(index)+ ".jpg"
        )
        with open(file_path, "wb") as f:
            f.write(image_content.read())
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term: str, number_images=5):
    target_folder = "catsdogs"
    file=search_term+'.txt'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome() as wd:
        res = fetch_image_urls(
            filename=file,
            query=search_term,
            max_links_to_fetch=number_images,
            wd=wd,
            sleep_between_interactions=SLEEP_BETWEEN_INTERACTIONS,
        )
        
        if res is not None:
            start_number=len(image_urls_from_file(file))
            index=start_number+1
            image_urls_to_file(file,res)
            for elem in res:
                persist_image(target_folder+'/',search_term, elem,index)
                index+=1
        else:
            print(f"Failed to return links for term: {search_term}")

for search_term in search_terms:
    search_and_download(search_term,number_of_images)