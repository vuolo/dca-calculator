from pydoc import doc
import re
import xml.etree.ElementTree as ET
import requests
from edgar.financial_statements import financial_statement as fS
from edgar.financial_statements import income_statement as iS
from edgar.financial_statements import balance_sheet as bS
from edgar.financial_statements import cash_flow as cF

HEADERS = { 'User-Agent': 'Sample Company Name AdminContact@<sample company domain>.com' }

def parse_and_get_ns(rawstr):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in ET.iter(rawstr, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #     to different URI namespaces in different parts of the
                #     document. This exception serves as a reminder that this
                #     solution is not robust.    Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "{%s}" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return ET.ElementTree(root), ns

class Financials():

    def __init__(self, ticker: str, period='annual') -> None:
        self.period = period

        # convert ticker to cik
        self.ticker = ticker.upper()
        self.setupCIK(ticker)

        # validate cik (adds leading zeros)
        self.cik = self.validateCIK(self.cik)

        # toggle to use depreciated (True uses )
        self.USE_DEPRECIATED = True

        # setup base api url & endpoint
        if self.USE_DEPRECIATED:
            # self.api_resource = 'https://www.sec.gov'
            # self.endpoint = f'/cgi-bin/browse-edgar?action=getcompany&CIK={self.cik}&type={"10-K" if period == "annual" else "10-Q"}&dateb=&owner=include&count={1000}&search_text='
            self.api_resource = 'https://data.sec.gov'
            self.endpoint = f'/submissions/CIK{self.cik}.json'
        else:
            self.api_resource = 'https://data.sec.gov'
            self.endpoint = f'/api/xbrl/companyfacts/CIK{self.cik}.json'

        # print url of data were processing
        # print(self.api_resource + self.endpoint)

        # request the company facts and decode it
        self.companyFacts = self.fetchCompanyFacts()

        # construct financial statements from company facts
        self.constructFinancials()

    def fetchCompanyFacts(self) -> dict:
        fetchedData = requests.get(self.api_resource + self.endpoint, headers=HEADERS).json()

        if not self.USE_DEPRECIATED:
            return fetchedData
        
        # loop through forms and get all forms based on period
        formIndexes = []
        for i, form in enumerate(fetchedData['filings']['recent']['form']):
            if form == ('10-K' if self.period == 'annual' else '10-Q'):
                formIndexes.append(i)
        
        # setup empty company facts obj
        companyFacts = {
            'ticker': self.ticker,
            'forms': []
        }

        # get company facts from each form
        for formIndex in formIndexes:
            accession_number = fetchedData['filings']['recent']['accessionNumber'][formIndex].replace('-', '')
            document_name = fetchedData['filings']['recent']['primaryDocument'][formIndex].replace('.htm', '_htm.xml')
            form_data_url = f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{accession_number}/{document_name}"

            # xml read using element tree
            root = ET.fromstring(requests.get(form_data_url, headers=HEADERS).text)

            # if error, then use older filing format
            if root.tag == 'Error':
                document_name = fetchedData['filings']['recent']['primaryDocument'][formIndex].replace('.htm', '.xml').replace('10k_' if self.period == 'annual' else '10q_', '')
                form_data_url = f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{accession_number}/{document_name}"
                root = ET.fromstring(requests.get(form_data_url, headers=HEADERS).text)
                # if error, then use alternate older filing format
                if root.tag == 'Error':
                    # conv wmtform10-kx1312017.xml to wmt-20170131.xml
                    document_name = f"{self.ticker.lower()}-{fetchedData['filings']['recent']['reportDate'][formIndex].replace('-', '')}.xml"
                    form_data_url = f"https://www.sec.gov/Archives/edgar/data/{self.cik}/{accession_number}/{document_name}"
                    root = ET.fromstring(requests.get(form_data_url, headers=HEADERS).text)

            # display form data url
            print(form_data_url)

            # setup company facts
            formCompanyFacts = {}
            for child in root.findall('./'):
                match = re.search('{.*}', child.tag)
                xmlns = match.group(0) if match else ''
    
                # replace xml ns with nothing to get tag (company fact) name
                companyFact = child.tag.replace(xmlns, '')
                if companyFact not in formCompanyFacts.keys():
                    formCompanyFacts[companyFact] = child.text

            companyFacts['forms'].append(formCompanyFacts)

        return companyFacts

    def setupCIK(self, ticker: str):
        # sec provided list of tickers : cik
        self.ticker_resource = 'https://www.sec.gov/files/company_tickers.json'
        
        # request tickers if not already fetched
        if not hasattr(self, 'companyTickers'):
            self.companyTickers = requests.get(self.ticker_resource, headers=HEADERS).json()

        # get cik and company name
        for index in self.companyTickers.keys():
            if self.companyTickers[index]['ticker'] == self.ticker:
                self.cik = str(self.companyTickers[index]['cik_str'])
                self.companyName = self.companyTickers[index]['title']
                return
    
    def validateCIK(self, cik: str) -> str:
        # add leading zeros to cik if missing
        if len(cik) < 10:
            num_of_zeros = 10 - len(cik)
            cik = num_of_zeros * "0" + cik
        return cik
    
    def constructFinancials(self) -> None:
        # setup generic aggregate financials dict for easy access to all financial variables
        self.aggregateFinancials = fS.FinancialStatement(self.ticker, self.companyFacts, self.period, self.USE_DEPRECIATED).aggregateFinancials

        # construct statements
        self.constructIncomeStatement()
        self.constructBalanceSheet()
        self.constructCashFlow()

    def constructIncomeStatement(self) -> None:
        self.incomeStatement = iS.IncomeStatement(self.ticker, self.companyFacts, self.period, self.USE_DEPRECIATED)

    def constructBalanceSheet(self) -> None:
        self.balanceSheet =  bS.BalanceSheet(self.ticker, self.companyFacts, self.period, self.USE_DEPRECIATED)

    def constructCashFlow(self) -> None:
        self.cashFlow =  cF.CashFlow(self.ticker, self.companyFacts, self.period, self.USE_DEPRECIATED)

    def getFinancials(self) -> dict:
        return self.aggregateFinancials

    def getIncomeStatement(self, raw=False) -> dict | iS.IncomeStatement:
        return self.incomeStatement.get(raw)

    def getBalanceSheet(self, raw=False) -> dict | bS.BalanceSheet:
        return self.balanceSheet.get(raw)

    def getCashFlow(self, raw=False) -> dict | cF.CashFlow:
        return self.cashFlow.get(raw)