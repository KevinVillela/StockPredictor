StockPredictor
==============

A Python script to analyze the sentiment of the news.

To run this script, you must first install the following dependencies:

jdcal (pip install jdcal)
BeautifulSoup (pip install beautifulsoup4)
jusText ([sudo] pip install git+git://github.com/miso-belica/jusText.git, if not then https://pypi.python.org/pypi/jusText/2.0.0)
urllib3
grequests (maybe. At the writing of this, it was not being used because of a potential memory leak - leaking file descriptors.)

Privoxy and Tor must be changed to make web queries anonymous.
webarticle2text is now included in the project files.

Installation instructions for Windows:

Download and install Python3.3
Download and install pip for Python3.3 (wwww.lfd.uci.edu/~gohlke/pythonlivs/#pip)
