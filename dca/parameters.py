import numpy as np # numerical computing library
import pandas as pd # data science library
from edgar.financials import Financials

# function to find outliers from a list
def get_outliers(data, m = 2.5): # the larger m is, the less outliers are removed
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.0)
    return data[s >= m].tolist()

class Parameters():

    def __init__(self, financials: Financials) -> None:
        self.financials = financials
        self.runParameters()

    def runParameters(self) -> None:
        # init helpful vars
        self.result = pd.DataFrame()
        self.aggregateFinancials = self.financials.getFinancials()
        self.financialStatements = self.aggregateFinancials['financials']
        self.columns = ['Ticker']
        self.series = [self.aggregateFinancials['ticker']]
        self.parameterAnswers = []
        self.totalDCAScore = 0
        self.totalEvaluatedParameters = 0

        # sort financial statements in ascending order to aid calculations
        self.financialStatements.reverse()

        # calculate dca parameters
        self.calcParameter1() # 1. Inventory & Net Earnings
        self.calcParameter2() # 2. Earning Power
        self.calcParameter3() # 3. Property/Plant/Equipment
        self.calcParameter4() # 4. Return on Total Assets
        self.calcParameter5() # 5. Long-Term Debt
        self.calcParameter6() # 6. (Treasury Stock Adjusted) Debt to Shareholder’s Equity Ratio
        self.calcParameter7() # 7. Preferred Stock
        self.calcParameter8() # 8. Retained Earnings
        self.calcParameter9() # 9. Treasury Stock
        self.calcParameter10() # 10. Return on Shareholder’s Equity
        self.calcParameter11() # 11. Goodwill

        # finalize results DataFrame
        self.finalizeResults()

    # ----------- 1. Inventory & Net Earnings
    # [1.1] Steady Inventory & Net Earnings Rise?
    # > Pull Inventory and EBITDA values from the BS and CFS respectively.
    # > Check for steady increase of values over the past 4 years.
    # >> SCORING: +1 → I&NE on a steady and consistent rise
    # [1.2] No Research and Development?
    # > No Research and Development (R&D) under operating expenses on IS.
    # >> SCORING: +1 → No R&D
    def calcParameter1(self) -> None:
        # add parameter title to column
        self.columns.append('[1.1] Steady Inventory & Net Earnings Rise?')

        # get all inventory values
        inventories = []
        for statement in self.financialStatements:
            if statement['inventory']:
                inventories.append(statement['inventory'])
                
        # don't include inventory in calculations if the inventory isn't reported
        hasInventory = 1 if len(inventories) > 0 else 0

        # calculate average inventory percent change (if present)
        if hasInventory:
            inventoryPercentChanges = []
            for i in range(1, len(self.financialStatements)):
                # validate we are comparing actual numbers and not against missing data
                if not self.financialStatements[i]['inventory'] or not self.financialStatements[i - 1]['inventory']: continue

                # calculate & append inventory percent changes
                inventoryPercentChanges.append((self.financialStatements[i]['inventory'] - self.financialStatements[i - 1]['inventory']) / self.financialStatements[i - 1]['inventory'])
            averageInventoryPercentChange = sum(inventoryPercentChanges) / len(inventoryPercentChanges)

        # calculate average ebitda percent change
        ebitdaPercentChanges = []
        for i in range(1, len(self.financialStatements)):
            # validate we are comparing actual numbers and not against missing data
            if not self.financialStatements[i]['EBITDA'] or not self.financialStatements[i - 1]['EBITDA']: continue

            # calculate & append ebitda percent changes
            ebitdaPercentChanges.append((self.financialStatements[i]['EBITDA'] - self.financialStatements[i - 1]['EBITDA']) / self.financialStatements[i - 1]['EBITDA'])
        averageEbitdaPercentChange = sum(ebitdaPercentChanges) / len(ebitdaPercentChanges)

        # add parameter answer to series
        if not hasInventory:
            self.parameterAnswers.append(1 if averageEbitdaPercentChange > 0 else 0)
        else:
            self.parameterAnswers.append(1 if averageInventoryPercentChange > 0 and averageEbitdaPercentChange > 0 else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

        # add parameter title to column
        self.columns.append('[1.2] No Research and Development?')

        # get all research and development values
        researchAndDevelopments = []
        for statement in self.financialStatements:
            if statement['researchAndDevelopment']:
                researchAndDevelopments.append(statement['researchAndDevelopment'])

        # check if company has research and development
        hasResearchAndDevelopment = 1 if len(researchAndDevelopments) > 0 else 0

        # add parameter answer to series
        self.parameterAnswers.append(not hasResearchAndDevelopment)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

    # ----------- 2. Earning Power
    # [2] Earning Power - History of EBITDA Covering Current Liabilities?
    # > Over the past 4 years pull values from EBITDA on the CFS and Current Liabilities on the BS.
    # > Does the company have a history of EBITDA being able to cover Current Liabilities in a given year?
    # >> SCORING: +1 → EBITDA > Current Liabilities
    def calcParameter2(self) -> None:
        # add parameter title to column
        self.columns.append('[2] Earning Power - History of EBITDA Covering Current Liabilities?')

        # get ebitdas & current liabilities
        ebitdas = []
        currentLiabilities = []
        for statement in self.financialStatements:
            if statement['EBITDA']:
                ebitdas.append(statement['EBITDA'])
            if statement['currentLiabilities']:
                currentLiabilities.append(statement['currentLiabilities'])

        # add parameter answer to series
        self.parameterAnswers.append(1 if np.all(np.asarray(ebitdas) > np.asarray(currentLiabilities)) else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1
    
    # ----------- 3. Property/Plant/Equipment
    # [3] Steady Rise in Property/Plant/Equipment With No Major Spikes Not Verified by Goodwill?
    # > Pull values of P/P/E under long-term assets from the BS.
    # > Do the values present a steady rise with no major jumps or spikes over the past 4 years?
    # > If there are major spikes, are the years with major spikes covered by a spike in goodwill?
    # >> SCORING: +1 → PPE on a steady rise with no major acquisitions
    def calcParameter3(self) -> None:
        # add parameter title to column
        self.columns.append('[3] Steady Rise in Property/Plant/Equipment With No Major Spikes Not Verified by Goodwill?')

        # calculate average property/plant/equipment change
        propertyPlantEquipmentPercentChanges = []
        for i in range(1, len(self.financialStatements)):
            # validate we are comparing actual numbers and not against missing data
            if not self.financialStatements[i]['propertyPlantEquipment'] or not self.financialStatements[i - 1]['propertyPlantEquipment']: continue

            # calculate & append ppe percent changes
            propertyPlantEquipmentPercentChanges.append((self.financialStatements[i]['propertyPlantEquipment'] - self.financialStatements[i - 1]['propertyPlantEquipment']) / self.financialStatements[i - 1]['propertyPlantEquipment'])
        averagePropertyPlantEquipmentPercentChange = sum(propertyPlantEquipmentPercentChanges) / len(propertyPlantEquipmentPercentChanges)

        # calculate number of outliers (to check for no major jumps/spikes)
        propertyPlantEquipmentOutliers = get_outliers(propertyPlantEquipmentPercentChanges, m=2.5)
        numOutliers = len(propertyPlantEquipmentOutliers)

        # get all goodwills values
        goodwills = []
        for statement in self.financialStatements:
            if statement['goodwill']:
                goodwills.append(statement['goodwill'])

        # check if company has goodwill reported
        hasGoodwill = 1 if len(goodwills) > 0 else 0

        # if outlier(s) present, check if goodwill also increase/decreased for the outlier's year(s)
        outliersGoodwillVerified = []
        if numOutliers > 0 and hasGoodwill:
            try:
                for i in range(0, len(propertyPlantEquipmentOutliers)):
                    outlier_year_index = propertyPlantEquipmentPercentChanges.index(propertyPlantEquipmentOutliers[i])
                    if outlier_year_index == 0:
                        if goodwills[1] - goodwills[0] >= 1000000: # check for at least million dollar increase
                            outliersGoodwillVerified.append(1) # mark as verified (million dollar increase)
                        else:
                            outliersGoodwillVerified.append(0) # mark as unverified
                    else:
                        if goodwills[outlier_year_index] - goodwills[outlier_year_index - 1] >= 1000000: # check for million dollar increase
                            outliersGoodwillVerified.append(1) # mark as verified (million dollar increase)
                        else:
                            outliersGoodwillVerified.append(0) # mark as unverified
            except:
                # errors here mean we cannot goodwill verify the spike...
                outliersGoodwillVerified.append(0)
            self.parameterAnswers.append(1 if averagePropertyPlantEquipmentPercentChange > 0 and np.all(np.asarray(outliersGoodwillVerified) == 1) else 0)
        else:
            self.parameterAnswers.append(1 if averagePropertyPlantEquipmentPercentChange > 0 and numOutliers == 0 else 0)

        # add parameter answer to series
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

    # ----------- 4. Return on Total Assets
    # [4.1] Good Average Return on Total Assets (≥ 11%)?
    # > Found through using an equation consisting of the values of EBITDA from the CFS, and Total Assets from the BS over the past 4 years.
    # > RTA = EBITDA / Total Assets
    # > The use of this formula will give you a company’s RTA for that given year.
    # > Use the equation to find the RTA for each year over the past 4 years and find the average RTA. Low RTA 0% → 10%, Good RTA 11% → 17%, Great RTA 17% and up.
    # >> SCORING: +1 → RTA ≥ 11%
    # [4.2] Great Average Return on Total Assets (≥ 17%)?
    # >> SCORING: +1 → RTA ≥ 17%
    def calcParameter4(self) -> None:
        # add parameter titles to column
        self.columns.append('[4.1] Good Average Return on Total Assets (≥ 11%)?')
        self.columns.append('[4.2] Great Average Return on Total Assets (≥ 17%)?')

        # calculate return on total assets
        returnsOnTotalAssets = []
        for statement in self.financialStatements:
            if statement['EBITDA'] and statement['totalAssets']:
                returnsOnTotalAssets.append(statement['EBITDA'] / statement['totalAssets'])
        averageReturnsOnTotalAssets = sum(returnsOnTotalAssets) / len(returnsOnTotalAssets)

        # add 4.1 parameter answer to series
        self.parameterAnswers.append(1 if averageReturnsOnTotalAssets >= 0.11 else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

        # add 4.2 parameter answer to series
        self.parameterAnswers.append(1 if averageReturnsOnTotalAssets >= 0.17 else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

    # ----------- 5. Long-Term Debt
    # [5.1] Healthy Long-Term Debt?
    # > Use the equation below to measure whether the company has a healthy long-term debt amount; pulling values from Long-Term Debt from the BS and Total Assets from the BS.
    # > LTD to Total Assets Ratio = LTD / Total Assets
    # > Use this equation for each year over the past 4 years and find the average.
    # > Generally speaking, a business with a healthy average ratio would result in a value of 0.5 or less.
    # > Next, Find out how long it would take (how many years) for the most recent year’s EBITDA to pay off the same year’s Long-Term Debt amount. If it can pay off the debt within 4 years it is likely to have a “DCA”.
    # >> SCORING: +1 → LTD to Total Assets ratio ≤ 0.5 (50%).
    # [5.2] EBITDA Can Pay Off Long-Term Debt Within 4 Years?
    # >> SCORING: +1 → EBITDA can pay off LTD within 3 to 4 years assuming the same EBITDA for the following years.
    def calcParameter5(self) -> None:
        # add parameter title to column
        self.columns.append('[5.1] Healthy Long-Term Debt?')

        # calculate average long-term debt to total assets ratio
        LTDToTARatios = []
        for statement in self.financialStatements:
            # validate we are comparing actual numbers and not against missing data
            if not statement['longTermDebt']: continue

            # calculate & append ltd to ta ratios
            LTDToTARatios.append(statement['longTermDebt'] / statement['totalAssets'])
        averageLTDToTARatio = sum(LTDToTARatios) / len(LTDToTARatios)

        # add parameter answer to series
        self.parameterAnswers.append(1 if averageLTDToTARatio <= 0.5 else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

        # add parameter title to column
        self.columns.append('[5.2] EBITDA Can Pay Off Long-Term Debt Within 4 Years?')

        # calculate years to pay off long-term debt
        lastYearsEBITDA = self.financialStatements[-1]['EBITDA']
        lastYearsLTD = self.financialStatements[-1]['longTermDebt']

        # add parameter answer to series
        self.parameterAnswers.append(1 if lastYearsLTD / lastYearsEBITDA <= 4 else 0)
        self.series.append('Yes (1/1)' if self.parameterAnswers[-1] == 1 else 'N/A' if self.parameterAnswers[-1] == -1 else 'No (0/1)')
        self.totalDCAScore += self.parameterAnswers[-1]
        self.totalEvaluatedParameters += 1

    def calcParameter6(self) -> None:
        return

    def calcParameter7(self) -> None:
        return

    def calcParameter8(self) -> None:
        return

    def calcParameter9(self) -> None:
        return
        
    def calcParameter10(self) -> None:
        return

    def calcParameter11(self) -> None:
        return

    def finalizeResults(self) -> None:
        # add total column at end
        self.columns.append('Total Durable Competitve Advantage Score')
        self.series.append(f'{self.totalDCAScore} / {self.totalEvaluatedParameters} ({int(self.totalDCAScore / self.totalEvaluatedParameters * 100)}%)')

        # TODO: remove this... display total durable competitive advantage score to terminal
        # print(f'Total Durable Competitve Advantage Score: {self.totalDCAScore} / {self.totalEvaluatedParameters} ({int(self.totalDCAScore / self.totalEvaluatedParameters * 100)}%)')

        # setup dataframe
        self.series = pd.Series(self.series, index = self.columns)
        self.result = pd.DataFrame(columns = self.columns)
        self.result = self.result.append(self.series, ignore_index = True)

    def getResults(self) -> pd.DataFrame:
        return self.result