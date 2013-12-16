'''
Created on Dec 15, 2013

@author: KevinVillela
'''
'''def oldGetSentimentOfArticle(articleURL, articleNumber, sentimentsFileName, dateToSearch, mutex_writefile, datum_box):
    tries = 0
    sentiment = ""
    while (tries < MAX_TRIES):
        try:
            urlText = webarticle2text.extractFromURL(articleURL)
            print "\tArticle #" + str(articleNumber) + " for date " + dateToSearch.strftime("%m/%d/%Y") + " returned, now being analyzed..."
            sentiment = datum_box.sentiment_analysis(urlText)
            break;
        except socket.timeout:
            print("\t ^^Article #" + str(articleNumber) + " timed out " + str(tries + 1) + " time(s)...")
            tries = tries + 1     
        except DatumBoxError, datumBoxError:
            if (datumBoxError.error_code == 11):
                print "Daily DatumBox Limit Reached for API KEY " + datum_box.api_key
                mutex_writefile.acquire()
                global dbError
                dbError = True
                mutex_writefile.release()
                return       
                
    if ( tries == MAX_TRIES):
        return
    mutex_writefile.acquire()
    sentimentsFile = open(sentimentsFileName, 'a')
    sentimentsFile.write(articleURL + seperator)
    sentimentsFile.write(dateToSearch.strftime("%m/%d/%Y") + seperator)
    sentimentsFile.write(sentiment);
    sentimentsFile.write("\n")
    sentimentsFile.close()
    global numberOfArticlesToday
    numberOfArticlesToday = numberOfArticlesToday + 1
    mutex_writefile.release()
'''
'''
 #For each article text, get its sentiment using a proxy
 sentimentRequests = []
 proxyIterator = proxies.iterkeys()
 proxyIterator.next()
 i = 1
 mutex_writefile = threading.Lock()
 threads = []
 for article, url in articles, urls:
     
     params_dict = {'text' : article}
     #params_dict['api_key'] = API_Key
     try:
         proxy = proxyIterator.next()
     except StopIteration:
         proxyIterator = proxies.iterkeys()
         proxy = proxyIterator.next()
     getSentimentOfArticle(url, article, i, fileName, dateToSearch, mutex_writefile, datum_box):
     i = i + 1
 sentiments = grequests.map(sentimentRequests)
 for sentiment in sentiments:
     print sentiment.content
'''