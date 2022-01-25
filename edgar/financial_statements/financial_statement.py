from locale import currency
from pprint import pprint

from attr import attr

class FinancialStatement:

    def __init__(self, ticker: str, companyFacts: dict, period='annual') -> None:
        self.ticker = ticker
        self.companyFacts = companyFacts
        self.period = period

        self.aggregateFinancials = None
        self.incomeStatement = None
        self.balanceSheet = None
        self.cashFlow = None

        self.construct()

    def construct(self) -> dict:
        # setup return variable
        self.aggregateFinancials = {
            'symbol': self.ticker,
            'name': self.companyFacts['entityName'],
            'financials': []
        }

        # filings are 10K forms if period='annual', and 10Q forms if period='quarter'
        filings = self.constructFilings()

        # begin building financials
        for filing in filings:
            # construct template
            curFinancials = self.constructTemplate()

            # setup attributes
            for attribute in curFinancials.keys():
                curFinancials[attribute] = self.getAttribute(attribute, filing)

            # append current financials
            self.aggregateFinancials['financials'].append(curFinancials)

        # # EBITDA formula 1: EBITDA = Operating Income + Depreciation & Amortization
        # # > self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']
        # print("EBITDA (1): ")
        # # print(self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization'])
        # print(self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss']["units"]["USD"][-6]['val'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']["units"]["USD"][-6]['val'])

        # # EBITDA formula 2: EBITDA = Net Income + Taxes + Interest Expense + Depreciation & Amortization
        # # > self.companyFacts['facts']['us-gaap']['NetIncomeLoss'] + self.companyFacts['facts']['us-gaap']['CurrentIncomeTaxExpenseBenefit'] + self.companyFacts['facts']['us-gaap']['InterestExpense'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']
        # print("EBITDA (2): ")
        # print(self.companyFacts['facts']['us-gaap']['NetIncomeLoss']["units"]["USD"][-6]['val'] + self.companyFacts['facts']['us-gaap']['CurrentIncomeTaxExpenseBenefit']["units"]["USD"][-6]['val'] + self.companyFacts['facts']['us-gaap']['InterestExpense']["units"]["USD"][-6]['val'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']["units"]["USD"][-6]['val'])

        # # "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"

        return self.aggregateFinancials

    def getAttribute(self, attribute: str, filing: dict):

        # TODO: finish for all attributes
        if attribute == 'EBITDA':
            return None

        if attribute == 'accountsPayable':
            return None

        if attribute == 'capitalSurplus':
            return None

        if attribute == 'cashChange':
            return None

        if attribute == 'cashFlow':
            return None

        if attribute == 'cashFlowFinancing':
            return None

        if attribute == 'changesInInventories':
            return None

        if attribute == 'changesInReceivables':
            return None

        if attribute == 'commonStock':
            return None

        if attribute == 'costOfRevenue':
            return None

        if attribute == 'currency':
            return filing['currency']

        if attribute == 'currentAssets':
            return None

        if attribute == 'currentCash':
            return None

        if attribute == 'currentDebt':
            return None

        if attribute == 'currentLongTermDebt':
            return None

        if attribute == 'depreciation':
            return None

        if attribute == 'dividendsPaid':
            return None

        if attribute == 'ebit':
            return None

        if attribute == 'exchangeRateEffect':
            return None

        if attribute == 'filingType':
            return None

        if attribute == 'fiscalDate':
            return None

        if attribute == 'fiscalQuarter':
            return 0 if self.period == 'annual' else None # TODO: find current quarter

        if attribute == 'fiscalYear':
            return filing['fiscalYear']

        if attribute == 'goodwill':
            for unit in self.companyFacts['facts']['us-gaap']['Goodwill']['units'][filing['currency']]:
                if filing['fiscalYear'] == unit['fy']:
                    return unit['val']

        if attribute == 'grossProfit':
            return None

        if attribute == 'incomeTax':
            return None

        if attribute == 'intangibleAssets':
            return None

        if attribute == 'inventory':
            return None

        if attribute == 'interestIncome':
            return None

        if attribute == 'investingActivityOther':
            return None

        if attribute == 'investments':
            return None

        if attribute == 'longTermDebt':
            return None

        if attribute == 'longTermInvestments':
            return None

        if attribute == 'minorityInterest':
            return None

        if attribute == 'netBorrowings':
            return None

        if attribute == 'netIncome':
            return None

        if attribute == 'netIncomeBasic':
            return None

        if attribute == 'netTangibleAssets':
            return None

        if attribute == 'operatingExpense':
            return None

        if attribute == 'operatingIncome':
            return None

        if attribute == 'operatingRevenue':
            return None

        if attribute == 'otherAssets':
            return None

        if attribute == 'otherCurrentAssets':
            return None

        if attribute == 'otherCurrentLiabilities':
            return None

        if attribute == 'otherIncomeExpenseNet':
            return None

        if attribute == 'otherLiabilities':
            return None

        if attribute == 'pretaxIncome':
            return None

        if attribute == 'propertyPlantEquipment':
            return None

        if attribute == 'receivables':
            return None

        if attribute == 'reportDate':
            return None

        if attribute == 'researchAndDevelopment':
            return None

        if attribute == 'retainedEarnings':
            return None

        if attribute == 'revenue':
            return None

        if attribute == 'sellingGeneralAndAdmin':
            return None

        if attribute == 'shareholderEquity':
            return None

        if attribute == 'shortTermDebt':
            return None

        if attribute == 'shortTermInvestments':
            return None

        if attribute == 'symbol':
            return None

        if attribute == 'totalAssets':
            return None

        if attribute == 'totalCash':
            return None

        if attribute == 'totalDebt':
            return None

        if attribute == 'totalInvestingCashFlows':
            return None

        if attribute == 'totalLiabilities':
            return None

        if attribute == 'totalRevenue':
            return None

        if attribute == 'treasuryStock':
            return None

        if attribute == 'id':
            return None

        if attribute == 'key':
            return None

        if attribute == 'subkey':
            return None

        if attribute == 'updated':
            return None
    
    def constructFilings(self) -> dict:
        # TODO: setup to make it use 10Q forms instead of 10K if period='quarter'
        # use the entity public float to get a list of 10K filings
        currency = entityPublicFloat = list(self.companyFacts['facts']['dei']['EntityPublicFloat']['units'])[0]
        entityPublicFloat = self.companyFacts['facts']['dei']['EntityPublicFloat']['units'][currency]
        filings = []
        for epf in entityPublicFloat:
            filings.append({
                'currency': currency,
                'endDate': epf['end'],
                'filingType': epf['form'],
                'filedDate': epf['filed'],
                'fiscalDate': None, # TODO ??
                'fiscalQuarter': 0, # TODO setup (1, 2, 3, 4 for 10Q forms [period='quarter])
                # 'fiscalYear': epf['fy'] + 1 # TODO figure out if + 1 is needed here...
                'fiscalYear': int(epf['filed'].split('-')[0])
            })

        return filings

    def constructTemplate(self) -> dict:
        return {
            "EBITDA": None, # 17719601200,
            "accountsPayable": None, # 42998973564,
            "capitalSurplus": None, # null,
            "cashChange": None, # null,
            "cashFlow": None, # 82243225634,
            "cashFlowFinancing": None, # -90480740851,
            "changesInInventories": None, # null,
            "changesInReceivables": None, # null,
            "commonStock": None, # 52683500776,
            "costOfRevenue": None, # 41281698523,
            "currency": None, # "USD",
            "currentAssets": None, # 147408209562,
            "currentCash": None, # 92433115477,
            "currentDebt": None, # 14042702867,
            "currentLongTermDebt": None, # null,
            "depreciation": None, # 11091337897,
            "dividendsPaid": None, # null,
            "ebit": None, # 15229091974,
            "exchangeRateEffect": None, # null,
            "filingType": None, # "10-K",
            "fiscalDate": None, # "2020-10-17",
            "fiscalQuarter": None, # 4,
            "fiscalYear": None, # 2020,
            "goodwill": None, # 0,
            "grossProfit": None, # 25476146025,
            "incomeTax": None, # 2237447945,
            "intangibleAssets": None, # 0,
            "inventory": None, # 4110848973,
            "interestIncome": None, # 653431048,
            "investingActivityOther": None, # null,
            "investments": None, # null,
            "longTermDebt": None, # 90201000000,
            "longTermInvestments": None, # 103250878098,
            "minorityInterest": None, # 0,
            "netBorrowings": None, # null,
            "netIncome": None, # 13007112349,
            "netIncomeBasic": None, # 13211528403,
            "netTangibleAssets": None, # null,
            "operatingExpense": None, # 51023064506,
            "operatingIncome": None, # 14873382386,
            "operatingRevenue": None, # null,
            "otherAssets": None, # 43334740957,
            "otherCurrentAssets": None, # 11337007423,
            "otherCurrentLiabilities": None, # null,
            "otherIncomeExpenseNet": None, # 45025988542,
            "otherLiabilities": None, # null,
            "pretaxIncome": None, # 15342982672,
            "propertyPlantEquipment": None, # 37297136451,
            "receivables": None, # 37549658022,
            "reportDate": None, # "2020-10-18",
            "researchAndDevelopment": None, # 5221387455,
            "retainedEarnings": None, # 15481666532,
            "revenue": None, # 64962762222,
            "sellingGeneralAndAdmin": None, # 5160667378,
            "shareholderEquity": None, # 65804482428,
            "shortTermDebt": None, # 14085341819,
            "shortTermInvestments": None, # null,
            "symbol": None, # "AAPL",
            "totalAssets": None, # 337635772114,
            "totalCash": None, # 80433000000,
            "totalDebt": None, # 112630000000,
            "totalInvestingCashFlows": None, # -4319108499,
            "totalLiabilities": None, # 260962428116,
            "totalRevenue": None, # 65427328464,
            "treasuryStock": None, # 0,
            "id": None, # "FINANCIALS",
            "key": None, # "AAPL",
            "subkey": None, # "quarterly",
            "updated": None, # 1671015835008
        }

    def get(self, raw=False) -> dict:
        return self if raw else self.aggregateFinancials if self.aggregateFinancials != None else self.incomeStatement if self.incomeStatement != None else self.balanceSheet if self.balanceSheet != None else self.cashFlow if self.cashFlow != None else {}