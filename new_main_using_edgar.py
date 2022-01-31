from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgarClient = EdgarClient()

# Fetch financial information using ticker symbol
ticker = 'AAPL'
period = 'annual'
financials = edgarClient.financials(ticker, period)

aggregateFinancials = financials.getFinancials()
# incomeStatement = financials.getIncomeStatement()
# balanceSheet = financials.getBalanceSheet()
# cashFlow = financials.getCashFlow()

pprint(aggregateFinancials)
# [print(f"\n{ticker}'s {financial['fiscalYear']} (Fiscal Year) EBITDA: \n{financial['EBITDA']}") for financial in aggregateFinancials['financials']]