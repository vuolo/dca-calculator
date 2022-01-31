import time

class FinancialStatement:

    def __init__(self, ticker: str, companyFacts: dict, period='annual', asReported=False) -> None:
        self.ticker = ticker
        self.companyFacts = companyFacts
        self.period = period
        self.currency = "USD" # USD by default

        self.aggregateFinancials = None
        self.incomeStatement = None
        self.balanceSheet = None
        self.cashFlow = None

        self.construct()

    def construct(self) -> dict:
        # setup return variable
        self.aggregateFinancials = {
            'ticker': self.ticker,
            'name': self.companyFacts['forms'][0]['EntityRegistrantName'],
            'financials': []
        }
        
        # print certain company fact for all forms
        # for form in self.companyFacts['forms']:
        #     # TODO: EBITDA = OperatingIncomeLoss + DepreciationAmortizationAndAccretionNet (or DepreciationAndAmortization or DepreciationDepletionAndAmortization???)
        #     # TODO: to find EBITDA, use whatever EBITDA value is calculated first (use order below)
        #     fact = 'LongTermDebtFairValue' # TODO: look at LongTermDebtFairValue for longTermDebt value?
        #     if fact in form.keys():
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")

        #     fact = 'OperatingIncomeLoss'
        #     if fact in form.keys():
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")

        #     fact = 'DepreciationDepletionAndAmortization'
        #     if fact in form.keys():
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationDepletionAndAmortization'])}")

        #     fact = 'DepreciationAmortizationAndAccretionNet'
        #     if fact in form.keys():
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationAmortizationAndAccretionNet'])}")

        #     fact = 'DepreciationAndAmortization'
        #     if fact in form.keys():
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {fact}: {form[fact]}")
        #         print(f"fiscalYear: {form['DocumentFiscalYearFocus']}, {'EBITDA'}: {int(form['OperatingIncomeLoss']) + int(form['DepreciationAndAmortization'])}")
            
        #     print()

        # begin building financials
        for form in self.companyFacts['forms']:
            # construct template
            curFinancials = self.constructTemplate()

            # setup concepts
            for concept in curFinancials.keys():
                curFinancials[concept] = self.getConcept(concept, form)

            # append current financials
            self.aggregateFinancials['financials'].append(curFinancials)

        return self.aggregateFinancials

    def getConceptVal(self, rawConcept: str, form: dict, type='int'):
        return None if not self.hasConcept(rawConcept, form) else int(form[rawConcept]) if type == 'int' else form[rawConcept]

    def hasConcept(self, rawConcept: str, form: dict) -> bool:
        return rawConcept in form.keys()

    def getConcept(self, concept: str, form: dict):
        # TODO: finish implementation for all concepts

        # TODO: implement EBITDA
        if concept == 'EBITDA': return None
        if concept == 'accountsPayable': return self.getConceptVal('IncreaseDecreaseInAccountsPayable', form) # AccountsPayableCurrent?
        if concept == 'capitalSurplus': return None
        if concept == 'cashChange': return None
        if concept == 'cashFlow': return self.getConceptVal('NetCashProvidedByUsedInOperatingActivities', form)
        if concept == 'cashFlowFinancing': return self.getConceptVal('NetCashProvidedByUsedInFinancingActivities', form)
        if concept == 'changesInInventories': return self.getConceptVal('IncreaseDecreaseInInventories', form)
        if concept == 'changesInReceivables':  return self.getConceptVal('IncreaseDecreaseInAccountsReceivable', form)
        # TODO: commonStock gets 'Common Equity (Total)' from WSJ cash-flow financials sheet... ASK JONNY IF THIS IS THE RIGHT VALUE WE WANT
        if concept == 'commonStock': return self.getConceptVal('StockholdersEquity', form)
        # TODO: verify if this is the right value w/ jonny
        if concept == 'costOfRevenue': return self.getConceptVal('CostOfGoodsAndServicesSold', form)
        if concept == 'currency': return self.currency
        if concept == 'currentAssets': return self.getConceptVal('AssetsCurrent', form)
        # TODO: ask jonny if we want 'Cash' or 'Cash & Short Term Investments' from WSJ balance-sheet... etc..
        if concept == 'currentCash': return self.getConceptVal('Cash', form)
        # TODO: ask jonny what this value is... short term or long term debt? bc next value asks for long term debt...
        if concept == 'currentDebt': return self.getConceptVal('DebtCurrent', form)
        if concept == 'currentLongTermDebt': return self.getConceptVal('LongTermDebtCurrent', form)
        if concept == 'depreciation': return self.getConceptVal('Depreciation', form)
        # TODO: check w/ jonny to see if this is the right value
        if concept == 'dividendsPaid': return self.getConceptVal('PaymentsOfDividendsCommonStock', form)
        # TODO: implement EBIT
        if concept == 'ebit': return None
        if concept == 'exchangeRateEffect': return None
        if concept == 'filingType': return self.getConceptVal('DocumentType', form, type='str')
        if concept == 'fiscalDate': return self.getConceptVal('DocumentPeriodEndDate', form, type='str')
        if concept == 'fiscalQuarter': return self.getConceptVal('DocumentFiscalPeriodFocus', form, type='str')
        if concept == 'fiscalYear': return self.getConceptVal('DocumentFiscalYearFocus', form)
        if concept == 'goodwill': return self.getConceptVal('Goodwill', form)
        if concept == 'grossProfit': return self.getConceptVal('GrossProfit', form)
        if concept == 'incomeTax': return self.getConceptVal('IncomeTaxExpenseBenefit', form)
        if concept == 'intangibleAssets': return None
        if concept == 'inventory': return self.getConceptVal('InventoryNet', form)
        # TODO: check interestIncome variable w/ jonny...
        if concept == 'interestIncome': return self.getConceptVal('InterestPaidNet', form)
        # TODO: check if this variable uses PaymentsForProceedsFromOtherInvestingActivities or NetCashProvidedByUsedInInvestingActivities
        if concept == 'investingActivityOther': return self.getConceptVal('PaymentsForProceedsFromOtherInvestingActivities', form)
        # TODO: verify if PaymentsToAcquireOtherInvestments is the right raw concept
        if concept == 'investments': return self.getConceptVal('PaymentsToAcquireOtherInvestments', form)
        # TODO: figure out how to get CORRECT long term debt from MSFT... LongTermDebtAndCapitalLeaseObligations / LongTermDebt???
        if concept == 'longTermDebt': return self.getConceptVal('LongTermDebtFairValue', form)
        # TODO: this is probs wrong so check this variable...
        if concept == 'longTermInvestments': return self.getConceptVal('MarketableSecuritiesNoncurrent', form)
        if concept == 'minorityInterest': return None
        if concept == 'netBorrowings': return None
        if concept == 'netIncome': return self.getConceptVal('NetIncomeLoss', form)
        if concept == 'netIncomeBasic': return None
        if concept == 'netTangibleAssets': return None
        if concept == 'operatingExpense': return self.getConceptVal('OperatingExpenses', form)
        if concept == 'operatingIncome': return self.getConceptVal('OperatingIncomeLoss', form)
        if concept == 'operatingRevenue': return None
        # TODO: ask jonny if OtherAssetsNoncurrent is the right raw concept name?
        if concept == 'otherAssets': return self.getConceptVal('OtherAssetsNoncurrent', form)
        if concept == 'otherCurrentAssets': return self.getConceptVal('OtherAssetsCurrent', form)
        if concept == 'otherCurrentLiabilities': return None
        if concept == 'otherIncomeExpenseNet': return None
        # TODO: check if this variable is correct
        if concept == 'otherLiabilities': return self.getConceptVal('OtherLiabilitiesNoncurrent', form)
        if concept == 'pretaxIncome': return self.getConceptVal('IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', form)
        # NET = 'Property, Plant, & Equipment Gross' - 'Property, Plant, & Equipment Accumulated Depreciation'
        if concept == 'propertyPlantEquipment': return self.getConceptVal('PropertyPlantAndEquipmentNet', form)
        if concept == 'receivables': return self.getConceptVal('AccountsReceivableNetCurrent', form)
        if concept == 'reportDate': return self.getConceptVal('DocumentPeriodEndDate', form, type='str')
        if concept == 'researchAndDevelopment': return self.getConceptVal('ResearchAndDevelopmentExpense', form, type='str')
        if concept == 'retainedEarnings':
            return None

        if concept == 'revenue': return self.getConceptVal('SalesRevenueNet', form)

        if concept == 'sellingGeneralAndAdmin':
            return None

        if concept == 'shareholderEquity':
            return None

        if concept == 'shortTermDebt':
            return None

        if concept == 'shortTermInvestments':
            return None

        if concept == 'symbol': return self.getConceptVal('TradingSymbol', form, type='str')

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

        if concept == 'id': return 'FINANCIALS'
        if concept == 'key': return self.getConceptVal('TradingSymbol', form, type='str')
        if concept == 'subkey': return self.period
        if concept == 'updated': return time.time()
    
        # base case
        return None

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

    def get(self, asReported=False) -> dict:
        # TODO: add functionality for asReported
        return self if asReported else self.aggregateFinancials if self.aggregateFinancials != None else self.incomeStatement if self.incomeStatement != None else self.balanceSheet if self.balanceSheet != None else self.cashFlow if self.cashFlow != None else None

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