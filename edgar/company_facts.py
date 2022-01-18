import requests
from bs4 import BeautifulSoup

class Financials():

    def __init__(self, ticker: str) -> None:

        # convert ticker to cik
        self.cik = self.tickerToCIK(ticker)
        self.ticker = ticker.upper()

        # validate cik (adds leading zeros)
        self.cik = self.validateCIK(self.cik)

        # setup base api url & endpoint
        self.api_resource = 'https://data.sec.gov'
        self.endpoint = f'/api/xbrl/companyfacts/CIK{self.cik}.json'

        # request the company facts and decode it
        self.companyFacts = requests.get(self.api_resource + self.endpoint, headers = { 'User-Agent': 'Sample Company Name AdminContact@<sample company domain>.com'}).json()
        # use case: self.companyfacts['facts']['us-gaap']['Goodwill] to access goodwill, etc...

    def tickerToCIK(self, ticker: str) -> str:
        # sec provided list of tickers : cik
        self.ticker_resource = 'https://www.sec.gov/include/ticker.txt'
        
        # request 
        self.tickersCIKList = requests.get(self.ticker_resource, headers = { 'User-Agent': 'Sample Company Name AdminContact@<sample company domain>.com'}).text.split()

        return self.tickersCIKList[self.tickersCIKList.index(ticker.lower()) + 1]
    
    def validateCIK(self, cik: str) -> str:
        # add leading zeros to cik if missing
        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros * "0" + cik
        return cik

    def getIncomeStatement(self) -> dict:
        return self.incomeStatement

    def getBalanceSheet(self) -> dict:
        return self.incomeStatement

    def getCashFlow(self) -> dict:
        return self.incomeStatement

    # https://data.sec.gov/api/xbrl/companyconcept/CIK0001326801/us-gaap/Goodwill.json
    # this gives us goodwill values (FB ex)

    # https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/InventoryNet.json
    # this gives us all Net Inventory Values (AAPL ex)