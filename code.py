#!/usr/bin/python
import re
import subprocess
import multiprocessing


def getFullContent(link):
    """gets the actual content of the article"""
    curl = "curl -L " + link
    tidy = "tidy --force-output yes --vertical-space no -utf8 -w 100000 2>/dev/null"
    grep = "grep word_count"
    try:
        output = subprocess.check_output(curl + " | " + tidy + " | " + grep, shell=True)
    except subprocess.CalledProcessError as e:
        output = str(e.output)
    return output

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

def fixItems(items):
    """Replaces the item's description with the full content 
        of the article it links to; multiprocessed """
    fixeditems = multiprocessing.Manager().list()
    processes = []
    index = 0
    for item in items:
        def work(item, fixeditems, index):
            # get the link to the full article
            item = items[0]
            link = re.search("<link>(.*?)</link>", item)
            link = link.group(1)
            # gets the content from that article
            fullcontent = getFullContent(link)
            newcontent = fullcontent
            #newcontent = fullcontent.splitlines()
            #newcontent = [re.sub(r"<p.*?>", r"<p>", p) for p in newcontent]
            #newcontent = ' '.join(newcontent)
            #newcontent = "------ ITEM "+str(count)+" CONTENT ------"
            #count +=1
            #fixeditem = re.sub(r"<content:encoded><!\[CDATA\[.*?\]\]>", r"<content:encoded><![CDATA["+newcontent+"]]>", item) # don't need to escape the sub-side

            #now we plug in the content into the description
            fixeditem = re.sub(r"<!\[CDATA\[.*?\]\]>",
                               r"<![CDATA["+newcontent+"]]>",
                               item)
            # and get rid of the original content:encoded, because we don't need it
            fixeditem = re.sub(r"<content:encoded>.*?</content:encoded>", 
                               "", 
                               fixeditem,
                               flags=re.S) # sets single-line mode, 
                                    # so . matches EVERY character, including \n
            fixeditems.append((index, fixeditem))
        p = multiprocessing.Process(target=work, 
                                    args=(item, 
                                       fixeditems, 
                                       index))
        index += 1
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    fixeditems = sorted(fixeditems)
    fixeditems = [item[1] for item in fixeditems]
    return fixeditems


data = ""
with open('content.txt', 'r') as text:
    data = text.read()

lines = data.splitlines()

items, numbers = getStuffBetween("item", lines)

fixeditems = fixItems(items)
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
