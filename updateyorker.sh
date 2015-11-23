#!/bin/bash

export PYTHONIOENCODING=UTF-8
./code.py newyorker > finalyorker.rss
./code.py nautilus > finalnaut.rss

git commit finalyorker.rss finalnaut.rss -m "auto-update rss feeds"
git push

