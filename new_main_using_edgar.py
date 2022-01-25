from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Fetch financial information using ticker symbol
financials = edgar_client.financials('HD')

aggregateFinancials = financials.getFinancials()
# incomeStatement = financials.getIncomeStatement()
# balanceSheet = financials.getBalanceSheet()
# cashFlow = financials.getCashFlow()

financials_s = aggregateFinancials['financials']
# for f_s in financials_s:
    # pprint(f_s['fiscalYear'])
    # pprint(f_s['goodwill'])
    # print()