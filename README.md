# Wandering Inn Scraper

This project is a loose collection of Python scripts and Jupyter Notebooks designed to webscrape, store, reformat, and analyze the text of [The Wandering Inn](https://wanderinginn.com/), an excellent web-fiction written by Pirateaba. This was partially a project of curosity, as there are no literary works of comparable scope that I am aware of and I am a deeply invested fan. Additionally, this project has served as a basic excercise in web-scraping, HTML processing, and related Python skills. It also allows me to have my web-fiction safely backed up locally, which pleases the digital preservationist in me. That said, I highly reccommend giving it a read on the author's own website and giving support to their work if you are able!

## Files and Directories

```bash
./raw/        # where the unmodified scraped webpages are cached
./out/        # where the reformatted files and table of contents are stored, can be served as a webpage
./index.json  # where the id, url, date_scraped, and cached file path are stored for each chapter
./table.csv   # where all info about each chapter is stored, such as title, word_count, output file path, date_published, and everything in index.json are stored
```

## Scripts

### Scraper

```bash
./scraper.py
```

This Python script was able to reliably pull the entirety of the webfiction and store the raw webpages in a local directory, over the course of an hour or two, including time delays.

- Reads from the index JSON file to see what the most recently cached chapter is. Starts with the second most recent, in order to avoid saving the Patreon page. If the index file is empty, starts at the first chapter (a hardcoded URL).
- For each page, first checks whether it has already been cached and if so loads it from local storage. Otherwise it sends an html request to wanderinginn.com, with a standard-looking browser request header. In the event of a request failure or timeout, the script will retry a certain number of times before giving up. A random time delay is added before each web request so as not be denied.
- Identifies the link to the next chapter using BeautifulSoup.
- Saves the loaded page's info to cache if it was not already cached, then repeats for the next chapter.
- Exits gracefully if the next page cannot be loaded, or a link to the next chapter cannot be found.

### Formatter

```bash
./formatter.py
```

This Python script exctracts the important content from each raw scraped webpage, then formats it into a minimal HTML template that relies minimally on external resources and styles. Internal formatting such as italics, bold, special colors or size, are all preserved. Finally, a table of contents page is generated with the index number, title, word count, and date published of each chapter. All gathered information is converted to a Pandas dataframe then saved as a CSV for future analysis.

The fields extracted from each raw chapter are:

- The chapter's title
- The date the chapter was published
- The text content of the chapter

Additionally generated are relative path links to the next and previous chapters at the top and bottom of the page. While the program attempts to remove the extraneous next chapter link at the bottom of the page, this does not work consistently, likely due to the fan art sometimes included at the bottom of the page (this is another issue to be remedied, as the scraper does not cache these images). A more dynamic solution is likely required.

While this reformatting mostly works as designed, there are some ~6 chapters where the parsing fails in some part, for some reason. Each of these cases will have to be investigated, and workarounds implemented. In the future, some of the analytics may be added to the index page, or a separate analytics page added and linked from it.

## Notebooks

### Analysis

```bash
./analysis.ipynb
```

This Jupyter Notebook loads the saved CSV and provides some basic analysis based on the word count of each chapter:

- Basic statistics about the per chapter word counts.
- The top ten longest chapters, including their title and publishing date
- A plot of the distribution of chapter word counts, including Gaussian density
- A plot of the cumulative word count over time, as well as the rolling mean and STD of per chapter word count

### Text Analysis

```bash
./text_analysis.ipynb
```

This Jupyter Notebook loads the saved CSV as well as the text (with formatting stripped) of each chapter. Currently in development is a stackplot of character mentions per chapter, with a separate plot for various character groups. The results are perhaps less interesting than anticipated, and due to the proliferation of unique and relevant characters certain arbitrary choices needed to be made.

Future projects may include plugging the text into my [Synthetic Word Generator](https://github.com/Potato-Rocket/Synthetic-Word-Generator), or doing some other sort of word frequency analysis. However, my attention may be better spent on other pursuits.

### Testing

```bash
./old/testing.ipynb
```

This Jupyter Notebook was simply a testbed for the webpage request code, as well as the webpage parsing with BeautifulSoup. All of the functionality within has been duplicated and built upon in the two scripts listed above.
