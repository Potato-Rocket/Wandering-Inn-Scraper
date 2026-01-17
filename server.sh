#! /bin/bash

PORT=9000
DIR="/home/oscar/Dropbox/Projects/024 Wandering Inn Scraper/out"

python -m http.server $PORT -d "$DIR"
