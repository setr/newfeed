#!/usr/bin/python
import re
import subprocess
import multiprocessing
from readability.readability import Document
import argparse
import urllib

# readability's the content & cleans it up 
def grabContent(link, negs, pos):
    html = urllib.urlopen(link).read()
    content = Document(html, url=link, negative_keywords=negs, positive_keywords=pos).summary()

    # rips out the newsletter portion, because I couldn't get readability neg keywords to do the job
    content = re.sub(r'<section id="newsletter-signup">.*?</section>',
                        "",
                        content,
                        flags=re.S) # sets single-line mode
    # added in by readability, because it assumes its work is the end product
    # rss probably doesn't like it though, so burn it
    content = re.sub(r'<html><body>', "", content)
    content = re.sub(r'</body></html>', "", content)
    return content

#wrappers
def getNautilusContent(link):
    return grabContent(link, None, None)

def getYorkerContent(link):
    extraNegs = "sendlater-container"
    return grabContent(link, extraNegs, None)

def getStuffBetween(tag, text):
    """ finds tag data, and notes the lines they appeared on
         assumes the html was passed through tidy first,
         as that means we can assume its line-delimited"""
    items = []
    item = ""
    keep = False
    linenumbers = [] # [(start, end)]
    start = 0
    for num, line in enumerate(text):
        if "<"+tag+">" in line: 
            keep = True
            start = num
        elif "</"+tag+">" in line:
            item += line
            keep = False
            items.append(item)
            linenumbers.append((start,num))

            item = ""
        if keep:
            item += line

    return items, linenumbers

# does our parsing
def work(item, fixeditems, index):
    # get the link to the full article
    link = re.search("<link>(.*?)</link>", item)
    link = link.group(1)
    link = re.sub(r'&amp;', "&", link)
    # gets the content from that article
    fullcontent = getContent(link)
    newcontent = fullcontent.encode("utf-8")

    #now we plug in the content into the description
    fixeditem = re.sub(r"(<description>.*?<!\[CDATA\[).*?(\]\]>)",
                        "\\1"+ newcontent +"\\2",
                        item,
                        flags=re.S)
    # and get rid of the original content:encoded, because we don't need it
    fixeditem = re.sub("<content:encoded>.*?</content:encoded>", 
                        "", 
                        fixeditem,
                        flags=re.S) # sets single-line mode, 
                            # so . matches EVERY character, including \n
    fixeditems.append((index, fixeditem))

def fixItems(items):
    """Replaces the item's description with the full content 
        of the article it links to; multiprocessed """
    fixeditems = multiprocessing.Manager().list()
    processes = []
    index = 0
    for item in items:
        p = multiprocessing.Process(target=work,
                                    args=(item,
                                       fixeditems,
                                       index))
        index += 1
        processes.append(p)
        item = ""
        p.start()

    for p in processes:
        p.join()
    fixeditems = sorted(fixeditems)
    fixeditems = [item[1] for item in fixeditems]
    return fixeditems

def parseCommandLine(choicelist):
    parser = argparse.ArgumentParser(
            prog="RSS fixer",
            description="takes the given rss feed, and replaces the description with the full content of the article")
    parser.add_argument(
            "domain",
            choices= choicelist,
            action='store',
            help="sets parsing rules for given site")
    return parser.parse_args()

if __name__ == '__main__':
    choices = {'newyorker': (getYorkerContent, 'http://newyorker.com/rss'),
            'nautilus': (getNautilusContent, 'http://nautil.us/rss/all')}

    # get the rss feed
    args = parseCommandLine(choices.keys())
    global getContent
    getContent, url = choices[args.domain]
    data = urllib.urlopen(url).read()
    lines = data.splitlines()

    # find the items
    items, numbers = getStuffBetween("item", lines)

    # fix the items (shove in the full article's content)
    fixeditems = fixItems(items)

    # and now we plug it back in

    #copy from 0 to start
    #add new item
    #copy from start+1 to next start
    #so on
    newlines = []
    lastend = -1
    for index, numberset in enumerate(numbers):
        start, end = numberset
        a = lines[lastend+1:start]
        a.append(fixeditems[index])
        newlines.extend(a)
        lastend=end
    _, finend = numbers[len(numbers)-1]
    newlines.extend(lines[finend+1:]) # grabs all the shit after the final item

    done = "\n\n ".join(newlines)

    done = re.sub(r"<atom:link.*?/>", # gets rid of the newyorker pubsubhubbub shit
                "",
                done)
    print done
