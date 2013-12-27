'''
Created on Dec 18, 2013

@author: KevinVillela
'''
import sys #To flush stdout
from DatumBox import DatumBox
#import urllib3
from math import trunc
import jdcal
from urllib.parse import quote_plus
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import webarticle2text
#from gevent.pool import Pool
from SentimentThread import SentimentThread
from TorThread import TorThread
from datetime import timedelta
import threading
import gc
import ssl
from queue import Queue
import justext
import requests
import time
import chardet
import atexit
#import gevent.monkey
#gevent.monkey.patch_all(thread=False)


class Crawler(object):
    '''def do_something(response, **kwargs):
        global numberOfArticlePages
        global total
        if (response.status_code == 200):
            numberOfArticlePages += 1
            print "\r" + str(numberOfArticlePages) + " / " + str(total) + " articles crawled to.",
            sys.stdout.flush()
    '''
    def __init__(self, MIN_ARTICLES_PERCENT = .9, MAX_THREADS = 50 ):
        self.threads = []
        self.articlesCompleted = 0
        self.MIN_ARTICLES_PERCENT = MIN_ARTICLES_PERCENT
        self.MAX_THREADS = MAX_THREADS
        self.dbError = False
        atexit.register(self.exitProgram)
        
    def getUser(self, userInfo, userNumber):
        for user in userInfo:
            if (user['userNumber'] == userNumber):
                return user
            
    def articleAnalyzed(self, success):
        self.articlesCompleted = self.articlesCompleted + 1
        if (success == False):
            self.dbError = True
        print(("\r" + str(self.articlesCompleted) + " / " + str(len(self.threads)) + " articles analyzed."), end=' ')
        sys.stdout.flush()

    def crawl(self, userInfo, userNumber, dateToSearch, daysToSearch, fileName):
        global proxies
        user = userInfo[userNumber]
        datum_box = DatumBox(user['APIKey'])  
        sentimentsFile = open(fileName, "a")
        daysToGoBack = 1;
        print("Starting Tor...")
        self.torThread = TorThread(self)
        self.torThread.start()
        time.sleep(5)
        #googleHttp = urllib3.PoolManager()
        while(daysToGoBack <= daysToSearch):
            #toSleep = 10
            #print "sleeping for " + str(toSleep) + " seconds in a pathetic attempt to bypass Google...."
            #time.sleep(toSleep)
            print("Searching on date " + dateToSearch.strftime("%m/%d/%Y") + " (day " + str(daysToGoBack) + " of " + str(daysToSearch) + ")")
            
            #try:
            julianDate = trunc(sum(jdcal.gcal2jd(dateToSearch.year, dateToSearch.month, dateToSearch.day)) + .5)
            keyword = "Boeing OR Caterpillar OR McDonalds OR Microsoft OR Nike OR Coca-Cola OR Visa OR Wal-Mart OR Disney OR Verizon OR Exxon OR IBM OR JPMorgan OR Intel"
            sites = ["http://money.cnn.com/" + dateToSearch.strftime("%Y"), "http://www.bloomberg.com/news/", "http://www.rttnews.com/", "http://www.reuters.com/finance", "money.usnews.com", "www.ft.com/home/us", "http://www.cnbc.com/" ]
            query = "site:" + sites[0]
            first = True
            for site in sites:
                if (first):
                    first = False
                    continue
                query = query + " OR site:" + site
            query = query + " " + keyword + " daterange:" + str(julianDate) + "-" + str(julianDate);
            #print("Query: " + query);
            query = quote_plus(query)
            #gs = GoogleSearch(query);
            #gs.results_per_page = 50
            #results = gs.get_results()
            headers={'User-agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6'}
            numberOfResults = 50
            startPageQuery = "https://startpage.com/do/search?cat=web&cmd=process_search&language=english&engine0=v1all&abp=1&x=-843&y=-302&prfh=lang_homepageEEEs%2Fair%2Feng%2FN1Nenable_post_methodEEE0N1NsslEEE1N1Nfont_sizeEEEmediumN1Nrecent_results_filterEEE1N1Nlanguage_uiEEEenglishN1Ndisable_open_in_new_windowEEE1N1Nnum_of_resultsEEE" + str(numberOfResults) + "N1N&suggestOn=0&query=" + query
            print (startPageQuery)
            #request = urllib2.Request('GET', startPageQuery, None, headers)
            #print(startPageQuery)
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv3) #monkey patch...
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context)) #monkey patch...
            urllib.request.install_opener(opener) #monkey patch...
            request = urllib.request.Request(url=startPageQuery, data=None, headers=headers)
            response = urllib.request.urlopen(request)
            resultsPage = response.read().decode('utf-8')
            soup = BeautifulSoup(resultsPage)
            resultDivs = soup.findAll("div", { "class" : "result" })
            results = []
            for resultDiv in resultDivs:
                if ('none' in resultDiv.get('class')):
                    continue
                h3 = resultDiv.find("h3")
                if (h3 is None):
                    continue
                url = h3.find("a", href=True)['href']
                results.append(url)
            #except SearchError, e:
            #    print "Search failed: %s" % e
            #    continue
            #Crawl to each web site and extract web articles
            try:
                numberOfArticlePages = 0
                articles = []
                articleURLs = []
                total = len(results)
                def fetch(url):
                    #request = urllib.request.Request(url)
                    #response = urllib.request.urlopen(request)
                    #resultsPage = response.read().decode('ascii')
                    response = requests.get(url)
                    #print (response.encoding)
                    #print (chardet.detect(response.content))
                    #paragraphs = justext.justext(response.content, justext.get_stoplist("English"),default_encoding=chardet.detect(response.content)['encoding'])
                    paragraphs = justext.justext(response.text, justext.get_stoplist("English"))
                    #paragraphs = justext.justext(resultsPage, justext.get_stoplist("English"))
                    article = ""
                    for paragraph in paragraphs:
                      if not paragraph.is_boilerplate:
                        article += paragraph.text
                    articles.append(article)
                    articleURLs.append(url)
                    #f.close()
                    print("\r" + str(len(articles)) + " / " + str(len(results)) + " articles crawled to.", end=' ')
                    sys.stdout.flush()
                    #response = requests.request('GET', url, hooks = {'response' : do_something}, timeout=60.0)
                    #articlePages.append(response)
                
                # Was using gevent, but then switched to python3.3, which does not yet support gevent
                crawlThreads = []
                for res in results:
                    t = threading.Thread(target=fetch, args={res})
                    t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
                    t.start()
                    crawlThreads.append(t)
                for thread in crawlThreads:
                    thread.join(60)
                    if (thread.isAlive()):
                        print("A URL has timed out")
                # I was using grequests, but it appeared that they were leaking file descriptors... :(
                #articleRequests = (grequests.get(res, hooks = {'response' : do_something}, timeout=60) for res in results)
                #articlePages = grequests.map(articleRequests)
                print()
            except gevent.Timeout:
                if (numberOfArticlePages >= len(results) * self.MIN_ARTICLES_PERCENT):
                    print(("Timeout, but continuing because we have " + str(numberOfArticlePages) + " articles."))
                else:
                    print(("Timeout, going to next day because we have only " + str(numberOfArticlePages) + " articles."))
                    continue
            '''articles = []
            articleURLs = []
            for articlePage in articlePages:
                if (articlePage is not None):
                    articles.append(webarticle2text.extractFromHTML(articlePage.text))
                    articleURLs.append(articlePage.url)
            '''
            print("All articles (" + str(len(articles)) + " of 'em) for date " + dateToSearch.strftime("%m/%d/%Y") + " returned, now being analyzed...")

            i = 1
            mutex_writefile = threading.Lock()
            #for res in results:
            self.dbError = True
            while (self.dbError == True): # This might get some articles twice, but its okay because once they are in the db it won't matter
                self.dbError = False
                self.threads = []
                for articleText, articleURL in zip(articles, articleURLs):
                    #articleURL = res.url.encode("utf8")
                    thread = SentimentThread(articleURL, articleText, i, fileName, dateToSearch, mutex_writefile, datum_box, "127.0.0.1:8118", self, user['subscriptionID'])
                    #thread.daemon = True
                    thread.start()
                    self.threads.append(thread)
                    i = i + 1
                    if (len(self.threads) >= self.MAX_THREADS):
                        for thread in self.threads:
                            thread.join()
                for thread in self.threads:
                    thread.join()
                self.articlesCompleted = 0
                if (self.dbError == True):
                    userNumber = userNumber - 1
                    if (userNumber < 0):
                        print("Out of Users")
                        return
                    user = userInfo[userNumber]
                    datum_box = DatumBox(user['APIKey']) 
                    print("Switching users and trying again.")
                    self.torThread.stop()
                    self.torThread.join()
                    time.sleep(5)
                    print("Tor stopped. Restarting...")
                    self.torThread = TorThread(self)
                    self.torThread.start()
                    time.sleep(5)
                
            #Next day!
            print()        
            dateToSearch = dateToSearch - timedelta(1)
            daysToGoBack += 1
        sentimentsFile.close()
        print("Congratulations! All articles analyzed. Shutting down...")
    def killThreads(self):
        pass
        #for thread in self.threads:
            #   thread.stop()
    def exitProgram(self):
        self.torThread.stop()
        print("Shut down successfully.")
    ''' End of Crawl Class ''' 