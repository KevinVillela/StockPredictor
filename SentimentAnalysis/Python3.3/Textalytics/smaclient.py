#smaclient.py -- wrap classes around the textalytics.com API 
#                and the returned results
# 
# @version    -- 1.0 
# @author     -- cdepablo 
# @contact    -- http://www.textalytics.com (http://www.daedalus.es)
# @copyright  -- Copyright (c) 2013, DAEDALUS S.A. All rights reserved.


import urllib.request, urllib.parse, urllib.error
import http.client
import json
import simplejson

from Textalytics.config import PROTOCOL,HOST,SERVICE_ENDPOINT;

class SmaClient:
	'textalytics.com Social Media Analysis client in Python'


	def __init__(self, key):
		self.key = key
		self.input  = "json" # JSON input and output are used
		self.output = "json"
		self.fields = ""    # By default, include all fields

	def analyze(self, document):
		"Returns the analyisis of the text or None if there is an error"
		params = urllib.parse.urlencode({
				'key': self.key,
				'input': self.input,
				'output': self.output,
				'fields': self.fields,
				'doc': document.toJson()})

		if (PROTOCOL == 'https'): 
			connection = http.client.HTTPSConnection(HOST)
		else: 
			connection = http.client.HTTPConnection(HOST)

		# connection.set_debuglevel(5)
		connection.request('POST',SERVICE_ENDPOINT,params)

		response = connection.getresponse()
		if (response.status == 200):
			encoding = response.headers.get_content_charset()
			#response_text = json.loads(response.read().decode('unicode_escape'))
			response_text = simplejson.loads(response.read().decode('unicode_escape'))
			#response_text = json.load(response)
			return Response(response_text)
		else:
			encoding = response.headers.get_content_charset()
			#r = json.loads(response.read().decode('unicode_escape'))
			r = simplejson.loads(response.read().decode('unicode_escape'))
			#r = json.load(response)
			error = Error(r["status"]["code"],r["status"]["message"],r["status"]["moreInfo"] )
			print(("Server returned: " + str(response.status)))
			return error



class Document:
        "Wrap a document information included in textaytics.com requets. Id and text are required values"

        def __init__(self,id,txt):
                self.id = id
                self.txt = txt

        def __str__(self):
                "Help  with printing"
                return self.id + " "  + self.txt

        def toJson(self):
                return '{ "document":' + json.dumps(self.__dict__, ensure_ascii=False) + '}'


class Response:
  	"Wrap the response from textanalytics Social Media Analysis API. include status and the extracted contents"
  	def __init__(self, d):
        	for a, b in list(d.items()):
            		if isinstance(b, (list, tuple)):
               			setattr(self, a, [Response(x) if isinstance(x, dict) else x for x in b])
            		else:
               			setattr(self, a, Response(b) if isinstance(b, dict) else b)
	
class Error:
        "Wrap error conditions"
        def __init__(self, code, message, moreInfo):
                self.code = code
                self.message = message
                self.moreInfo = moreInfo
                
        def __str__(self):
                return "Error: [\ncode: " + self.code + "\nmessage: " + self.message + "\nmore info: " +  self.moreInfo + "\n]"; 

