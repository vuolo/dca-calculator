# TODO: if no yearly data exists, try to grab the last quarter that has data in it???

class FinancialStatement:

    def __init__(self, ticker: str, companyFacts: dict, period='annual', USE_DEPRECIATED=False) -> None:
        self.ticker = ticker
        self.companyFacts = companyFacts
        self.period = period
        self.USE_DEPRECIATED = USE_DEPRECIATED
        self.currency = "USD" # USD by default

        self.aggregateFinancials = None
        self.incomeStatement = None
        self.balanceSheet = None
        self.cashFlow = None

        self.construct()

    def construct(self) -> dict:
        if not self.USE_DEPRECIATED: # TODO: remove USE_DEPRECIATED... IN ALL FILES!
            return {}

        # setup return variable
        self.aggregateFinancials = {
            'ticker': self.ticker,
            'name': self.companyFacts['forms'][0]['EntityRegistrantName'],
            'financials': []
        }

        print(self.aggregateFinancials)
        
        # print certain company fact for all forms
        for form in self.companyFacts['forms']:
            # TODO: EBITDA = OperatingIncomeLoss + DepreciationAmortizationAndAccretionNet (or DepreciationAndAmortization or DepreciationDepletionAndAmortization???)
            # TODO: to find EBITDA, use whatever EBITDA value is calculated first (use order below)
            fact = 'LongTermDebtFairValue' # TODO: look at LongTermDebtFairValue for longTermDebt value?
            if fact in form.keys():
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")

            fact = 'OperatingIncomeLoss'
            if fact in form.keys():
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")

            fact = 'DepreciationDepletionAndAmortization'
            if fact in form.keys():
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationDepletionAndAmortization'])}")

            fact = 'DepreciationAmortizationAndAccretionNet'
            if fact in form.keys():
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationAmortizationAndAccretionNet'])}")

            fact = 'DepreciationAndAmortization'
            if fact in form.keys():
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
                print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationAndAmortization'])}")
            
            print()
        exit(0)

        # filings are 10K forms if period='annual', and 10Q forms if period='quarter'
        filings = self.constructFilings()

        # begin building financials
        for filing in filings:
            # construct template
            curFinancials = self.constructTemplate()

            # setup concepts
            for concept in curFinancials.keys(): curFinancials[concept] = self.getConcept(concept, filing['fiscalYear'])

            # append current financials
            self.aggregateFinancials['financials'].append(curFinancials)

        return self.aggregateFinancials

    def getConceptVal(self, rawConcept: str, fiscalYear: int):
        total_return_val = 0
        if not self.hasConcept(rawConcept): return None
        for unit in self.getConceptUnits(rawConcept):
            if fiscalYear == unit['fy']:
                if self.period == 'annual' and unit['form'] == '10-K':
                    return unit['val'] or None
                elif self.period == 'quarter' and unit['form'] == '10-Q':
                    total_return_val += unit['val'] or 0
        
        return total_return_val
                
    def getConceptUnits(self, concept: str, factsType='us-gaap', raw=False) -> bool:
        if raw: return self.companyFacts['facts'][factsType][concept]['units']
        else: return self.companyFacts['facts'][factsType][concept]['units'][self.currency]

    def hasConcept(self, concept: str, factsType='us-gaap') -> bool:
        return concept in self.companyFacts['facts'][factsType].keys()

    def getConcept(self, concept: str, fiscalYear: int):
        # TODO: finish implementation for all concepts
        if concept == 'EBITDA':
            # IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest????????
            # income: 13510 (IncomeTaxesPaid or IncreaseDecreaseInIncomeTaxesReceivable or AccruedIncomeTaxesNoncurrent) + Depreciation & Amortization: (WeightedAverageNumberOfSharesOutstandingBasic?) 11152 + net interest expense: 2315 + income taxes: 6858
            operatingIncome = self.getConceptVal('IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', fiscalYear)
            DA = self.getConceptVal('DepreciationAndAmortization', fiscalYear) or 0 # TODO: look into DepreciationAmortizationAndAccretionNet
            # return operatingIncome + DA
            return operatingIncome
            # return DA

            # # net income
            # EB = self.getConceptVal('NetIncomeLoss', fiscalYear) or 0
            # # interest
            # I = self.getConceptVal('InterestExpenseDebtExcludingAmortization', fiscalYear) or 0
            # # taxes
            # T = self.getConceptVal('IncomeTaxExpenseBenefit', fiscalYear) or 0
            # # depreciation + amortization
            # DA = self.getConceptVal('DepreciationAndAmortization', fiscalYear) or 0 # TODO: look into DepreciationAmortizationAndAccretionNet
            # print(f'EB: {EB}, I: {I}, T: {T}, DA: {DA} ({EB + I + T + DA})')
            # return EB + I + T + DA

        # # EBITDA formula 1: EBITDA = Operating Income + Depreciation & Amortization
        # # > self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']
        # print("EBITDA (1): ")
        # # print(self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization'])
        # print(self.companyFacts['facts']['us-gaap']['OperatingIncomeLoss']["units"]["USD"][-6]['val'] + self.companyFacts['facts']['us-gaap']['DepreciationAndAmortization']["units"]["USD"][-6]['val'])
        
        # # "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"

        if concept == 'accountsPayable': return self.getConceptVal('AccountsPayableCurrent', fiscalYear)

        if concept == 'capitalSurplus': return self.getConceptVal('AdditionalPaidInCapitalCommonStock', fiscalYear)

        if concept == 'cashChange':
            return None

        if concept == 'cashFlow': return self.getConceptVal('NetCashProvidedByUsedInOperatingActivities', fiscalYear)

        if concept == 'cashFlowFinancing':
            return None

        if concept == 'changesInInventories':
            return None

        if concept == 'changesInReceivables':
            return None

        # TODO: verify if this is the right raw concept name to use
        if concept == 'commonStock': return self.getConceptVal('CommonStockValue', fiscalYear)

        if concept == 'costOfRevenue':
            return None

        if concept == 'currency': return self.currency

        if concept == 'currentAssets': return self.getConceptVal('AssetsCurrent', fiscalYear)

        if concept == 'currentCash':
            return None

        if concept == 'currentDebt':
            return None

        if concept == 'currentLongTermDebt': return self.getConceptVal('LongTermDebtCurrent', fiscalYear)

        if concept == 'depreciation': return self.getConceptVal('Depreciation', fiscalYear)

        if concept == 'dividendsPaid':
            return None

        if concept == 'ebit':
            return None

        if concept == 'exchangeRateEffect':
            return None

        if concept == 'filingType':
            return None

        if concept == 'fiscalDate':
            return None

        if concept == 'fiscalQuarter': return 0 if self.period == 'annual' else None # TODO: find current quarter

        if concept == 'fiscalYear': return fiscalYear

        if concept == 'goodwill': return self.getConceptVal('Goodwill', fiscalYear)

        if concept == 'grossProfit': return self.getConceptVal('GrossProfit', fiscalYear)

        if concept == 'incomeTax':
            return None

        if concept == 'intangibleAssets':
            return None

        if concept == 'inventory': return self.getConceptVal('InventoryNet', fiscalYear)

        if concept == 'interestIncome':
            return None

        if concept == 'investingActivityOther':
            return None

        if concept == 'investments':
            return None

        if concept == 'longTermDebt':
            # TODO: figure out how to get CORRECT long term debt from MSFT... LongTermDebtAndCapitalLeaseObligations / LongTermDebt???
            return self.getConceptVal('LongTermDebt', fiscalYear)

        if concept == 'longTermInvestments':
            return None

        if concept == 'minorityInterest':
            return None

        if concept == 'netBorrowings':
            return None

        if concept == 'netIncome':
            return None

        if concept == 'netIncomeBasic':
            return None

        if concept == 'netTangibleAssets':
            return None

        if concept == 'operatingExpense':
            return None

        if concept == 'operatingIncome':
            return None

        if concept == 'operatingRevenue':
            return None

        if concept == 'otherAssets':
            return None

        if concept == 'otherCurrentAssets':
            return None

        if concept == 'otherCurrentLiabilities':
            return None

        if concept == 'otherIncomeExpenseNet':
            return None

        if concept == 'otherLiabilities':
            return None

        if concept == 'pretaxIncome':
            return None

        if concept == 'propertyPlantEquipment':
            return None

        if concept == 'receivables':
            return None

        if concept == 'reportDate':
            return None

        if concept == 'researchAndDevelopment':
            return None

        if concept == 'retainedEarnings':
            return None

        if concept == 'revenue':
            return None

        if concept == 'sellingGeneralAndAdmin':
            return None

        if concept == 'shareholderEquity':
            return None

        if concept == 'shortTermDebt':
            return None

        if concept == 'shortTermInvestments':
            return None

        if concept == 'symbol':
            return None

        if concept == 'totalAssets':
            return None

        if concept == 'totalCash':
            return None

        if concept == 'totalDebt':
            return None

        if concept == 'totalInvestingCashFlows':
            return None

        if concept == 'totalLiabilities':
            return None

        if concept == 'totalRevenue':
            return None

        if concept == 'treasuryStock':
            return None

        if concept == 'id':
            return None

        if concept == 'key':
            return None

        if concept == 'subkey':
            return None

        if concept == 'updated':
            return None
    
    def constructFilings(self) -> dict:
        # TODO: setup to make it use 10Q forms instead of 10K if period='quarter'
        # use the entity public float to get a list of 10K filings
        self.currency = list(self.getConceptUnits('EntityPublicFloat', 'dei', True))[0]
        entityPublicFloat = self.getConceptUnits('EntityPublicFloat', 'dei')
        filings = []
        for epf in entityPublicFloat:
            filings.append({
                'currency': self.currency,
                'endDate': epf['end'],
                'filingType': epf['form'],
                'filedDate': epf['filed'],
                'fiscalDate': None, # TODO ??
                'fiscalQuarter': 0, # TODO setup (1, 2, 3, 4 for 10Q forms [period='quarter])
                'fiscalYear': epf['fy'] # fiscalYear means END OF YEAR DATA (ex: 2020 means Dec 31, 2020)
                # 'fiscalYear': epf['fy'] + 1 # TODO figure out if + 1 is needed here...
                # 'fiscalYear': int(epf['filed'].split('-')[0])
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
        return self if raw else self.aggregateFinancials if self.aggregateFinancials != None else self.incomeStatement if self.incomeStatement != None else self.balanceSheet if self.balanceSheet != None else self.cashFlow if self.cashFlow != None else None

# ------------------------------------ IEX CLOUD RAW DATA:
# "AccountsPayableCurrent" : 6932000000,
# "AccountsReceivableNetCurrent" : 16186000000,
# "AccruedIncomeTaxesCurrent" : 711000000,
# "AccruedIncomeTaxesNoncurrent" : 11300000000,
# "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment" : 16192000000,
# "AccumulatedOtherComprehensiveIncomeLossNetOfTax" : 3383000000,
# "AcquisitionsNetofCashAcquiredAndPurchasesOfIntangibleandOtherAssets" : 2794000000,
# "AllocatedShareBasedCompensationExpense" : 633000000,
# "AllowanceForDoubtfulAccountsReceivableCurrent" : 288000000,
# "AmortizationOfIntangibleAssets" : 329000000,
# "Assets" : 174848000000,
# "AssetsCurrent" : 116362000000,
# "AssetsFairValueDisclosureRecurring" : 97350000000,
# "AvailableForSaleDebtSecuritiesAmortizedCostBasis" : 84953000000,
# "AvailableForSaleSecurities" : 102563000000,
# "AvailableForSaleSecuritiesAccumulatedGrossUnrealizedGainBeforeTax" : 5243000000,
# "AvailableForSaleSecuritiesAccumulatedGrossUnrealizedLossBeforeTax" : 427000000,
# "AvailableForSaleSecuritiesAmortizedCost" : 97747000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPosition12MonthsOrLongerAccumulatedLoss" : 103000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPositionAccumulatedLoss" : 427000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPositionFairValue" : 39900000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPositionLessThan12MonthsAccumulatedLoss" : 324000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPositionLessThanTwelveMonthsFairValue" : 38893000000,
# "AvailableForSaleSecuritiesContinuousUnrealizedLossPositionTwelveMonthsOrLongerFairValue" : 1007000000,
# "AvailableForSaleSecuritiesCurrent" : 83823000000,
# "AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsAmortizedCostBasis" : 29985000000,
# "AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsFairValue" : 29998000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenAmortizedCostBasis" : 1457000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenFairValue" : 1540000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenAmortizedCostBasis" : 2719000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenFairValue" : 2710000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingYearTwoThroughFiveAmortizedCostBasis" : 50792000000,
# "AvailableForSaleSecuritiesDebtMaturitiesRollingYearTwoThroughFiveFairValue" : 50822000000,
# "AvailableForSaleSecuritiesDebtSecurities" : 85070000000,
# "AvailableForSaleSecuritiesGrossRealizedGains" : 421000000,
# "AvailableForSaleSecuritiesGrossRealizedLosses" : 78000000,
# "BusinessCombinationIntegrationRelatedCosts" : 243000000,
# "CapitalizedComputerSoftwareAmortization" : 15000000,
# "CashAndCashEquivalentsAtCarryingValue" : 6426000000,
# "CashAndCashEquivalentsPeriodIncreaseDecrease" : 124000000,
# "CashCashEquivalentsAndShortTermInvestments" : 90249000000,
# "CommercialPaper" : 8300000000,
# "CommitmentAmountUponClosingMergerTransaction" : 2000000000,
# "CommonStockDividendsPerShareDeclared" : 0.31,
# "CommonStockSharesAuthorized" : 24000000000,
# "CommonStockSharesOutstanding" : 8218000000,
# "CommonStocksIncludingAdditionalPaidInCapital" : 68765000000,
# "ComprehensiveIncomeNetOfTax" : 5489000000,
# "CostOfRevenue" : 10136000000,
# "DebtInstrumentFaceAmount" : 20104000000,
# "DebtInstrumentUnamortizedDiscount" : 95000000,
# "DebtLongtermAndShorttermCombinedAmount" : 28300000000,
# "DeferredIncomeTaxExpenseBenefit" : 314000000,
# "DeferredRevenue" : 21243000000,
# "DeferredRevenueCurrent" : 19192000000,
# "DeferredRevenueNoncurrent" : 2051000000,
# "DeferredTaxAssetsLiabilitiesNetCurrent" : 1701000000,
# "DeferredTaxLiabilitiesNoncurrent" : 2820000000,
# "DepositsReceivedForSecuritiesLoanedAtCarryingValue" : 430000000,
# "DepreciationAmortizationAndOther" : 1521000000,
# "DerivativeInstrumentsNotDesignatedAsHedgingInstrumentsGainLossNet" : -77000000,
# "DividendPayableDateToBePaidDayMonthAndYear" : "2015-03-12",
# "DividendsCommonStockCash" : 2548000000,
# "DividendsPayableDateDeclaredDayMonthAndYear" : "2014-12-03",
# "DividendsPayableDateOfRecordDayMonthAndYear" : "2015-02-19",
# "DocumentFiscalPeriodFocus" : "Q2",
# "DocumentFiscalYearFocus" : "2015",
# "DocumentType" : "10-Q",
# "EarningsPerShareBasic" : 0.71,
# "EarningsPerShareDiluted" : 0.71,
# "EffectOfExchangeRateOnCashAndCashEquivalents" : -34000000,
# "EffectiveIncomeTaxRateContinuingOperations" : 0.25,
# "EmployeeRelatedLiabilitiesCurrent" : 3479000000,
# "ExcessTaxBenefitFromShareBasedCompensationFinancingActivities" : 22000000,
# "ExcessTaxBenefitFromShareBasedCompensationOperatingActivities" : 22000000,
# "FiniteLivedIntangibleAssetsAccumulatedAmortization" : 4680000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseAfterYearFive" : 2803000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseRemainderOfFiscalYear" : 683000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseYearFive" : 759000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseYearFour" : 843000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseYearThree" : 978000000,
# "FiniteLivedIntangibleAssetsAmortizationExpenseYearTwo" : 1233000000,
# "FiniteLivedIntangibleAssetsGross" : 11979000000,
# "FiniteLivedIntangibleAssetsNet" : 7299000000,
# "ForeignCurrencyCashFlowHedgeGainLossToBeReclassifiedDuringNext12Months" : 478000000,
# "ForeignCurrencyTransactionGainLossBeforeTax" : 83000000,
# "GainLossOnInvestments" : 317000000,
# "GainLossOnInvestmentsAndDerivativeInstruments" : 179000000,
# "GeneralAndAdministrativeExpense" : 1097000000,
# "Goodwill" : 21855000000,
# "GrossProfit" : 16334000000,
# "HeldToMaturitySecurities" : 351000000,
# "HeldToMaturitySecuritiesAccumulatedUnrecognizedHoldingGain" : 78000000,
# "HeldToMaturitySecuritiesAmortizedCostBeforeOtherThanTemporaryImpairment" : 351000000,
# "HeldToMaturitySecuritiesFairValue" : 429000000,
# "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments" : 7850000000,
# "IncomeTaxExpenseBenefit" : 1987000000,
# "IncreaseDecreaseInAccountsPayable" : 137000000,
# "IncreaseDecreaseInAccountsReceivable" : 3378000000,
# "IncreaseDecreaseInCollateralHeldUnderSecuritiesLending" : -238000000,
# "IncreaseDecreaseInDeferredRevenue" : 10200000000,
# "IncreaseDecreaseInInventories" : -1070000000,
# "IncreaseDecreaseInOtherCurrentAssets" : 159000000,
# "IncreaseDecreaseInOtherCurrentLiabilities" : -986000000,
# "IncreaseDecreaseInOtherNoncurrentAssets" : -170000000,
# "IncreaseDecreaseInOtherNoncurrentLiabilities" : 651000000,
# "IncrementalCommonSharesAttributableToShareBasedPaymentArrangements" : 69000000,
# "InterestExpense" : 162000000,
# "InventoryFinishedGoodsNetOfReserves" : 1112000000,
# "InventoryNet" : 2053000000,
# "InventoryRawMaterialsNetOfReserves" : 681000000,
# "InventoryWorkInProcessNetOfReserves" : 260000000,
# "InvestmentIncomeNet" : 183000000,
# "Liabilities" : 82969000000,
# "LiabilitiesAndStockholdersEquity" : 174848000000,
# "LiabilitiesCurrent" : 47415000000,
# "LongTermDebt" : 20000000000,
# "LongTermDebtCurrent" : 1749000000,
# "LongTermDebtFairValue" : 21600000000,
# "LongTermDebtNoncurrent" : 18260000000,
# "LongTermInvestments" : 12665000000,
# "LongTermInvestmentsExcludingHeldToMaturity" : 12314000000,
# "MarketableSecuritiesRealizedGainLossOtherThanTemporaryImpairmentsAmount" : 26000000,
# "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations" : 534000000,
# "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations" : -4716000000,
# "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations" : 4340000000,
# "NetIncomeLoss" : 5863000000,
# "NoncashAssetRelatedRestructuringCharge" : 56000000,
# "NonoperatingIncomeExpense" : 74000000,
# "OperatingExpenses" : 8558000000,
# "OperatingIncomeLoss" : 7776000000,
# "OtherAssetsCurrent" : 6173000000,
# "OtherAssetsFairValueDisclosure" : 2000000,
# "OtherAssetsNoncurrent" : 3060000000,
# "OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax" : -231000000,
# "OtherComprehensiveIncomeLossAvailableForSaleSecuritiesTax" : -124000000,
# "OtherComprehensiveIncomeLossDerivativesQualifyingAsHedgesNetOfTax" : 247000000,
# "OtherComprehensiveIncomeLossDerivativesQualifyingAsHedgesTax" : 6000000,
# "OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax" : -390000000,
# "OtherComprehensiveIncomeLossForeignCurrencyTranslationAdjustmentTax" : -211000000,
# "OtherComprehensiveIncomeLossNetOfTax" : -374000000,
# "OtherFinancialInstrumentCovenantMinimumLiquidity" : 1000000000,
# "OtherLiabilitiesCurrent" : 6623000000,
# "OtherLiabilitiesNoncurrent" : 12423000000,
# "OtherNonoperatingIncomeExpense" : -209000000,
# "PaymentsForRepurchaseOfCommonStock" : 2145000000,
# "PaymentsOfDividendsCommonStock" : 2547000000,
# "PaymentsToAcquireInvestments" : 19167000000,
# "PaymentsToAcquirePropertyPlantAndEquipment" : 1490000000,
# "ProceedsFromDebtMaturingInMoreThanThreeMonths" : 0,
# "ProceedsFromIssuanceOfCommonStock" : 121000000,
# "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities" : 2389000000,
# "ProceedsFromPaymentsForOtherFinancingActivities" : 285000000,
# "ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess" : 4798000000,
# "ProceedsFromSaleOfAvailableForSaleSecurities" : 16108000000,
# "PropertyPlantAndEquipmentNet" : 13607000000,
# "RecognitionOfDeferredRevenue" : 11495000000,
# "RepaymentsOfDebtMaturingInMoreThanThreeMonths" : 0,
# "ResearchAndDevelopmentExpense" : 2903000000,
# "RestructuringAndRelatedCostExpectedCostRemaining1" : 200000000,
# "RestructuringAndRelatedCostNumberOfPositionsEliminatedInceptionToDate" : 17500,
# "RestructuringCharges" : 132000000,
# "RestructuringReserve" : 275000000,
# "RetainedEarningsAccumulatedDeficit" : 19731000000,
# "SalesRevenueNet" : 26470000000,
# "SecuritiesLoaned" : 414000000,
# "SegmentOperatingExpenseExcludingIntegrationAndRestructuring" : 8315000000,
# "SellingAndMarketingExpense" : 4315000000,
# "ShortTermBorrowings" : 8299000000,
# "StockRepurchaseProgramRemainingAuthorizedRepurchaseAmount1" : 31100000000,
# "StockholdersEquity" : 91879000000,
# "TradingSymbol" : "MSFT",
# "WeightedAverageNumberOfDilutedSharesOutstanding" : 8297000000,
# "WeightedAverageNumberOfSharesOutstandingBasic" : 8228000000,
# "accessionNumber" : "0001193125-15-020351",
# "cik" : "0000789019",
# "date" : 1422230400000,
# "dateFiled" : 1422230400000,
# "documentType" : "10-Q",
# "entityName" : "MICROSOFT CORP",
# "id" : "REPORTED_FINANCIALS",
# "irsNumber" : "911144442",
# "key" : "MSFT",
# "periodEnd" : 1419984000000,
# "periodStart" : 1412121600000,
# "reportLink" : "https://www.sec.gov/Archives/edgar/data/789019/000119312515020351/msft-20141231.xml",
# "subkey" : "10-Q",
# "update" : "20150126",
# "updated" : 1620931568000

# ------------------------------------ IEX CLOUD PROCESSED DATA:
# "EBITDA": 17719601200,
# "accountsPayable": 42998973564,
# "capitalSurplus": null,
# "cashChange": null,
# "cashFlow": 82243225634,
# "cashFlowFinancing": -90480740851,
# "changesInInventories": null,
# "changesInReceivables": null,
# "commonStock": 52683500776,
# "costOfRevenue": 41281698523,
# "currency": "USD",
# "currentAssets": 147408209562,
# "currentCash": 92433115477,
# "currentDebt": 14042702867,
# "currentLongTermDebt": null,
# "depreciation": 11091337897,
# "dividendsPaid": null,
# "ebit": 15229091974,
# "exchangeRateEffect": null,
# "filingType": "10-K",
# "fiscalDate": "2020-10-17",
# "fiscalQuarter": 4,
# "fiscalYear": 2020,
# "goodwill": 0,
# "grossProfit": 25476146025,
# "incomeTax": 2237447945,
# "intangibleAssets": 0,
# "interestIncome": 653431048,
# "inventory": 4110848973,
# "investingActivityOther": null,
# "investments": null,
# "longTermDebt": 90201000000,
# "longTermInvestments": 103250878098,
# "minorityInterest": 0,
# "netBorrowings": null,
# "netIncome": 13007112349,
# "netIncomeBasic": 13211528403,
# "netTangibleAssets": null,
# "operatingExpense": 51023064506,
# "operatingIncome": 14873382386,
# "operatingRevenue": null,
# "otherAssets": 43334740957,
# "otherCurrentAssets": 11337007423,
# "otherCurrentLiabilities": null,
# "otherIncomeExpenseNet": 45025988542,
# "otherLiabilities": null,
# "pretaxIncome": 15342982672,
# "propertyPlantEquipment": 37297136451,
# "receivables": 37549658022,
# "reportDate": "2020-10-18",
# "researchAndDevelopment": 5221387455,
# "retainedEarnings": 15481666532,
# "revenue": 64962762222,
# "sellingGeneralAndAdmin": 5160667378,
# "shareholderEquity": 65804482428,
# "shortTermDebt": 14085341819,
# "shortTermInvestments": null,
# "symbol": "AAPL",
# "totalAssets": 337635772114,
# "totalCash": 80433000000,
# "totalDebt": 112630000000,
# "totalInvestingCashFlows": -4319108499,
# "totalLiabilities": 260962428116,
# "totalRevenue": 65427328464,
# "treasuryStock": 0,
# "id": "FINANCIALS",
# "key": "AAPL",
# "subkey": "quarterly",
# "updated": 1671015835008