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

# Type in your Goodreads developer key and User id
key = ""
user_id = ""

# pull text from xml data and append to a list
def get_text(tree, tg, lst):
    for element in tree.iter(tag=tg):
        lst.append(element.text)
# use get_text() to extract book titles, authors, and page numbers
def get_data():
    try:
        get_text(tree, 'title', titles)
        get_text(tree, 'name', authors)
        get_text(tree, 'num_pages', pages)
    except:
        print("Failed to retrieve data form xml tree.\n")

# take book title and author names and create the url that will be used to conduct the search
def make_liburl(search_terms):
    liburl= "http://catalog.pascolibraries.org/cgi-bin/koha/opac-search.pl?idx=&q="
    for targets in re.findall('[(].+?[)]',search_terms):
        search_terms = search_terms.replace(targets,"")
    for words in search_terms.split():
        liburl = liburl+"+"+words
    liburl = liburl + "&limit=available&limit=itype:BOOK"
    return liburl

# so we don't search for a book twice
def remove_book(index):
    authors.remove(authors[index])
    titles.remove(titles[index])
    pages.remove(pages[index])

# randomly choose a book and search for it in the library catalogue
def search_book():
    global page_total
    global book_total
    random_book = random.randint(0,book_total-1)
    search_terms = authors[random_book]+' '+titles[random_book]
    search_url = make_liburl(search_terms)
    try:
        fhand = requests.get(search_url)
    except:
        print("Failed to search library catalogue\n")
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
            print("weirdness on",titles[random_book],'\n')
        book_total = book_total - 1
        remove_book(random_book)
    else:
        print("Couldn't find",titles[random_book],"by",authors[random_book],"\n")
        book_total = book_total - 1
        remove_book(random_book)

# lists for storing book data
titles = []
authors = []
pages = []

page_total = 0
current_page = "1"
page_goal = int(input("How many pages do you want to read?\n"))


start = time.time()

# get and parse data from goodreads
url = "https://www.goodreads.com/review/list/"+user_id+".xml?key="+key+"&shelf=to-read&per_page=200&page="+current_page
try:
    XML = requests.get(url)
except:
    print("Failed to get xml data from Goodreads\n")

try:
    tree = ET.fromstring(XML.content)
except:
    print("Failed to parse XML data\n")

# find number of pages of xml data
try:
    numpages = tree.find('./books').attrib['numpages']
except:
    print("Couldn't discover number of pages of XML data\n")

get_data()

# cycle through any remaining pages of xml data
while(int(numpages)>int(current_page)):
    current_page = str(int(current_page)+1)
    url = "https://www.goodreads.com/review/list/"+user_id+".xml?key="+key+"&shelf=to-read&per_page=200&page="+current_page
    XML = requests.get(url)
    tree = ET.fromstring(XML.content)
    get_data()

book_total = len(titles)

# search for random books until page goal is met
while(page_goal>page_total):
    search_book()

# how long did that take?
end = time.time()
print("Finished in",end - start,"seconds.\n")
