#!/bin/bash

export PYTHONIOENCODING=UTF-8
./code.py newyorker http://newyorker.com/rss > finalyorker.rss
git commit finalyorker.rss -m "auto-update finalyorker.rss"
git push

