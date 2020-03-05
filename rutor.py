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
from typing import List, Tuple
from pyquery import PyQuery as pq
import requests

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
    magnet: str
    name: str
    size: int
    seeds: int
    leech: int
    engine_url: str
    desc_link: str

class rutor(object):
    """
    `url`, `name`, `supported_categories` should be static variables of the engine_name class,
     otherwise qbt won't install the plugin.

    `url`: The URL of the search engine.
    `name`: The name of the search engine, spaces and special characters are allowed here.
    `supported_categories`: What categories are supported by the search engine and their corresponding id,
    possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books').
    """
    ip = '127.0.0.1'
    port = '9050'
    url = 'http://rutor.info'
    name = 'Full engine name'    
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4', 'music': '1', 'games': '2', 'anime': '7', 'software': '3'}
            
    def __init__(self):        
        self.initProxy()
        #self.loadPageRows(open('testsearchpage.txt', 'r', encoding='utf8').read())
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

    def loadPageRows(self, content: str)->List[urlInfo]:
        urlMain = pq(content)
        table = urlMain('#index')
        rows = table('tr[class!="backgr"]')
        result = list()
        for row in rows:
            element = urlInfo()            

            columns = pq(row)('td')
            datacolumn = pq(columns[1])
            
            dcobjects = datacolumn('a')
            element.magnet = dcobjects[1].attrib['href']
            element.link = dcobjects[2].attrib['href']
            element.name = dcobjects[2].text
            
            sizestring = columns[columns.length-2].text
            sizebaseValue = re.findall(r'\d+\.\d+', sizestring)[0]
            multiplier = 1
            if 'KB' in sizestring:
                multiplier = 1024
            if 'MB' in sizestring:
                multiplier = pow(1024, 2)
            if 'GB' in sizestring:
                multiplier = pow(1024, 3)
            if 'TB' in sizestring:
                multiplier = pow(1024, 4)

            element.size = int((float(sizebaseValue)*multiplier))

            seedspeers = pq(columns[columns.length-1])
            element.seeds = int(seedspeers('.green').text())
            element.peers = int(seedspeers('.red').text())

            result.append(element)
        return result

    def find(self, categories: eCategories, searchMethod : eSearchMethod, searchIn: eSearchIn, sort: eSort, order: eOrder, searchString:str):
        page = 0
        results = list()
        while True:
            url = f'http://rutor.info/search/{page}/{categories.value}/{searchMethod.value}{searchIn.value}0/{sort.value+order.value}/{searchString}'

            urldata = self.getUrlData(url)

            rows = self.loadPageRows(urldata)
            if len(rows) < 0:
                break
            page+=1
            for row in rows:
                results.append(row)                    
            
        return results
    

    def renew_tor_ip(self):
        if '127.0.0.1' in self.ip:
            try:
                with Controller.from_port(port = 9051) as controller:
                    controller.authenticate()
                    controller.signal(Signal.NEWNYM)
            except:
                return

    def getProxyFrom_proxylist_com(self) -> Tuple[str, str]:
        res = requests.get('https://api.getproxylist.com/proxy?lasttested=1&protocol=socks5')
        if res.status_code == 200:
            proxyinfo = json.loads(res.content)
            return proxyinfo['ip'], proxyinfo['port']
        return None

    def testProxy(self, ipcandidate: str, portcandidate: str) -> bool:
        return self.getUrlDataFull('http://rutor.info', ipcandidate, portcandidate) is not None

    def initProxyFromFile(self) -> bool:
        proxylist = None
        if path.exists('proxylist.txt'):
            proxylist = open('proxylist.txt', 'r')
        else:
            return False
        
        for record in proxylist.readlines():
            splittedRecord = record.split(' ')
            ipcandidate = splittedRecord[0]
            portcandidate = splittedRecord[1]
            if self.testProxy(ipcandidate, portcandidate):
                self.ip = ipcandidate
                self.port = portcandidate
                proxylist.close()
                return True
        
        proxylist.close()
        return False

    def initProxy(self) -> bool:
        if self.initProxyFromFile():
            return True
        while True:
            ipport = self.getProxyFrom_proxylist_com()
            if ipport is None:
                return False
            ipcandidate = ipport[0]
            portcandidate = ipport[1]
            if self.testProxy(ipcandidate, portcandidate):
                self.ip = ipcandidate
                self.port = portcandidate
                proxylist = open('proxylist.txt', 'a')
                proxylist.write(f'{ipcandidate} {portcandidate}\r\n')
                proxylist.close()
                return True

    def getUrlData(self, url: str) -> str:
        return self.getUrlDataFull(url, self.ip, self.port)

    def getUrlDataFull(self, url: str, ipv: str, portv: str) -> str:
        self.renew_tor_ip()

        output = io.BytesIO()
        query = pycurl.Curl()
        query.setopt(pycurl.URL, url)
        """
        query.setopt(pycurl.PROXY, 'localhost')
        query.setopt(pycurl.PROXYPORT, 9050)
        """
        query.setopt(pycurl.PROXY, ipv)
        query.setopt(pycurl.PROXYPORT, int(portv))
        #"""
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        query.setopt(pycurl.WRITEFUNCTION, output.write)

        try:
            query.perform()                            
            return output.getvalue().decode('UTF-8')    
        except:
            return None

if __name__ == "__main__":
    rt = rutor()
