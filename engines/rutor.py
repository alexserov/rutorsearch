#VERSION: 1.00
#AUTHORS: YOUR_NAME (YOUR_MAIL)

# LICENSING INFORMATION

#from helpers import download_file, retrieve_url
#from novaprinter import prettyPrinter
#import sgmllib
from enum import Enum
from os import path
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
from pathlib import Path

class eCategories(object):
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

#'all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books'
class qbCategories(object):
    all = [eCategories.all]
    movies = [eCategories.foreign_movies, eCategories.russian_movies, eCategories.sci_pop_movies, eCategories.cartoons]
    tv = [eCategories.foreign_series, eCategories.tv, eCategories.russian_series]
    music = [eCategories.music]
    anime = [eCategories.anime, eCategories.cartoons]
    software = [eCategories.games, eCategories.software]
    pictures = [eCategories.cartoons, eCategories.humor]
    books = [eCategories.books, eCategories.household]


class eSort(object):
    date = 0
    seeds = 2
    peers = 4
    caption = 6
    relevance = 10

class eOrder(object):
    descending = 0
    ascending = 1

class eSearchMethod(object):
    phrase_full = 0
    all_words = 1
    any_word = 2
    expression = 3

class eSearchIn(object):
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
    name = 'Rutor with proxy'    
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4', 'music': '1', 'games': '2', 'anime': '7', 'software': '3'}    
            
    def __init__(self):           
        self.dbgprint('init')     
        self.initProxy()
        #self.loadPageRows(open('testsearchpage.txt', 'r', encoding='utf8').read())
        #self.find(eCategories.music, eSearchMethod.all_words, eSearchIn.caption, eSort.relevance,eOrder.ascending,'music')
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
        # 
        from helpers import download_file, retrieve_url
        from novaprinter import prettyPrinter
        #import sgmllib                 
        """
        link => A string corresponding the the download link (the .torrent file or magnet link)
        name => A unicode string corresponding to the torrent's name (i.e: "Ubuntu Linux v6.06")
        size => A string corresponding to the torrent size (i.e: "6 MB" or "200 KB" or "1.2 GB"...)
        seeds => The number of seeds for this torrent (as a string)
        leech => The number of leechers for this torrent (a a string)
        engine_url => The search engine url (i.e: http://www.mininova.org)
        desc_link => A string corresponding to the the description page for the torrent
        
        """

        for result in self.findHelper(what, cat):
            prettyPrinter({
                'link':result.magnet, 
                'name' : result.name.replace("|", "!"),
                'size' : str(result.size),
                'seeds' : str(result.seeds),
                'leech' : str(result.peers),
                'engine_url' : 'http//rutor.info',
                'desc_link' : '-1'
                })
            #print(f'{result.magnet}|{result.name.replace("|", "!")}|{result.size}|#{result.seeds}|#{result.peers}|http://rutor.info')
        """
        Here you can do what you want to get the result from the search engine website.
        Everytime you parse a result line, store it in a dictionary
        and call the prettyPrint(your_dict) function.

        `what` is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        `cat` is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
        """
    def findHelper(self, what, cat):

        qbcats = getattr(qbCategories, cat)
        for qbcat in qbcats:
            count = 0
            for result in self.find(qbcat, eSearchMethod.all_words, eSearchIn.caption, eSort.seeds, eOrder.descending, what):
                if count > 50:
                    break
                if result.seeds < 1:
                    break
                count+=1
                yield result


    def loadPageRows(self, content: str):
        urlMain = pq(content)
        table = urlMain('#index')
        rows = table('tr[class!="backgr"]')        
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

            yield element

    def find(self, categories: int, searchMethod : int, searchIn: int, sort: int, order: int, searchString:str):
        page = 0        
        while True:
            url = f'http://rutor.info/search/{page}/{categories}/{searchMethod}{searchIn}0/{sort+order}/{searchString}'

            urldata = self.getUrlData(url)

            if urldata is None or 'rutor' not in urldata:
                if self.initProxy():
                    continue
                else:
                    break
            
            page+=1
            stop = True
            for row in self.loadPageRows(urldata):
                stop = False
                yield row
            
            if stop:
                break

    def renew_tor_ip(self):
        if '127.0.0.1' in self.ip:
            try:
                with Controller.from_port(port = 9051) as controller:
                    controller.authenticate()
                    controller.signal(Signal.NEWNYM)
            except:
                return

    def getProxyFrom_proxylist_com(self) -> Tuple[str, str]:
        res = requests.get('https://api.getproxylist.com/proxy?lasttested=1&protocol=socks5&allowshttps=1')
        if res.status_code == 200:
            proxyinfo = json.loads(res.content)
            return proxyinfo['ip'], proxyinfo['port']
        return None

    def testProxy(self, ipcandidate: str, portcandidate: str) -> bool:
        self.dbgprint(f'test[{ipcandidate}:{portcandidate}]')
        result = self.getUrlDataFull('https://api.ipify.org/?format=json', ipcandidate, portcandidate)
        try:
            return json.loads(result)['ip'] is not None
        except:
            return False


    def initProxyFromFile(self) -> bool:
        self.dbgprint('start init from file')
        proxylist = None
        if Path('proxylist.txt').exists():
            proxylist = open('proxylist.txt', 'r')
        else:
            proxylist = open('proxylist.txt', 'w')
            proxylist.write('127.0.0.1 9050\n')
            proxylist.close()
            proxylist = open('proxylist.txt', 'r')        
        
        for record in proxylist.readlines():
            if not record:
                break
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
        self.dbgprint('start init from network')
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
                proxylist.write(f'{ipcandidate} {portcandidate}\n')
                proxylist.close()
                return True

    def getUrlData(self, url: str) -> str:
        self.renew_tor_ip()
        return self.getUrlDataFull(url, self.ip, self.port)

    def getUrlDataFull(self, url: str, ipv: str, portv: str) -> str:        
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
        query.setopt(pycurl.TIMEOUT, 10)
        query.setopt(pycurl.SSL_VERIFYPEER, 0)
        query.setopt(pycurl.SSL_VERIFYHOST, 0)
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        query.setopt(pycurl.WRITEFUNCTION, output.write)

        try:
            query.perform()                            
            return output.getvalue().decode('UTF-8')    
        except:
            return None

    def dbgprint(self, value):
        """
        print(value)
        """

if __name__ == "__main__":
    print('main\n')
    rt = rutor()
    rt.search(r'breaking%20bad', 'movies')
