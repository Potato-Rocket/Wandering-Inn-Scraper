import sys
import json
import copy
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from scraper import load_from_file


def format(page, metadata):
    # Set up BeautifulSoup for raw input file
    raw = BeautifulSoup(page, "html.parser")

    # Set up BeautifulSoup for output file
    template_path = Path.cwd() / "template.html"
    with open(template_path, "r") as file:
        out = BeautifulSoup(file.read(), "html.parser")

    print("\nParsing source HTML:")
    info = {}


    # Identify the container for the chapter title
    title_tag = raw.find(class_="elementor-element elementor-element-3d7596e elementor-widget elementor-widget-heading")
    if title_tag is None:
        print("Error: Could not find title container!")
        return None, None

    # Get the tag with the chapter title
    title_tag = title_tag.find("h2")
    if title_tag is None:
        print("Error: Could not find title!")
        return None, None

    # Clean up and print the chapter title
    title = title_tag.string.strip()
    print(f"Title: {title}")
    info["title"] = title

    # Replace title string
    title_tag = out.find(class_="title")
    title_tag.string = title
    title_tag.attrs["id"] = metadata["id"]


    # Identify the containter for the chapter date
    date_tag = raw.find(class_="elementor-element elementor-element-8aba006 elementor-widget elementor-widget-text-editor")
    if date_tag is None:
        print("Error: Could not find date container!")
        return None, None

    # Get the tag with the chapter date
    date_tag = date_tag.find(class_="elementor-widget-container")
    if date_tag is None:
        print("Error: Could not find date tag!")
        return None, None

    # Clean up and pring the publishing date
    date = date_tag.string.strip()
    print(f"Date published: {date}")
    info["date_published"] = date

    # Replace date published string
    date_tag = out.find(class_="date_published")
    date_tag.string = "Date published: " + date


    # Replace date scraped string
    date = metadata["date_scraped"]
    print(f"Date scraped: {date}")
    date_tag = out.find(class_="date_scraped")
    date_tag.string = "Date scraped: " + date


    # Update the next chapter links
    next_tags = out.find_all(class_="next")
    for tag in next_tags:
        id = metadata.get("next")
        if id is not None:
            tag.attrs["href"] = "./" + id + ".html"
        else:
            tag.string = ""

    # Update the previous chapter links
    prev_tags = out.find_all(class_="prev")
    for tag in prev_tags:
        id = metadata.get("prev")
        if id is not None:
            tag.attrs["href"] = "./" + id + ".html"
        else:
            tag.string = ""


    # Get the main chapter content
    chapter_raw = raw.find(class_="twi-article")
    if chapter_raw is None:
        print("Error: Could not chapter content!")
        return None, None

    # Strip the bottom links from the chapter contenthtml.unsecape(
    for i in range(6):
        print(f"Removed extraneous tag {i+1}: {repr(chapter_raw.contents.pop(-1))}")

    # Print the word count of the chapter content
    wc = len(chapter_raw.get_text().split())
    print(f"Content: {wc} words")
    info["word_count"] = wc

    # Replace chapter contents
    chapter_out = out.find(class_="content")
    chapter_out.extend(chapter_raw.contents)

    return out.decode(), info


def format_index(data):
    print("Generating table of contents:")
    # Sets up beautiful soup
    template_path = Path.cwd() / "template_index.html"
    with open(template_path, "r") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    
    # Replace date generated string
    date = datetime.now(timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ")
    print(f"Date generated: {date}")
    date_tag = soup.find(class_="generated")
    date_tag.string = "Date generated: " + date

    # Finds the table and extracts the row template
    table_tag = soup.find(class_="contents")
    row_template = table_tag.find(class_="row").extract()
    print("Table rows:")
    # Add a list item for each chapter
    for i, chapter in enumerate(data):
        row_tag = copy.deepcopy(row_template)

        number_tag = row_tag.find(class_="number")
        number_tag.string = str(i+1)
        
        link = "./" + chapter["id"] + ".html"
        link_tag = row_tag.find(class_="title").find("a")
        link_tag.attrs["href"] = link
        link_tag.string = chapter.get("title", "N/A")

        wc_tag = row_tag.find(class_="word_count")
        wc_tag.string = f"{chapter.get("word_count", 0):,}"

        date_tag = row_tag.find(class_="date")
        date_tag.string = chapter.get("date_published", "N/A")

        print(row_tag)
        table_tag.append(row_tag)
        table_tag.append("\n")
    
    # Save the formatted html file
    path = Path.cwd() / "out/index.html"
    with open(path, "w") as file:
        file.write(soup.decode())


def format_chapters(data):
    # For each chapter entry in the data file
    for i, chapter in enumerate(data):
        page = load_from_file(Path(chapter["raw"]))
        if page is None:
            continue
        
        metadata = {
            "id": chapter["id"],
            "date_scraped": chapter["date_scraped"]
        }
        # Try to get the indices of the previous and next chapters
        try:
            metadata["next"] = data[i+1]["id"]
        except IndexError:
            pass
        if i > 0:
            metadata["prev"] = data[i-1]["id"]

        # Translate the existing chapter into the template
        page, info = format(page, metadata)
        if page is None:
            continue

        chapter.update(info)

        # Save the formatted html file
        path = Path.cwd() / "out" / (chapter["id"] + ".html")
        with open(path, "w") as file:
            file.write(page)
        
        chapter["out"] = path


def main():
    # Open the data file if it exists
    data_path = Path.cwd() / "index.json"
    if data_path.exists():
        with open(data_path, "r") as file:
            data = json.load(file)
    else:
        sys.exit()
    
    format_chapters(data)
    format_index(data)


if __name__ == "__main__":
    main()
