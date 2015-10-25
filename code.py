#!/usr/bin/python
import re
import subprocess

def getFullContent(link):
    curl = "curl -L " + link
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


data = ""
with open('content.txt', 'r') as text:
    data = text.read()

lines = data.splitlines()

items, numbers = getStuffBetween("item", lines)

fixeditems = []
count =0 
for item in items:
    link = re.search("<link>(.*?)</link>", item)
    link = link.group(1)
    fullcontent = getFullContent(link)
    newcontent = fullcontent.splitlines()
    newcontent = [re.sub(r"<p.*?>", r"<p>", p) for p in newcontent]
    newcontent = ' '.join(newcontent)
    #newcontent = "------ ITEM "+str(count)+" CONTENT ------"
    #count +=1
    fixeditem = re.sub(r"<content:encoded><!\[CDATA\[.*?\]\]>", r"<content:encoded><![CDATA["+newcontent+"]]>", item) # don't need to escape the sub-side
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
    #newlines += lines[laststart:start-1].append(fixeditems[index])
    lastend=end
_, finend = numbers[len(numbers)-1]
newlines.extend(lines[finend+1:]) # grabs all the shit after the final item

done = "\n\n ".join(newlines)
print done
    
