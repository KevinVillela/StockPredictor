#from urllib2 import Request, ProxyHandler
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlencode
import json
import pprint
import socks
import socket

class DatumBox():
	
	base_url = "http://api.datumbox.com/1.0/"
	
	def __init__(self, api_key):
		self.api_key = api_key
		
	def sentiment_analysis(self, text, proxy, subscriptionID = None):
		"""Possible responses are "positive", "negative" or "neutral" """
		return self._classification_request(text, "SentimentAnalysis", proxy, subscriptionID)

	
	def twitter_sentiment_analysis(self, text):
		"""Possible responses are "positive", "negative" or "neutral" """
		return self._classification_request(text, "TwitterSentimentAnalysis")

	
	def is_subjective(self, text):
		"""Returns boolean"""
		response = self._classification_request(text, "SubjectivityAnalysis")
		return response == "subjective"
	
	def topic_classification(self, text):
		"""Possible topics are "Arts", "Business & Economy", "Computers & Technology", "Health", "Home & Domestic Life", "News", "Recreation & Activities", "Reference & Education", "Science", "Shopping","Society" or "Sports"""
		return self._classification_request(text, "TopicClassification")
	
	def is_spam(self, text):
		"""Returns a boolean"""
		response = self._classification_request(text, "SpamDetection")
		return response == "spam"
	
	def is_adult_content(self, text):
		"""Returns a boolean"""
		response = self._classification_request(text, "AdultContentDetection")
		return response == "adult"
	
	def readability_assessment(self, text):
		"""Responses "basic", "intermediate" or "advanced" """
		return self._classification_request(text, "ReadabilityAssessment")
	
	def detect_language(self, text):
		"""Returns an ISO_639-1 language code"""
		return self._classification_request(text, "LanguageDetection")
	
	def is_commercial(self, text):
		"""Returns "commercial" or "noncommercial" """
		response = self._classification_request(text, "CommercialDetection")
		return response == "commercial"
	
	def is_educational(self, text):
		"""Returns boolean"""
		response = self._classification_request(text, "EducationalDetection")
		return response == "educational"
	
	def keyword_extract(self, text):
		"""Returns a list of keywords from the given text"""
		full_url = DatumBox.base_url + "KeywordExtraction.json"
		response = self._send_request(full_url, {'text' : text, 'n' : 1})
		return list(response['1'].keys());
	
	def text_extract(self, text):
		"""Extracts text from a webpage"""
		return self._classification_request(text, "TextExtraction")
		
	def document_similarity(self, text, text2):
		"""Returns number between 0 (No similarity) and 1(Exactly equal)"""
		full_url = DatumBox.base_url + "DocumentSimilarity.json"
		response = self._send_request(full_url, {'original': text, 'copy' : text2})
		return response['Oliver'];
	
	def _classification_request(self, text, api_name, proxy, subscriptionID):
		full_url = DatumBox.base_url + api_name + ".json"
		
		data = {'text' : text}
		if (subscriptionID is not None): #UGH THIS IS A HACK GET OVER IT
			data = {'text' : text, 'subscription_id' : subscriptionID} 
		return self._send_request(full_url, data, proxy)
		
	def _send_request(self, full_url, params_dict, proxy):
		params_dict['api_key'] = self.api_key
		if (params_dict.get('subscription_id') is None) and (proxy != ""): # If we don't get the 10k requests, use a proxy
			proxy_support = urllib.request.ProxyHandler({'http': '127.0.0.1:8118'})
			opener = urllib.request.build_opener(proxy_support, urllib.request.HTTPHandler(debuglevel=0))
			urllib.request.install_opener(opener)
			#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8118)
			#socket.socket = socks.socksocket
		else:
			proxy_support = urllib.request.ProxyHandler({})
			opener = urllib.request.build_opener(proxy_support, urllib.request.HTTPHandler(debuglevel=0))
		
		headers={'User-agent' : 'Mozilla/5.0', 'Connection':'close'}
		binary_data = urlencode(params_dict).encode('utf-8') 
		request = urllib.request.Request(url=full_url, data=binary_data, headers=headers)
		f = opener.open(request)
		response = json.loads(f.read().decode('utf-8'))
		f.close()
		return self._process_result(response)
		
	def _process_result(self, response):		
		if "error" in response['output']:
			raise DatumBoxError(response['output']['error']['ErrorCode'], response['output']['error']['ErrorMessage'])
		else:
			return self.sentimentToNumber(response['output']['result'])	
	def sentimentToNumber(self, sentiment):
		if (sentiment == "neutral"):
			return "0"
		elif (sentiment == "negative"):
			return "-1"
		elif (sentiment == "positive"):
			return "1"
		else:
			return "999999"
		
class DatumBoxError(Exception):
	def __init__(self, error_code, error_message):
		self.error_code = error_code
		self.error_message = error_message



	def __str__(self):
		return "Datumbox API returned an error: " + str(self.error_code) + " " + self.error_message
		
		
	
