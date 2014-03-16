'''
Created on Feb 21, 2014

@author: KevinVillela
'''
import unittest
import FetchArticle
import Article
import os
import csv
from textblob import TextBlob
import random
from DatumBox import DatumBox
from SentimentThread import SentimentThread
from TorThread import TorThread
import Textalytics.smaclient
import Textalytics.myclient

class Test(unittest.TestCase):

    def main(self):
        sentimentAnalysisTest()
    def getArticlesFromTSV(self, fileName):
        fileName = os.path.join(os.path.dirname(__file__), "../", fileName)
        tempArticles = []
        articles = []
        with open(fileName, 'r', encoding='utf-8') as csvFile:
            defaultParametersFileReader = csv.reader(csvFile, delimiter='\t')
            for row in defaultParametersFileReader:
                article = Article.Article("", row[0], -1,row[2])
                FetchArticle.fetch("\"" + row[3] + "\"", article.URL, article.rank, tempArticles, 0)
                article.paragraphs = [tempArticles[0].text]
                tempArticles = []
                articles.append(article)
            csvFile.close()
            return articles
        
    def getArticlesFromPSV(self, fileName):
        fileName = os.path.join(os.path.dirname(__file__), "../", fileName)
        tempArticles = []
        articles = []
        with open(fileName, 'r', encoding='utf-8') as csvFile:
            defaultParametersFileReader = csv.reader(csvFile, delimiter='|')
            for row in defaultParametersFileReader:
                paragraphs = []
                for i in range(1, len(row)):
                    paragraphs.append(row[i])
                article = Article.Article(paragraphs, row[0], -1,row[2])
                #FetchArticle.fetch(row[3], article.URL, article.rank, tempArticles, 0)
                tempArticles = []
                articles.append(article)
            csvFile.close()
            return articles
        
    def fetchArticleTest(self):
        articles = []
        FetchArticle.fetch("\"AT&T Inc\"", "http://www.bloomberg.com/news/2012-11-29/cox-considers-buying-business-services-to-step-up-at-t-challenge.html", 1,articles,1)
        if not articles:
            self.fail("Article contained keyword but was not saved")
        FetchArticle.fetch("\"AT&T Inc\"", "http://www.bloomberg.com/news/2012-11-29/cox-considers-buying-business-services-to-step-up-at-t-challenge.html", 1,articles,1)
        if articles:
            self.fail("Article did not contain keyword but was saved")

    def test_sentimentAnalysisTest(self):
        articles = self.getArticlesFromPSV("ProductData/3MentionMinimum.psv")
        self.runControlSentimentAnalysis(articles)
        #self.runTextBlobSentimentAnalysis(articles)
        #self.runTextBlobSentimentAnalysisByParagraph(articles)
        #self.runTextalyticsSentimentAnalysis(articles)
        self.runDatumBoxSentimentAnalysis(articles)
        
    def runControlSentimentAnalysis(self, articles):
        numWrong = 0
        for article in articles:
            guessedSentiment = random.randint(-1,1)
            if int(article.sentiment) != int(guessedSentiment):
                numWrong += 1
        print("\nCONTROL: Correctly analyzed " + str(len(articles) - numWrong) + " out of " + str(len(articles)) + " articles.")
        
    def runTextalyticsSentimentAnalysis(self, articles):
        client = Textalytics.smaclient.SmaClient('480bfbfd0443ed56723d114d32a56dec')#('ce168f5cb99959451a1514b9a326afc7')
        numWrong = 0
        for article in articles:
            document = Textalytics.smaclient.Document("0", article.getText())
            document.language = "en"
            document.source = "UNKNOWN"
            document.itf = "txt"
            
            response = client.analyze(document)
            if (isinstance(response,Textalytics.smaclient.Response)):
                guessedSentiment = 0
                #if response.result.subjectivity == "OBJECTIVE" and response.result.score < .10 and response.result.score > .10:
                #    guessedSentiment = 0
                if response.result.sentiment == "P":
                    guessedSentiment = 1
                elif response.result.sentiment == "N":
                    guessedSentiment = -1
                #print(article.getText())
                print("Guess: " + response.result.sentiment + "=" + str(guessedSentiment) + ", actual: " + str(article.sentiment))
                if int(article.sentiment) != int(guessedSentiment):
                    numWrong += 1
                #Textalytics.myclient.printr(response.result)
            elif (isinstance(response,Textalytics.smaclient.Error)):
                print(response)
            else:
                print("Unknown error")
                    
        print("\TEXTALYTICS: Correctly analyzed " + str(len(articles) - numWrong) + " out of " + str(len(articles)) + " articles.")
    def runTextBlobSentimentAnalysisByParagraph(self, articles):
        numWrong = 0
        for article in articles:
            subjectivitySum = 0
            polaritySum = 0
            numOfParagraphs = 0
            for paragraph in article.paragraphs:
                #print(paragraph + "\n")
                blob = TextBlob(paragraph)
                tempSentiment = blob.sentiment;
                #print(paragraph + "\n" + str(tempSentiment.subjectivity) + "," + str(tempSentiment.polarity))
                polaritySum += tempSentiment.polarity
                subjectivitySum += tempSentiment.subjectivity
                numOfParagraphs += 1
            polarityAverage = polaritySum / numOfParagraphs
            subjectivityAverage = subjectivitySum / numOfParagraphs
            if subjectivityAverage <= .4:
                guessedSentiment = 0
            elif polarityAverage > .05:
                guessedSentiment = 1
            else:
                guessedSentiment = -1
            print("polarity: " + str(polarityAverage) + ", subjectivity: " + str(subjectivityAverage) + ", actual: " + article.sentiment)
            if int(article.sentiment) != int(guessedSentiment):
                numWrong += 1
        print("\nTEXTBLOB WITH PARAGRAPHS: Correctly analyzed " + str(len(articles) - numWrong) + " out of " + str(len(articles)) + " articles.")
        
    def runTextBlobSentimentAnalysis(self, articles):
        numWrong = 0
        for article in articles:                
            blob = TextBlob(article.getText())
            
            tempSentiment = blob.sentiment;
            #print(article.getText())
            #print(str(article.sentiment) + " " + str(blob.sentiment))
            if tempSentiment.subjectivity <= .4:
                guessedSentiment = 0
            elif tempSentiment.polarity > .05:
                guessedSentiment = 1
            else:
                guessedSentiment = -1
            if int(article.sentiment) != int(guessedSentiment):
                numWrong += 1
        print("\nTEXTBLOB: Correctly analyzed " + str(len(articles) - numWrong) + " out of " + str(len(articles)) + " articles.")
        
    def runDatumBoxSentimentAnalysis(self, articles):
        numWrong = 0
        #torThread = TorThread(self)
        #torThread.start()
        #time.sleep(5)
        datumBox = DatumBox("08fe94b761715219d636bd338b1cd984") 
        for article in articles:
            sentimentModule = SentimentThread(article=article,articleNumber=0, datum_box=datumBox, proxy="127.0.0.1:8118")
            guessedSentiment = sentimentModule.getSentimentOfArticle()
            #print(article.getText())
            print("Guess: " + str(guessedSentiment) + ", actual: " + str(article.sentiment))
            if int(article.sentiment) != int(guessedSentiment):
                numWrong += 1
        print("\nCorrectly analyzed " + str(len(articles) - numWrong) + " out of " + str(len(articles)) + " articles.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()