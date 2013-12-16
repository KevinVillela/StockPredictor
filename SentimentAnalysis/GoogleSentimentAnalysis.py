'''
Created on Dec 1, 2013

@author: KevinVillela
'''
def getAPIKey(user_number):
    return { 
            1 : "a01778a8cafdedfc2e676b8ba0495a19", # API KEY for KVillela (DatumBox1)
            2 :  "6193d654c5eebe977005717702592f26", # API KEY for KevinV
            3 : "aafd2b194cfbe927cb85c4e1fc579141", # API KEY for villka02
            4 : "c15e170662def9c247a0d074f01f0222", # API KEY for MrMAV, still usable
            5 : "efdbf9d23fa099395061285c6f099422", # API KEY for JordanArmstrong (JArms1)
            6 : "d20bc2c623458697bdd93795b6b62ebc", #API KEY for SlyPro (SlyPro1)
            7 : "07b6561391d98533a14b62c25703884e", #API KEY for weispm02 (Weispm02)
            8 : "31c1f4c9515eb8b3e45b6eb2385eebfc", # API KEY for TestUser (Test1234)
            9 : "abe7659bbfb1bef45f27f23ee5ea2d93", # API KEY for Test5678 (Test5678)
            10: "f0fbbbfa171390e2c2db6cd54fc17af4", # API KEY for Test90 (Test90)
            11: "33a996e29a35f9e5ac9c007015529b56", #API KEY for DatumBox2 (DatumBox2)
            12: "5c8b8c72713dbc627de54d08303a12d3", #API KEY for DatumBox3 (DatumBox3)
            13: "68cb2f676303c2a908702804d7f777e7", #API KEY for DatumBox4 (DatumBox4)
            14: "e365916a2a059772faded70eacef545d", #API KEY for DatumBox5 (DatumBox5)
            15: "3313a3fb36fe35b05f038c44f32607e7", #API KEY for DatumBox6 (DatumBox6)
            16: "020eb0d148c3c8bb8d8acd29f5aaae34", #API KEY for DatumBox7 (DatumBox7)
            17: "5d20722e009d6c2180aa8ddd1d7a1b5b", #API KEY for DatumBox8 (DatumBox8)
            18: "43e72eef35675d2bdd3f37246bddf052", #API KEY for DatumBox9 (DatumBox9)
            19: "ad34470ff161ffd414a82b9ff1194c62", #API KEY for DatumBox10 (DatumBox10)
            20: "88ce955d4d524ab8413c76dc59ef4ffa" #API KEY for DatumBox11 (DatumBox11)
            }[user_number]
MAX_PROXIES = 50
MAX_TRIES = 7
MAX_THREADS = 50
MIN_ARTICLES_PERCENT = .9
numberOfArticlesToday = 0
numberOfArticlePages = 0
total = 0
seperator = "|"
dbError = False
proxies = {}

from DatumBox import DatumBox, DatumBoxError
import webarticle2text
import socket
import threading
from datetime import timedelta, datetime
import time # To sleep
from xgoogle.search import GoogleSearch, SearchError
import jdcal
from math import trunc
import grequests
import requests
import sys
import pprint
import urllib2
import urllib3
from urllib import urlencode, quote_plus
from httplib import BadStatusLine
from apiclient.discovery import build
from bs4 import BeautifulSoup
import gevent.monkey
gevent.monkey.patch_socket()
from gevent.pool import Pool

