import requests
from edgar.financial_statements import financial_statement as fS
from edgar.financial_statements import income_statement as iS
from edgar.financial_statements import balance_sheet as bS
from edgar.financial_statements import cash_flow as cF

HEADERS = { 'User-Agent': 'Sample Company Name AdminContact@<sample company domain>.com' }

class Financials():

    def __init__(self, ticker: str, period='annual') -> None:
        # convert ticker to cik
        self.cik = self.tickerToCIK(ticker)
        self.ticker = ticker.upper()

        # validate cik (adds leading zeros)
        self.cik = self.validateCIK(self.cik)

        # setup base api url & endpoint
        self.api_resource = 'https://data.sec.gov'
        self.endpoint = f'/api/xbrl/companyfacts/CIK{self.cik}.json'

        # print url of data were processing
        print(self.api_resource + self.endpoint)

        # request the company facts and decode it
        self.companyFacts = requests.get(self.api_resource + self.endpoint, headers=HEADERS).json()

        # construct financial statements from company facts
        self.period = period
        self.constructFinancials()

    def tickerToCIK(self, ticker: str) -> str:
        # sec provided list of tickers : cik
        self.ticker_resource = 'https://www.sec.gov/include/ticker.txt'
        
        # request
        self.tickersCIKList = requests.get(self.ticker_resource, headers=HEADERS).text.split()

        return self.tickersCIKList[self.tickersCIKList.index(ticker.lower()) + 1]
    
    def validateCIK(self, cik: str) -> str:
        # add leading zeros to cik if missing
        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros * "0" + cik
        return cik
    
    def constructFinancials(self) -> None:
        # setup generic aggregate financials dict for easy access to all financial variables
        self.aggregateFinancials = fS.FinancialStatement(self.ticker, self.companyFacts, self.period).aggregateFinancials

        # construct statements
        self.constructIncomeStatement()
        self.constructBalanceSheet()
        self.constructCashFlow()

    def constructIncomeStatement(self) -> None:
        self.incomeStatement = iS.IncomeStatement(self.ticker, self.companyFacts, self.period)

    def constructBalanceSheet(self) -> None:
        self.balanceSheet =  bS.BalanceSheet(self.ticker, self.companyFacts, self.period)

    def constructCashFlow(self) -> None:
        self.cashFlow =  cF.CashFlow(self.ticker, self.companyFacts, self.period)

    def getFinancials(self) -> dict:
        return self.aggregateFinancials

    def getIncomeStatement(self, raw=False) -> dict | iS.IncomeStatement:
        return self.incomeStatement.get(raw)

    def getBalanceSheet(self, raw=False) -> dict | bS.BalanceSheet:
        return self.balanceSheet.get(raw)

    def getCashFlow(self, raw=False) -> dict | cF.CashFlow:
        return self.cashFlow.get(raw)