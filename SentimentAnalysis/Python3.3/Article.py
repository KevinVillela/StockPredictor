'''
Created on Feb 21, 2014

@author: KevinVillela
'''

class Article(object):
    def __init__(self, paragraphs, URL, rank, sentiment = 0):
        self.paragraphs = paragraphs
        self.URL = URL
        self.rank = rank
        self.sentiment = sentiment
    
    def getText(self):
        text = ""
        for paragraph in self.paragraphs:
             text += paragraph + "\n"
        return text
        