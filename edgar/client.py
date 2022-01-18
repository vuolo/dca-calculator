from edgar.company_facts import Financials

class EdgarClient():

    def financials(self, ticker: str) -> str:
        return Financials(ticker=ticker)