from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgarClient = EdgarClient()

# Fetch financial information using ticker symbol
ticker = 'MSFT'
financials = edgarClient.financials(ticker)

aggregateFinancials = financials.getFinancials()
# incomeStatement = financials.getIncomeStatement()
# balanceSheet = financials.getBalanceSheet()
# cashFlow = financials.getCashFlow()

# [print(f"\n{ticker}'s {financial['fiscalYear']} Goodwill: \n{financial['goodwill']}") for financial in aggregateFinancials['financials']]
[print(f"\n{ticker}'s {financial['fiscalYear']} Long Term Debt: \n{financial['longTermDebt']}") for financial in aggregateFinancials['financials']]