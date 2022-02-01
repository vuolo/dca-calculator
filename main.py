from pprint import pprint
from edgar.client import EdgarClient
from dca.client import DCAClient

# Initialize the Edgar Client
edgarClient = EdgarClient()

# Fetch financial information using ticker symbol
ticker = 'CBOE'
period = 'annual'
financials = edgarClient.financials(ticker, period)

# Initialize the DCA Client
dcaClient = DCAClient(financials)

# pprint(financials.getFinancials())

# Run parameters on financial data
result = dcaClient.getParametersResult()

pprint(result)

# aggregateFinancials = financials.getFinancials()
# incomeStatement = financials.getIncomeStatement()
# balanceSheet = financials.getBalanceSheet()
# cashFlow = financials.getCashFlow()

# pprint(aggregateFinancials)
# [print(f"\n{ticker}'s {financial['fiscalYear']} (Fiscal Year) EBITDA: \n{financial['EBITDA']}") for financial in aggregateFinancials['financials']]