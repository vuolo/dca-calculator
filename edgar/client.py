from edgar.financials import Financials

class EdgarClient():

    def financials(self, ticker: str, period='annual') -> str:
        return Financials(ticker, period)