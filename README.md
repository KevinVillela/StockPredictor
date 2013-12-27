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
urllib3
requests (pip install requests)
tor (go to their project page and make sure a circuit is established)
privoxy (go to their project page and make sure it is working, then chain it with tor. The project page has instructions for this as well)
stem (pip install stem)
chardet (pip install chardet)

Privoxy and Tor must be changed to make web queries anonymous.
webarticle2text is now included in the project files.

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
After gathering data from December 20th, 2013 to May 12, 2012, we found: 