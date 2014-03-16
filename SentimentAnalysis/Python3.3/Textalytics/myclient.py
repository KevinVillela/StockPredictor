# myclient.py -- Simple client to use textalytics.com 
#                Social Media Analysis service 
# 
# @version    -- 1.0 
# @author     -- cdepablo 
# @contact    -- http://www.textalytics.com (http://www.daedalus.es)
# @copyright  -- Copyright (c) 2013, DAEDALUS S.A. All rights reserved.

import Textalytics.smaclient
import argparse


def main(key, text, fields):
    ''' Analyze a text and extract relevant fields. A usage key for textalytics.com is required '''
    client = smaclient.SmaClient(key)
    client.fields= fields
    document = smaclient.Document("0", text)
    document.language = "es"
    document.source = "UNKNOWN"
    document.itf = "txt"

    response = client.analyze(document)
    if (isinstance(response,smaclient.Response)):
        printr(response.result)
    elif (isinstance(response,smaclient.Error)):
        print(response)
    else:
        print("Unknown error")
        

def printr(result):
        ''' Print API call results '''
        if hasattr(result, 'sentiment'):
                print('\nSentiment')
                print(result.sentiment)

        if hasattr(result, 'categorization'):
                print('\nCategorization')
                for c in result.categorization:
                        print(' '.join((c.code, ' - '.join (c.labels), str(c.relevance))))

        if hasattr(result, 'entities'):
                print('\nEntities')
                for e in result.entities:
                        print(' '.join((e.form,'[',e.type, ','.join(e.variants), str(e.relevance),']')))
        
        if hasattr(result, 'concepts'):
                print('\nConcepts')
                for c in result.concepts:
                        print(' '.join((c.form,'[', ','.join(c.variants), str(c.relevance),']')))

        if hasattr(result, 'timeExpressions'):
                print('\nTime Expressions')
                for t in result.timeExpressions:
                        print(' '.join((t.form,'[', getattr(t,'time',''), getattr(t,'date',''), ']')))

        if hasattr(result, 'moneyExpressions'):
                print('\nMoney Expressions')
                for m in result.moneyExpressions:
                        print(' '.join((m.form, '[', getattr(m,'amount',''), getattr(m,'currency', ''), ']')))

        if hasattr(result, 'uris'):
                print('\nUris')
                for uri in result.uris:
                        print(' '.join((uri.form, uri.type)))

        if hasattr(result, 'phoneExpressions'):
                print('\nPhone Expressions')
                for p in result.phoneExpressions:
                        print(p.form)


if __name__ == "__main__":
    ''' Parse arguments and invoke textalytics.com service'''
    parser = argparse.ArgumentParser("Process a document with Textalytics.com Social Media Analytics")
    #parser.add_argument("key", help="service key")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to analyze")
    group.add_argument("--file", help="File with text to analyze")
    parser.add_argument("--fields", help="analysis fields to include in the output separated by commas")
    args = parser.parse_args()
    print('hi')
    text = None
    if args.text:
    	text = args.text
    if args.file:
    	text = open(args.file).read()
    
    print(text)
    
    if args.fields:
    	fields = args.fields.replace(',','|')	
    else:
    	fields=""

    main('480bfbfd0443ed56723d114d32a56dec', text, fields)
    #main(args.key,text,fields)
