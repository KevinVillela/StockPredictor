'''
Created on Feb 21, 2014

@author: KevinVillela
'''
''' These methods fetch an article and then ensures that
    it meets our requirements for articles we want to keep.
'''
import requests
import justext
import Article
import sys
def fetch(keyword, url, rank, articles, totalNumber):
    searchKeywords = keyword.split('" OR "') # We are going to check the article text for our keywords after being run through JusText
    response = requests.get(url)
    paragraphs = justext.justext(response.text, justext.get_stoplist("English"))
    empty = True
    containsKeyword = False
    minMentions = 3
    mentions = 0
    searchKeyword = searchKeywords[0].replace('"', '').strip().split(' ', 1)[0] # Get the first word of the search term
    articleParagraphs = []
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            if searchKeyword in paragraph.text:
                mentions += 1 #paragraph.text.count(searchKeyword)
                articleParagraphs.append(paragraph.text)
    if (mentions < minMentions):
        #print("A website (" + url + ") did not have the keyword enough times! Removed.")
        return
    '''for searchKeyword in searchKeywords:
        searchKeyword = searchKeyword.replace('"', '').strip().split(' ', 1)[0] # Get the first word of the search term
        if searchKeyword in article:
            containsKeyword = True
            break
    if (containsKeyword == False):
        print("A website (" + url + ") does not contain the keyword! Removed.")
        return '''
    articles.append(Article.Article(articleParagraphs, url, rank))
    print("\r" + str(len(articles)) + " / " + str(totalNumber) + " articles crawled to for keyword " + keyword, end=' ')
    sys.stdout.flush() 