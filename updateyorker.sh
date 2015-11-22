#!/bin/bash

export PYTHONIOENCODING=UTF-8
curl http://www.newyorker.com/rss > content.txt
./code.py > finalyorker.rss
git commit finalyorker.rss -m "auto-update finalyorker.rss"
git push

