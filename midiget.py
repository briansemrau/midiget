# coding: utf-8
"""
(c) Valerio Velardo, velardovalerio@gmail.com, 2015

This program crawls the pages of a website and downloads all the midi files it
finds. The midi files are saved in a directory called 'savedmidi'. 
The program is launched from the command line. 2 parameters should be 
specified:
 1- the url of the start page 
 2- the max number of pages to crawl before the program stops

The second parameter is optional (default value = 1000 pages)
"""

import urllib.request, urllib.parse, urllib.error
import requests
import re
import urllib.parse
import os
import errno
import sys
import bs4 as bs 
import time


def crawl_and_save(start_page, MAX_PAGES, out_path):
    """ Crawl pages of website from start_page and save all midi files"""
    
    start_time = time.time()
    page = 1
    links_to_crawl = [start_page]
    links_crawled = []
    url_files = []
    url_start_page = urllib.parse.urlparse(start_page)
    netloc = url_start_page.netloc    
    # loop over the pages of the website 
    while page <= MAX_PAGES:
        page_to_download = links_to_crawl[0]
        sauce = urlopen(page_to_download)
        soup = bs.BeautifulSoup(sauce, 'lxml')
        # loop over all links in a page
        for link_tag in soup.find_all('a'):
            href = str(link_tag.get('href'))
            href = str(handle_relative_link(page_to_download, href))
            # check link wasn't encountered before and is internal
            if (href not in links_crawled and 
                href not in links_to_crawl and
                is_internal_link(href, netloc) and 
                href not in url_files):
                # check if links takes to a midi file
                if is_midi(href):
                    file_name = href.split('/')[-1]
                    url_files.append(href)
                    save_file(href, file_name, out_path)
                    print("Saved: ", file_name)
                else:
                    links_to_crawl.append(href)
        links_crawled.append(links_to_crawl.pop(0))
        if page % 10 == True:
            pagesPerSec = (time.time() - start_time) / page
            print()
            print('Pages crawled:', page)
            print('Time so far:', time.time() - start_time, "sec") 
            print('Avg time per page:', pagesPerSec, "sec")
            print()
        page = page + 1
        # exit if MAX_pages is reached
        if page == MAX_PAGES:
            print()
            print("Max no. of pages reached!")
            print()
            sys.exit(0)
        # exit if all pages have been crawled
        if len(links_to_crawl) == 0:
            print()
            print("All the pages of the website have been crawled!")
            print()
            break
        
def is_internal_link(link, netloc):
    """ Check if a link belongs to the website"""
    
    return bool((re.search(netloc, link)))
    
# function needed to handle relative links
def save_file(url_file, file_name, out_path):  
    """ Save midi file in directory 'midisaves'"""
    
    path = os.path.join(out_path, file_name)
    urlretrieve(url_file, path)

    # write metadata to jsonl
    with open(os.path.join(out_path, 'index.jsonl'), 'a') as f:
        f.write('{"url": "%s", "filename": "%s"}\n' % (url_file, file_name))

# handle relative links
def handle_relative_link(base_link, link):
    """" If necessary, transform relative links into absolute links"""
    
    if bool(re.search('^http', link)):
        return link
    else:        
        return urllib.parse.urljoin(base_link, link)

def is_midi(link):
    """ Check if a link leads to a midi file"""
    
    return bool(re.search('\.mid$|\.midi$|freemidi\.org/getter-', link))
    
def make_sure_path_exists(path):
    """ Check if 'savemidi' directory exists, otherwise create it"""
    
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def check_type_max_pages(MAX_PAGES):
    """ Check that max_pages argument input by user is int"""
    
    try:
        int(MAX_PAGES)
    except ValueError:
        print()
        print("The 2nd argument (i.e., max no. pages) must be an integer.")
        print()
        sys.exit(0)

def check_no_args(arguments):
    """ Check that user has input at least 1 argument"""
    
    if len(arguments) < 2:
        print()
        print("At least 1 argument (i.e., start page) must be provided.")
        print()
        sys.exit(0)
        
def check_start_page_url(start_page):
    """ Check that start_page argument input by the user is a valid url"""
    
    try:
        urlopen(start_page)
    except IOError as e:
        print(e)
        print()
        print("Insert valid url (e.g., http://google.com).")
        print()
        sys.exit(0)

def urlopen(url):
    """ Open url with a different user agent """

    sauce = requests.get(url, headers={'User-Agent' : "Mozilla/5.0"})
    return sauce.text

def urlretrieve(url, path):
    """ Retrieve url with a different user agent """

    sauce = requests.get(url, headers={'User-Agent' : "Mozilla/5.0"})
    with open(path, 'wb') as f:
        f.write(sauce.content)

if __name__ == "__main__":
    # check args are ok
    check_no_args(sys.argv)
    start_page = sys.argv[1]
    check_start_page_url(start_page)
    if len(sys.argv) > 2:
        check_type_max_pages(sys.argv[2])
        MAX_PAGES = int(sys.argv[2])
    else:
        MAX_PAGES = 1000
    if len(sys.argv) > 3:
        out_path = sys.argv[3]
    else:
        out_path = "./savedmidi"
    make_sure_path_exists(out_path)
    crawl_and_save(start_page, MAX_PAGES, out_path)
    