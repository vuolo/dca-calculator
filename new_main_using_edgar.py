from pprint import pprint
from edgar.client import EdgarClient

# Initialize the Edgar Client
edgar_client = EdgarClient()

# Fetch financial information using ticker symbol
financials = edgar_client.financials('AAPL')

# pprint(financials.cik)
# pprint(financials.companyFacts['facts']['us-gaap']['Goodwill'])