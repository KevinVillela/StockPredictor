StockPredictor
==============

A Python script to analyze the sentiment of the news.

To run this script, you must first install the following dependencies:

jdcal (pip install jdcal)
BeautifulSoup (pip install beautifulsoup4)
lxml (used by jusText. pip install lxml. In case of a can't find *.bat error, install compiled binaries from wwww.lfd.uci.edu/~gohlke/pythonlivs/#lxmll)
jusText 
	([sudo] pip install justext
	or [sudo] pip install git+git://github.com/miso-belica/jusText.git, 
	if not then https://pypi.python.org/pypi/jusText/2.0.0.
	Alternative: download the ZIP file and run pip install -r requirements.txt in the unzipped directory)
requests (pip install requests)
tor (go to their project page and make sure a circuit is established)
privoxy (go to their project page and make sure it is working, then chain it with tor. The project page has instructions for this as well)
stem (pip install stem)
chardet (pip install chardet)

Privoxy and Tor must be changed to make web queries anonymous.
webarticle2text is now included in the project files, but is no longer used.

Installation instructions for Windows:

Download and install git
Add git to your path (On Windows 7: Start -> Edit Environment Variables or SET PATH=%PATH%;/path/to/git)
Clone this repository
Download and install Python3.3
Download and install Setuptools (Download ez_setup.py and run it with python ez_setup.py)
Add Scripts to your PATH 
Download and install pip for Python3.3 (wwww.lfd.uci.edu/~gohlke/pythonlivs/#pip)
Add pip to your PATH
Run the linux commands above for downloading dependencies with pip
cd into the directory StockPredictor/SentimentAnalysis
run python Python3.3/main.py <user_number> <year_to_start_search> <month_to_start_search> <day_to_start_search> <days_to_search> <output_file_name>")

Note that from July 22nd, 2011 (7/22/2011 closing: 12681) to November 16th, 2012 (11/16/2012 closing: 12588), the DOW made a total change of -93 points. 
Therefore, we choose this time period to test our data. This is a time period of 483 days. We change this later.

HYPOTHESES FOR DATA SETS:

When collecting data, our Keyword of DOW was returning articles that had the word "DOW" in the footnotes, which was fairly common. 
It was also not acquiring very many articles for dates too far in the past (> 1.5 years or so. The farther back, the worse it got).
Therefore, we changed our query to one that contained a few of the top companies in the DOW Stock Index: 
"Boeing OR Caterpillar OR McDonalds OR Microsoft OR Nike OR Coca-Cola OR Visa OR Wal-Mart OR Disney OR Verizon OR Exxon OR IBM OR JPMorgan OR Intel"

We found a %75 correlation in some data using the above multiple keywords and a time period of:
October 14, 2011 to May 12, 2012. This is a time period of 211 days. It was chosen because the DOW doesn't rise or fall much between these dates.
These findings were very encouraging, so we decided to acquire more data. 
Unfortunately, when acquiring data from December 20th, 2013 (the current date) to May 12, 2012, it did not fit the previous correlation.
We think this may be because the distribution of news sources between the two data sets are vastly different:
				early (good)	later (bad) 
money.cnn.com:	.1521			.0695
bloomberg.com	.6083			.1123
usnews.com		.0377			.0129
cnbc.com		.1461			.3675
usatoday.com	.0230			.3293
other			.0328			.1085

On further review of usatoday's articles, their majority were about sports and topics largely unrelated to the stock market.
After removing usatoday's articles from the early (good) data set, we saw an increase in correlation by 1%. 
However, removing usatoday's articles from the later (bad) data set made the data much worse. This could be due to deleting almost %33 of the data set.
Therefore, we retried the bad data set search without usatoday.com in the query.
After about 120 days, the data gave us a worse correlation, but still a very good one at about %50. However, since the correlation dropped so much with the addition of only about 40 data points, more data must be inserted.
After gathering data from May 12, 2012 to December 20th, 2013, we found that the more data you add, the lower the correlation becomes.

In an attempt to discover the driving force behind the sentiment->market correlation, we decided to test each news source individually by using only their articles from the data set.
This gave us the following table or maximum correlations:
				early (good)	total (good and bad)
money.cnn.com:	.06				59.9
bloomberg.com	.07				55.8
cnbc.com		.226			66.5

Because of cnbc's supposed influence on the result, we decided to gather data for cnbc only. 
However, if we did this with the current query of a few DOW Jones sites, we would likely not get enough data.
Therefore, we gathered data from CNBC only and included ALL of the companies in the DOW in our query.
Finally, we also realized that some websites were returning no text at all; or, more specifically, the justext module was not finding any article text in the websites. We removed these few occurrences from the analysis.
After gathering data for cnbc from December 20th, 2013 to October 14, 2011, using every company in the DOW as the query, we found a terrible correlation. This didn't work at all. The data is stored in Current-All-CNBC.psv.

After this, we tried all the companies but with all the websites except for usatoday.
For some reason, about halfway through this query, we began getting a 414 error: URI too long. Further investigation revealed that Google limits the search terms to 32 characters.
This meant that the previous query was getting cut off after the 2nd Johnson in "Johnson and Johnson".  In order to complete this test, the query was cut off before "Johnson and Johnson". Data from December 20,2013 to October 15, 2011 showed no correlation.

This test also came up with a way to test our variables: using test dates. We use the following as test dates:
April 12, 2012: As the DOW drops sharply after this until about June 1, 2012.
December 28, 2012: As the DOW rises sharply after this until about February 1st and continues to rise slowly afterwards.
January 25, 2013: As the DOW stays very similar between then and March 1, 2013

Using these test dates and the query DOW, we came up with:
DOW Drop after April 12 2012 -> 1.38 average sentiment over X days
DOW rise after December 28 2012 -> -4.69 average sentiment over X days
DOW steady after January 25 2013 -> -2.02 average sentiment over X days
These results were encouraging, so we gathered data from December 1, 2013, back.
From then to December 1, 2013, the data had an R squared value of .42 with 23 days back and 25 days forward. Adding more data before that dropped the correlation, but this could be because the number of articles found dropped as well.
Therefore, we gathered the most recent data we could at the time to see if the correlation would be helped. After gathering data from December 13th, 2013, back, the correlation decreased to .35.

Now, we are going to try getting every article from the above web sites without any keywords, but the results for the test days were poor.
