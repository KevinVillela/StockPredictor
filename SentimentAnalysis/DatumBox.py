#from urllib2 import Request, ProxyHandler
import urllib2
from urllib import urlencode
import json
import socket

class DatumBox():
	
	base_url = "http://api.datumbox.com/1.0/"
	
	def __init__(self, api_key):
		self.api_key = api_key
		
	def sentiment_analysis(self, text, proxy):
		"""Possible responses are "positive", "negative" or "neutral" """
		return self._classification_request(text, "SentimentAnalysis", proxy)

	
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
		return response['1'].keys();
	
	def text_extract(self, text):
		"""Extracts text from a webpage"""
		return self._classification_request(text, "TextExtraction")
		
	def document_similarity(self, text, text2):
		"""Returns number between 0 (No similarity) and 1(Exactly equal)"""
		full_url = DatumBox.base_url + "DocumentSimilarity.json"
		response = self._send_request(full_url, {'original': text, 'copy' : text2})
		return response['Oliver'];
	
	def _classification_request(self, text, api_name, proxy):
		full_url = DatumBox.base_url + api_name + ".json"
		return self._send_request(full_url, {'text' : text}, proxy)
		
	def _send_request(self, full_url, params_dict, proxy):
		params_dict['api_key'] = self.api_key
		proxy_support = urllib2.ProxyHandler({'http': 'http://' + proxy})
		headers={'User-agent' : 'Mozilla/5.0', 'Connection':'close'}
		opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler(debuglevel=0))
		urllib2.install_opener(opener)
		request = urllib2.Request(url=full_url, data=urlencode(params_dict), headers=headers)
		f = urllib2.urlopen(request)
		response = json.loads(f.read())
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
		
		
	
