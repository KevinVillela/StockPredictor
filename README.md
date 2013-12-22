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

