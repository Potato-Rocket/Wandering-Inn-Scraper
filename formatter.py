#! /bin/python3

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

from scraper import load_from_file


def parse(page, metadata):
    # Set up BeautifulSoup for raw input file
    raw = BeautifulSoup(page, "html.parser")

    # Set up BeautifulSoup for output file
    template_path = Path.cwd() / "template.html"
    with open(template_path, "r") as file:
        out = BeautifulSoup(file.read(), "html.parser")

    print("\nParsing source HTML:")


    # Identify the container for the chapter title
    title_tag = raw.find(class_="elementor-element elementor-element-3d7596e elementor-widget elementor-widget-heading")
    if title_tag is None:
        print("Error: Could not find title container!")
        return None

    # Get the tag with the chapter title
    title_tag = title_tag.find("h2")
    if title_tag is None:
        print("Error: Could not find title!")
        return None

    # Clean up and print the chapter title
    title = title_tag.string.strip()
    print(f"Title: {title}")

    # Replace title string
    title_tag = out.find(class_="title")
    title_tag.string = title
    title_tag.attrs["id"] = metadata["id"]


    # Identify the containter for the chapter date
    date_tag = raw.find(class_="elementor-element elementor-element-8aba006 elementor-widget elementor-widget-text-editor")
    if date_tag is None:
        print("Error: Could not find date container!")
        return None

    # Get the tag with the chapter date
    date_tag = date_tag.find(class_="elementor-widget-container")
    if date_tag is None:
        print("Error: Could not find date tag!")
        return None

    # Clean up and pring the publishing date
    date = date_tag.string.strip()
    print(f"Date published: {date}")

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
        return None

    # Strip the bottom links from the chapter contenthtml.unsecape(
    for i in range(6):
        print(f"Removed extraneous tag {i+1}: {repr(chapter_raw.contents.pop(-1))}")

    # Print the word count of the chapter content
    print(f"Content: {len(chapter_raw.get_text().split())} words")

    # Replace chapter contents
    chapter_out = out.find(class_="content")
    chapter_out.extend(chapter_raw.contents)

    return out.decode()


def main():
    # Open the data file if it exists
    data_path = Path.cwd() / "index.json"
    if data_path.exists():
        with open(data_path, "r") as file:
            data = json.load(file)
    else:
        sys.exit()

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
        page = parse(page, metadata)
        if page is None:
            continue

        # Save the formatted html file
        path = Path.cwd() / "out" / (chapter["id"] + ".html")
        with open(path, "w") as file:
            file.write(page)


if __name__ == "__main__":
    main()
