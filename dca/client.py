from sqlite3 import paramstyle
from edgar.financials import Financials
from dca.parameters import Parameters

class DCAClient():

    def __init__(self, financials: Financials) -> None:
        self.financials = financials
        self.parametersResults = {}

        self.runParameters(self.financials)

    def runParameters(self, financials: Financials) -> None:
        self.parameters = Parameters(financials)
        self.parametersResults[financials.ticker] = self.parameters.getResults()
    
    def getParametersResult(self, ticker=None) -> dict:
        return self.parametersResults[ticker or self.financials.ticker]