'''
Created on Dec 18, 2013

@author: KevinVillela
'''
import threading
import socket
from http.client import BadStatusLine
import urllib.request, urllib.error, urllib.parse
from DatumBox import DatumBoxError 
import sys # for sys.exit()
class SentimentThread(threading.Thread):
    def __init__(self, article, articleNumber, datum_box, proxy, parent=None, keyword="",sentimentsFileName="", dateToSearch=None, mutex_writefile=None, subscriptionID = None):
        super(SentimentThread, self).__init__()
        self.article = article
        self.articleNumber = articleNumber
        self.sentimentsFileName = sentimentsFileName
        self.dateToSearch = dateToSearch
        self.mutex_writefile = mutex_writefile
        self.datum_box = datum_box
        self.proxy = proxy
        self.parent = parent
        self.MAX_TRIES = 7
        self.MAX_STRIKES = 3
        self.separator = '|'
        self.subscriptionID = subscriptionID
        self.keyword = keyword
    def run(self):
        sentiment = self.getSentimentOfArticle()
        if sentiment == "-1" or sentiment == "0" or sentiment == "1":
            self.writeSentiment(sentiment)
    def stop(self):
        print("Thread stopping...")
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
        for tid, tobj in list(threading._active.items()):
            if tobj is self:
                self._thread_id = tid
                return tid
        # TODO: in python 2.6, there's a simpler way to do : self.ident

        raise AssertionError("could not determine the thread's id")
    def getSentimentOfArticle(self):
        tries = 0
        sentiment = ""
        while (tries < self.MAX_TRIES):
            try:
                sentiment = self.datum_box.sentiment_analysis(self.article.getText(), self.proxy, self.subscriptionID)
                break;
            except socket.timeout:
                print(("\t ^^Article #" + str(self.articleNumber) + " timed out " + str(tries + 1) + " time(s)..."))
                tries = tries + 1     
            except DatumBoxError as datumBoxError:
                if (datumBoxError.error_code == 11):
                    print("Daily DatumBox Limit Reached for API KEY " + self.datum_box.api_key)
                elif (datumBoxError.error_code == 4):
                    print("DatumBox received an unexpected error. Its okay though. Continuing normally.")
                    tries = tries + 1
                    continue
                else:
                    print("Datum Box received error code " + str(datumBoxError.error_code) + ", meaning: " + datumBoxError.error_message)   
                self.parent.articleAnalyzed(False)
                self.parent.killThreads()
                return    
            except urllib.error.URLError as error:
                print("url error " + str(error));
                if (error.errno == 60): #Operation timed out
                    print(("Operation timed out, likely due to the proxy.(Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1)  + ")"))
            except socket.error as error:
                print("socket error " + str(error));
                if (error.errno == 54): #Connection reset by peer
                    print(("Connection reset by peer. ugh. Trying again. (Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1) + ")"))
                    tries = tries + 1 
            except BadStatusLine:
                print(("Could not get article: BadStatusLine. (Article #" + str(self.articleNumber) + ", attempt #" + str(tries + 1) + ")"))
                continue
            except SystemExit:
                print('An exception flew by!')
        if ( tries == self.MAX_TRIES):
            return -100   
        return sentiment
         
    def writeSentiment(self, sentiment):
        self.mutex_writefile.acquire()
        sentimentsFile = open(self.sentimentsFileName, 'a')
        sentimentsFile.write(self.article.URL + self.separator)
        sentimentsFile.write(self.dateToSearch.strftime("%m/%d/%Y") + self.separator)
        sentimentsFile.write(str(sentiment) + self.separator);
        sentimentsFile.write(self.keyword + self.separator);
        sentimentsFile.write(str(self.article.rank))
        try:
            for paragraph in self.article.paragraphs:
                sentimentsFile.write("|" + paragraph)
        except Exception as e:
            print("printing error")
        sentimentsFile.write("\n")
        sentimentsFile.close()
        self.mutex_writefile.release()
        self.parent.articleAnalyzed(True)