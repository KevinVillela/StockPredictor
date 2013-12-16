'''
Created on Dec 1, 2013

@author: KevinVillela
'''
def getBaseURL(startDate):
    return "http://www.latimes.com/search/dispatcher.front?Query=finance&target=adv_article&date=" + startDate.strftime("%m/%d/%Y-%m/%d/%Y") + "&sortby=contentrankprof"
def sentimentToNumber(sentiment):
    if (sentiment == "neutral"):
        return "0"
    elif (sentiment == "negative"):
        return "-1"
    elif (sentiment == "positive"):
        return "1"
    else:
        return "999999"
def getAPIKey(user_number):
    return {
            1 : "a01778a8cafdedfc2e676b8ba0495a19", # API KEY for KVillela
            2 :  "6193d654c5eebe977005717702592f26", # API KEY for KevinV
            3 : "aafd2b194cfbe927cb85c4e1fc579141", # API KEY for villka02
            4 : "c15e170662def9c247a0d074f01f0222", # API KEY for MrMAV
            }[user_number]
USER_NUMBER = 4
API_KEY = getAPIKey(USER_NUMBER)
MAX_TRIES = 7
seperator = "|"
from DatumBox import DatumBox
from bs4 import BeautifulSoup
import webarticle2text
import urllib
import socket
import threading
from datetime import date, timedelta, datetime
from xgoogle.search import GoogleSearch, SearchError

datum_box = DatumBox(API_KEY) 
try:
    keyword = "investing"
    sites = ["http://online.wsj.com/public/page/news-business-us.html", "http://www.bloomberg.com/news/economy/", "http://www.marketwatch.com/", "http://www.rttnews.com/list/us-economic-news.aspx", "http://www.reuters.com/finance",  "http://www.usatoday.com/money/", "money.usnews.com", "www.ft.com/home/us", "http://www.cnbc.com/" ]
    query = "money.cnn.com"
    for site in sites:
        query = query + " OR site:" + site
    qeury = query + " " + keyword + "daterange:";
    gs = GoogleSearch(query);#"investing daterange:2456294-2456294")
    gs.results_per_page = 50
    results = gs.get_results()
    for res in results:
        print res.title.encode("utf8")
        print res.desc.encode("utf8")
        print res.url.encode("utf8")
        print
except SearchError, e:
  print "Search failed: %s" % e
def getSentimentOfArticle(articleURL, articleNumber, sentimentsFileName, dateToSearch, mutex_writefile):
    tries = 0
    sentiment = ""
    print "\tArticle #" + str(articleNumber) + " for date " + dateToSearch.strftime("%m/%d/%Y") + " being analyzed..."
    while (tries < MAX_TRIES):
        try:
            sentiment = sentimentToNumber(datum_box.sentiment_analysis(webarticle2text.extractFromURL(articleURL)))
            break;
        except socket.timeout:
            print("\t ^^Article #" + str(articleNumber) + " timed out " + str(tries + 1) + " time(s)...")
            tries = tries + 1
    if ( tries == MAX_TRIES):
        return
    mutex_writefile.acquire()
    sentimentsFile = open(sentimentsFileName, 'a')
    sentimentsFile.write(articleURL + seperator)
    sentimentsFile.write(dateToSearch.strftime("%m/%d/%Y") + seperator)
    sentimentsFile.write(sentiment);
    sentimentsFile.write("\n")
    sentimentsFile.close()
    mutex_writefile.release()
            
def crawl(dateToSearch, daysToSearch, fileName):
    'dateToSearch = date(2013, 8, 30)'
    sentimentsFile = open(fileName, "a")
    for daysToGoBack in range(1, daysToSearch + 1):
        print "Searching on date " + dateToSearch.strftime("%m/%d/%Y") + " (day " + str(daysToGoBack) + " of " + str(daysToSearch) + ")"
        url = getBaseURL(dateToSearch)
        try:
            f = urllib.urlopen(url)
        except socket.timeout:
            daysToGoBack = daysToGoBack - 1
            continue
        myfile = f.read()
        f.close()
        soup = BeautifulSoup(myfile)
        mydivs = soup.findAll("div", { "class" : "result" })
        i = 1
        threads = []
        mutex_writefile = threading.Lock()
        for each_div in mydivs:
            articleURL = each_div.find("a", href=True)['href']
            if (articleURL[0] == '/'):
                articleURL = "http://www.latimes.com" + articleURL
            thread = threading.Thread(target=getSentimentOfArticle, args=(articleURL, i, fileName, dateToSearch, mutex_writefile))
            thread.start()
            threads.append(thread)
            i = i + 1
        for thread in threads:
            thread.join()
        dateToSearch = dateToSearch - timedelta(1)
    sentimentsFile.close()
''' End of crawling '''    
    
#crawl(date(2013, 1, 16), 16, "articlesentiments.psv")