#VERSION: 1.00
#AUTHORS: YOUR_NAME (YOUR_MAIL)

# LICENSING INFORMATION

#from helpers import download_file, retrieve_url
#from novaprinter import prettyPrinter
from enum import Enum
from os import path
#import sgmllib
import io
import pycurl
import json
import sys
from stem import Signal
from stem.control import Controller
import re
from typing import List
from html.parser import HTMLParser

# some other imports if necessary
class eCategories(Enum):
    all = 0
    foreign_movies = 1
    music = 2
    other = 3
    foreign_series = 4
    russian_movies = 5
    tv = 6
    cartoons = 7
    games = 8
    software = 9
    anime = 10
    books = 11
    sci_pop_movies = 12
    sports_and_health = 13
    household = 14
    humor = 15
    russian_series = 16
    foreign_releases = 17

class eSort(Enum):
    date = 0
    seeds = 2
    peers = 4
    caption = 6
    relevance = 10

class eOrder(Enum):
    descending = 0
    ascending = 1

class eSearchMethod(Enum):
    phrase_full = 0
    all_words = 1
    any_word = 2
    expression = 3

class eSearchIn(Enum):
    caption = 0
    caption_and_description = 1   

class urlInfo(object):
    link: str
    name: str
    size: int
    seeds: int
    leech: int
    engine_url: str
    desc_link: str

class MyHTMLParser(HTMLParser):
    skip = True
    result = None
    currentInfo = None
    currentColumn = -1
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = list()

    def handle_starttag(self, tag, attrs):
        if self.skip == True:
            if tag == 'div' and self.getAttrValue(attrs, 'id') == 'index':                
                self.skip = False
                return
        if self.skip == True:
            return
        if tag == 'tr' and (self.getAttrValue(attrs, 'class')=='gai' or self.getAttrValue(attrs, 'class')=='tum'):
            self.currentInfo = urlInfo()
            self.currentColumn = -1
        
        if tag == 'td' and self.currentInfo:
            self.currentColumn+=1
            if self.currentColumn == 1:
                """
                link
                """
            if self.currentColumn == 3:
                """
                size
                """
            if self.currentColumn == 4:
                """
                seeds peers
                """
        

    def getAttrValue(self, attrs: list, attrName: str):
        for attr in attrs:
            if attr[0] == attrName:
                return attr[1]
        return None

    def handle_endtag(self, tag):
        if self.skip == True:
            return
        if tag == 'tr' and self.currentInfo:
            self.result.append(self.currentInfo)
        if tag == 'table':
            self.skip = True
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)

class rutor(object):
    """
    `url`, `name`, `supported_categories` should be static variables of the engine_name class,
     otherwise qbt won't install the plugin.

    `url`: The URL of the search engine.
    `name`: The name of the search engine, spaces and special characters are allowed here.
    `supported_categories`: What categories are supported by the search engine and their corresponding id,
    possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books').
    """
    url = 'http://rutor.info'
    name = 'Full engine name'    
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4', 'music': '1', 'games': '2', 'anime': '7', 'software': '3'}
            
    def __init__(self):        
        self.find(eCategories.music, eSearchMethod.all_words, eSearchIn.caption, eSort.relevance,eOrder.ascending,'music')
        """
        some initialization
        """

    def download_torrent(self, info):
        """
        Providing this function is optional.
        It can however be interesting to provide your own torrent download
        implementation in case the search engine in question does not allow
        traditional downloads (for example, cookie-based download).
        """
        #print download_file(info)
    
    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        #http://rutor.info/search/PAGE/{eCategories}/{eSearchMethod}{eSearchIn}0/{eSort+eOrder}/{search_string}        
        #https://api.getproxylist.com/proxy?protocol=http&lasttested=60
         
        """
        Here you can do what you want to get the result from the search engine website.
        Everytime you parse a result line, store it in a dictionary
        and call the prettyPrint(your_dict) function.

        `what` is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        `cat` is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
        """

    def getData(self, path: str)->urlInfo:
        data = self.getUrlData(f'http://rutor.info{path}')
        #<h1>HEADER</h1>


    def find(self, categories: eCategories, searchMethod : eSearchMethod, searchIn: eSearchIn, sort: eSort, order: eOrder, searchString:str):
        page = 0
        results = list()
        while True:
            url = f'http://rutor.info/search/{page}/{categories.value}/{searchMethod.value}{searchIn.value}0/{sort.value+order.value}/{searchString}'

            urldata = self.getUrlData(url)
            parser = MyHTMLParser()
            parser.feed(urldata)
            parser.close()
                      
            shouldBreak = True    
            for res in re.findall(r'\/torrent\/\d+\/[^\""]+',self.getUrlData(url)):
                results.append(res)
                shouldBreak = False
            if shouldBreak:
                break
            page+=1
        return results
    

    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)


    def getUrlData(self, url: str):
        self.renew_tor_ip()

        output = io.BytesIO()
        query = pycurl.Curl()
        query.setopt(pycurl.URL, url)
        query.setopt(pycurl.PROXY, 'localhost')
        query.setopt(pycurl.PROXYPORT, 9050)
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        query.setopt(pycurl.WRITEFUNCTION, output.write)
        query.perform()            
        
        
        return output.getvalue().decode('UTF-8')    

if __name__ == "__main__":
    rt = rutor()
