# Wandering Inn Scraper

This project is a loose collection of Python scripts and Jupyter Notebooks designed to webscrape, store, reformat, and analyze the text of [The Wandering Inn](https://wanderinginn.com/), an excellent web-fiction written by Pirateaba. This was partially a project of curosity, as there are no literary works of comparable scope that I am aware of and I am a deeply invested fan. Additionally, this project has served as a basic excercise in web-scraping, HTML processing, and related Python skills. It also allows me to have my web-fiction safely backed up locally, which pleases the digital preservationist in me. That said, I highly reccommend giving it a read on the author's own website and giving support to their work if you are able!

## Scripts

### Scraper

This script was able to reliably pull the entirety of the webfiction and store the raw webpages in a local directory, over the course of an hour or two, including time delays.

- Reads from the index JSON file to see what the most recently cached chapter is. Starts with the second most recent, in order to avoid saving the Patreon page. If the index file is empty, starts at the first chapter (a hardcoded URL).
- For each page, first checks whether it has already been cached and if so loads it from local storage. Otherwise it sends an html request to wanderinginn.com, with a standard-looking browser request header. In the event of a request failure or timeout, the script will retry a certain number of times before giving up. A random time delay is added before each web request so as not be denied.
- Identifies the link to the next chapter using BeautifulSoup.
- Saves the loaded page's info to cache if it was not already cached, then repeats for the next chapter.
- Exits gracefully if the next page cannot be loaded, or a link to the next chapter cannot be found.

### 