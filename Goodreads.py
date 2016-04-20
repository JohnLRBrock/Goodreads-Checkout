'''
John Brock

2016-04-20

Randomly select books from goodreads, search library for them, then open up webpages when they are found until a certain number of pages is met
'''

import random
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
import re
import requests
import time

start = time.time()


def get_text(tree, tg, lst):
    for element in tree.iter(tag=tg):
        lst.append(element.text)

def get_data():
    get_text(tree, 'title', titles)
    get_text(tree, 'name', authors)
    get_text(tree, 'num_pages', pages)

def make_liburl(search_terms):
    liburl= "http://catalog.pascolibraries.org/cgi-bin/koha/opac-search.pl?idx=&q="
    for targets in re.findall('[(].+?[)]',search_terms):
        search_terms = search_terms.replace(targets,"")
    for words in search_terms.split():
        liburl = liburl+"+"+words
    liburl = liburl + "&limit=available&limit=itype:BOOK"
    return liburl

def remove_book(index):
    authors.remove(authors[index])
    titles.remove(titles[index])
    pages.remove(pages[index])

def search_book():
    global page_total
    global book_total
    random_book = random.randint(0,book_total-1)
    search_terms = authors[random_book]+' '+titles[random_book]
    search_url = make_liburl(search_terms)
    fhand = requests.get(search_url)
    found_book = False
    for line in fhand:
        if "Copies available for loan:" in str(line) or "Available" in str(line):
            found_book = True
    if found_book == True:
        webbrowser.open(search_url)
        print("Found", titles[random_book], "by", authors[random_book])
        try:
            page_total = page_total + int(pages[random_book])
        except:
            page_total = page_total + 240
            print("weirdness on",titles[random_book])
        book_total = book_total - 1
        remove_book(random_book)
    else:
        print("Couldn't find",titles[random_book],"by",authors[random_book])
        webbrowser.open(search_url)
        book_total = book_total - 1
        remove_book(random_book)


titles = []
authors = []
pages = []
page_total = 0
page_goal = int(input("How many pages do you want to read?\n"))
key = input("Input your goodreads API key")
secret = ""
current_page = "1"

# get and parse data from goodreads
url = "https://www.goodreads.com/review/list/12433997.xml?key="+key+"&shelf=to-read&per_page=200&page="+current_page
XML = requests.get(url)
tree = ET.fromstring(XML.content)

# how many pages do I need to search through?
numpages = tree.find('./books').attrib['numpages']

get_data()


# cycle through the rest of the pages
while(int(numpages)>int(current_page)):
    current_page = str(int(current_page)+1)
    url = "https://www.goodreads.com/review/list/12433997.xml?key="+key+"&shelf=to-read&per_page=200&page="+current_page
    XML = requests.get(url)
    tree = ET.fromstring(XML.content)
    get_data()

book_total = len(titles)

while(page_goal>page_total):
    search_book()
end = time.time()
print("Finished in",end - start,"seconds.\n")