class SentimentThread(threading.Thread):
    def __init__(self, articleURL, articleText, articleNumber, sentimentsFileName, dateToSearch, mutex_writefile, datum_box, proxy, parent):
        super(SentimentThread, self).__init__()
        self.articleURL = articleURL
        self.articleText = articleText
        self.articleNumber = articleNumber
        self.sentimentsFileName = sentimentsFileName
        self.dateToSearch = dateToSearch
        self.mutex_writefile = mutex_writefile
        self.datum_box = datum_box
        self.proxy = proxy
        self.parent = parent
    def run(self):
        self.getSentimentOfArticle()
    def stop(self):
        print "Thread stopping..."
        sys.exit()
        return
    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        # TODO: in python 2.6, there's a simpler way to do : self.ident

        raise AssertionError("could not determine the thread's id")
    def getSentimentOfArticle(self):
        tries = 0
        sentiment = ""
        while (tries < MAX_TRIES):
            try:
                sentiment = self.datum_box.sentiment_analysis(self.articleText, self.proxy)
                break;
            except socket.timeout:
                print("\t ^^Article #" + str(self.articleNumber) + " timed out " + str(tries + 1) + " time(s)...")
                tries = tries + 1     
            except DatumBoxError, datumBoxError:
                if (datumBoxError.error_code == 11):
                    print "Daily DatumBox Limit Reached for API KEY " + self.datum_box.api_key
                    self.mutex_writefile.acquire()
                    global dbError
                    dbError = True
                    self.mutex_writefile.release()
                    self.parent.killThreads()
                    return       
            except urllib2.URLError, error:
                if (error.errno == 60): #Operation timed out
                    print("Operation timed out, likely due to the proxy.(Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1)  + ")")
                    global proxies
                    global MAX_STRIKES
                    proxies[self.proxy] = proxies[self.proxy] + 1
                    tries = tries + 1 
                    if (proxies[self.proxy] >= MAX_STRIKES):
                        print("Proxy " + self.proxy + " has struck out! Removing from list...")
                        del proxies[self.proxy]
                        return
            except socket.error, error:
                if (error.errno == 54): #Connection reset by peer
                    print("Connection reset by peer. ugh. Trying again. (Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1) + ")")
                    tries = tries + 1 
            except BadStatusLine:
                print("Could not get article: BadStatusLine. (Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1) + ")")
                return
            except SystemExit:
                print 'An exception flew by!'
        if ( tries == MAX_TRIES):
            return
        self.mutex_writefile.acquire()
        sentimentsFile = open(self.sentimentsFileName, 'a')
        sentimentsFile.write(self.articleURL + seperator)
        sentimentsFile.write(self.dateToSearch.strftime("%m/%d/%Y") + seperator)
        sentimentsFile.write(sentiment);
        sentimentsFile.write("\n")
        sentimentsFile.close()
        global numberOfArticlesToday
        numberOfArticlesToday = numberOfArticlesToday + 1
        self.mutex_writefile.release()
        self.parent.articleAnalyzed()
  
def do_something(response, **kwargs):
    global numberOfArticlePages
    global total
    if (response.status_code == 200):
        numberOfArticlePages += 1
        print "\r" + str(numberOfArticlePages) + " / " + str(total) + " articles crawled to.",
        sys.stdout.flush()
      
