#!/usr/bin/python
import re
import subprocess

def getFullContent(link):
    curl = "curl -L " + link
    # note: tidy -xml can be used to format the final output
    tidy = "tidy --force-output yes --vertical-space no -utf8 -w 100000 2>/dev/null"
    grep = "grep word_count"
    try:
        output = subprocess.check_output(curl + " | " + tidy + " | " + grep, shell=True)
    except subprocess.CalledProcessError as e:
        output = str(e.output)
    return output

def getStuffBetween(tag, text):
    items = []
    item = ""
    keep = False
    linenumbers = [] # [(start, end)]
    start = 0
    for num, line in enumerate(text):
        if "<"+tag+">" in line:  # if we open, start keeping the lines
            keep = True
            start = num
        elif "</"+tag+">" in line:  # if we close, we be done
            item += line
            keep = False
            items.append(item)
            linenumbers.append((start,num))
            item = ""

        if keep:
            item += line

    return items, linenumbers


data = ""
with open('content2.txt', 'r') as text:
    data = text.read()

lines = data.splitlines()

items, numbers = getStuffBetween("item", lines)

fixeditems = []
for item in items:
    # get the article url
    link = re.search("<link>(.*?)</link>", item)
    link = link.group(1)
    # scrape the content (curl | tidy | grep word_count
    fullcontent = getFullContent(link)

    # and now we just need to remove the paragraph attributes because who cares
    newcontent = fullcontent.splitlines()
    newcontent = [re.sub(r"<p.*?>", r"<p>", line) for line in newcontent]
    newcontent = ' '.join(newcontent)

    # and now we plug the content into the item
    # search
    head = r"<description><!\[CDATA\[<p class=\"descender\">"
    tail = r".*?\]\]"
    search = head + tail
    # replace; don't need to escape for substitution
    head2 = r"<description><![CDATA[<p class=\"descender\">"
    tail2 = r"]]"
    replace = head2 + newcontent + tail2

    fixeditem = re.sub(search, replace, item)
    fixeditems.append(fixeditem)

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
print done
    
