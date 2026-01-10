#! /bin/python3

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import random
import time
import json
import datetime
from yaspin import yaspin


START = "https://wanderinginn.com/2017/03/03/rw1-00/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate"
}
DELAY_RANGE = [5, 15]
PAGE_LIMIT = 3


def load_from_web(url):
    # Implement random delay to avoid being blocked
    with yaspin() as sp:
        delay = random.randint(1, 3)
        for i in range(delay, 0, -1):
            sp.text = f"Applying {i}s random delay..."
            time.sleep(1)
        sp.stop()
        print(f"Applied {delay}s random delay")

    # Make request to the webpage
    start = time.time()
    with yaspin(text=f"Making request to {url}") as sp:
        try:
            response = requests.get(url, headers=HEADERS)
            sp.stop()
            print(sp.text)
        except Exception as e:
            sp.stop()
            print(sp.text)
            print(f"Request failed with exception: {e}")
            return None

    # Check that the request was successful
    if response.status_code != 200:
        print(f"Request failed with code: {response.status_code}")
        return None

    delay = time.time() - start
    print(f"{int(len(response.content) / 1024)}kb recieved")
    print(f"Request successfully completed in {delay:.3f}s with code: {response.status_code}")

    return response.content


def load_from_file(fname):
    # Check whether the file already exists
    if not fname.exists():
        print(f"File {fname} does not exist in local cache!")
        return None
    
    # Open and read the file
    with open(fname, "r") as file:
        text = file.read()

    print(f"Successfully loaded {int(len(text) / 1024)}kb file {fname}")

    return text


def fetch_chapter(url, force=False):
    # Generate an file path based on the web url
    id = url.strip("/").split("/")[-1]
    path = Path.cwd() / "raw" / (id + ".html")

    # Fail gracefully, and in the order determined by the forcing parameter
    if not force:
        page = load_from_file(path)
        save = False
    if force or page is None:
        page = load_from_web(url)
        save = True
    if page is None and force:
        page = load_from_file(path)
        save = False

    # Save the page to the cache if it was loaded from the web
    if page is not None: #and save:
        with open(path, "w") as file:
            file.write(BeautifulSoup(page, "html.parser").prettify())
        print(f"Saved page to \"{path}\"")

        # Update the index data upon scraping and saving a page
        data_path = Path.cwd() / "index.json"
        if data_path.exists():
            with open(data_path, "r") as file:
                data = json.load(file)
        else:
            data = []

        # Format the current date and time as the
        date_scraped = datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ")
        # Create the data entry for the page
        info = {
            "id": id,
            "url": url,
            "raw": str(path),
            "date_scraped": date_scraped
        }

        # Update the page's entry if it already exists
        existing = False
        for i, chapter in enumerate(data):
            if chapter["id"] == id:
                data[i] = info
                existing = True
                break
        # Otherwise, append a new entry
        if not existing:
            data.append(info)
        
        # Write the updated data file
        with open(data_path, "w") as file:
            json.dump(data, file, indent=2)
        
        print(f"Updated \"{data_path}\" with page info")
    
    return page


def parse_next(page):
    # Extracts the link to the next chapter from the file
    soup = BeautifulSoup(page, "html.parser")
    next = soup.find(rel="next")
    if next is None:
        print("No link to next chapter found")
        sys.exit()
    return next.get("href")


def main():
    # Set the starting chapter url
    current_url = START
    # Repeat within a set page limit
    for _ in range(3):
        # Fetch the current chapter
        page = fetch_chapter(current_url)
        # If failed, the program cannot continue
        if page is None:
            print("Failed to source page from either web or local cache")
            sys.exit()
        
        # Find the link to the next page
        next = parse_next(page)
        # If link cannot be found, abort. Otherwise, update the current url
        if next is None:
            print("Link to next chapter invalid")
            sys.exit()
        else:
            print(f"Link to next chapter found: {next}")
            current_url = next


if __name__ == "__main__":
    main()