class Crawler(object):
    def __init__(self):
        self.threads = []
        self.articlesCompleted = 0
        
    def articleAnalyzed(self):
        self.articlesCompleted = self.articlesCompleted + 1
        print ("\r" + str(self.articlesCompleted) + " / " + str(len(self.threads)) + " articles analyzed."),
        sys.stdout.flush()

    def crawl(self, userNumber, dateToSearch, daysToSearch, fileName):
        global proxies
        API_Key = getAPIKey(userNumber);
        datum_box = DatumBox(API_Key)  
        global dbError
        sentimentsFile = open(fileName, "a")
        daysToGoBack = 1;
        googleHttp = urllib3.PoolManager()
        while(daysToGoBack <= daysToSearch + 1):
            #toSleep = 10
            #print "sleeping for " + str(toSleep) + " seconds in a pathetic attempt to bypass Google...."
            #time.sleep(toSleep)
            print "Searching on date " + dateToSearch.strftime("%m/%d/%Y") + " (day " + str(daysToGoBack) + " of " + str(daysToSearch) + ")"
            
            try:
                julianDate = trunc(sum(jdcal.gcal2jd(dateToSearch.year, dateToSearch.month, dateToSearch.day)) + .5)
                keyword = "investing"
                sites = ["http://online.wsj.com/", "http://www.bloomberg.com/news/", "http://www.marketwatch.com/", "http://www.rttnews.com/", "http://www.reuters.com/finance",  "http://www.usatoday.com/", "money.usnews.com", "www.ft.com/home/us", "http://www.cnbc.com/" ]
                query = "site:money.cnn.com"
                for site in sites:
                    query = query + " OR site:" + site
                query = query + " " + keyword + " daterange:" + str(julianDate) + "-" + str(julianDate);
                print "Query: " + query;
                query = quote_plus(query)
                #gs = GoogleSearch(query);
                #gs.results_per_page = 50
                #results = gs.get_results()
                headers={'User-agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6'}
                startPageQuery = "https://startpage.com/do/search?cat=web&cmd=process_search&language=english&engine0=v1all&abp=1&x=-843&y=-302&prfh=lang_homepageEEEs%2Fair%2Feng%2FN1Nenable_post_methodEEE0N1NsslEEE1N1Nfont_sizeEEEmediumN1Nrecent_results_filterEEE1N1Nlanguage_uiEEEenglishN1Ndisable_open_in_new_windowEEE1N1Nnum_of_resultsEEE50N1N&suggestOn=0&query=" + query
                #request = urllib2.Request('GET', startPageQuery, None, headers)
                request = urllib2.Request(url=startPageQuery, data=None, headers=headers)
                f = urllib2.urlopen(request)
                resultsPage = f.read()
                #print resultsPage
                f.close()
                soup = BeautifulSoup(resultsPage)
                resultDivs = soup.findAll("div", { "class" : "result" })
                results = []
                for resultDiv in resultDivs:
                    if ('none' in resultDiv.get('class')):
                        continue
                    h3 = resultDiv.find("h3")
                    url = h3.find("a", href=True)['href']
                    results.append(url)
            except SearchError, e:
                print "Search failed: %s" % e
                continue
            #Crawl to each web site and extract web articles
            try:
                global numberOfArticlePages
                numberOfArticlePages = 0
                articlePages = []
                articles = []
                articleURLs = []
                global total
                total = len(results)
                def fetch(url):
                    #request = urllib2.Request(url)
                    #f = urllib2.urlopen(request)
                    articles.append(webarticle2text.extractFromURL(url, timeout=60))
                    articleURLs.append(url)
                    #f.close()
                    print "\r" + str(len(articles)) + " / " + str(len(results)) + " articles crawled to.",
                    sys.stdout.flush()
                    #response = requests.request('GET', url, hooks = {'response' : do_something}, timeout=60.0)
                    #articlePages.append(response)
            
                pool = Pool(50)
                for res in results:
                    pool.spawn(fetch, res)
                pool.join()
                del pool
                # I was using grequests, but it appeared that they were leaking file descriptors... :(
                #articleRequests = (grequests.get(res, hooks = {'response' : do_something}, timeout=60) for res in results)
                #articlePages = grequests.map(articleRequests)
                print
            except gevent.Timeout:
                if (numberOfArticlePages >= len(results) * MIN_ARTICLES_PERCENT):
                    print ("Timeout, but continuing because we have " + str(numberOfArticlePages) + " articles.")
                else:
                    print ("Timeout, going to next day because we have only " + str(numberOfArticlePages) + " articles.")
                    continue
            '''articles = []
            articleURLs = []
            for articlePage in articlePages:
                if (articlePage is not None):
                    articles.append(webarticle2text.extractFromHTML(articlePage.text))
                    articleURLs.append(articlePage.url)
            '''
            print "All articles (" + str(len(articles)) + " of 'em) for date " + dateToSearch.strftime("%m/%d/%Y") + " returned, now being analyzed..."

            i = 1
            self.threads = []
            mutex_writefile = threading.Lock()
            #for res in results:
            for articleText, articleURL in zip(articles, articleURLs):
                #articleURL = res.url.encode("utf8")
                thread = SentimentThread(articleURL, articleText, i, fileName, dateToSearch, mutex_writefile, datum_box, "127.0.0.1:8118", self)
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                i = i + 1
                if (len(self.threads) >= MAX_THREADS):
                    for thread in self.threads:
                        thread.join()
            for thread in self.threads:
                        thread.join()
            self.articlesCompleted = 0
            if (dbError == True):
                dbError = False
                userNumber = userNumber - 1
                if (userNumber <= 0):
                    print("Out of Users")
                    return
                API_Key = getAPIKey(userNumber)
                datum_box = DatumBox(API_Key) 
                continue
                    
            dateToSearch = dateToSearch - timedelta(1)
            daysToGoBack += 1
        sentimentsFile.close()
    def killThreads(self):
        pass
        #for thread in self.threads:
            #   thread.stop()
    ''' End of Crawl Class ''' 
def getProxies(fileName):
    f = open(fileName, 'r')
    global proxies
    proxies = {}
    i = 0
    for line in f:
        proxy = line.strip()
        proxies[proxy] = 0
        i = i + 1
        if (i >= MAX_PROXIES):
            break
    f.close()
def main():
    year = 2012
    month = 2
    day = 3
    daysToSearch = 300
    userNumber = 13
    fileName = "newarticlesentiments.psv"
    #API_Key = getAPIKey(userNumber)
    #datum_box = DatumBox(API_Key)  
    #print "analysis: " + str(datum_box.sentiment_analysis("test"));
    if (len(sys.argv) != 7):
        print "usage: ./<name> <user_number> <year_to_start_search> <month_to_start_search> <day_to_start_search> <days_to_search> <output_file_name>"
        print "Note that search goes backwards in time each day for <days_to_search> days or until API calls are exhausted"
        delay = 0
        print "Now running with default values in " + str(delay) + " seconds"
        time.sleep(delay);
    else:
        userNumber = int(sys.argv[1])
        year = int(sys.argv[2])
        month = int(sys.argv[3])
        day = int(sys.argv[4])
        daysToSearch = int(sys.argv[5])
        fileName = sys.argv[6]
    print "\tRunning with values: user_number: " + str(userNumber) + ", year: " + str(year) + ", month: " + str(month) + ", day: " + str(day) + ", days to search: " + str(daysToSearch) + ", file name: " + fileName
    
    getProxies("united_states_proxies.txt")
    crawler = Crawler()
    crawler.crawl(userNumber, datetime(year, month, day, 12, 0, 0, 0), daysToSearch, fileName)

if __name__ == "__main__":
    main()