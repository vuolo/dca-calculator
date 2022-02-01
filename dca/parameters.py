import pandas as pd # data science library
from edgar.financials import Financials

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

        # ----------- 1. Inventory & Net Earnings
        # [1.1] Steady Inventory & Net Earnings Rise?
        # > Pull Inventory and EBITDA values from the BS and CFS respectively.
        # > Check for steady increase of values over the past 4 years.
        # >> SCORING: +1 → I&NE on a steady and consistent rise
        # [1.2] No Research and Development?
        # > No Research and Development (R&D) under operating expenses on IS.
        # >> SCORING: +1 → No R&D

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

        # add total column at end
        self.columns.append('Total Durable Competitve Advantage Score')
        self.series.append(f'{self.totalDCAScore} / {self.totalEvaluatedParameters} ({int(self.totalDCAScore / self.totalEvaluatedParameters * 100)}%)')

        # TODO: remove this... display total durable competitive advantage score to terminal
        print(f'Total Durable Competitve Advantage Score: {self.totalDCAScore} / {self.totalEvaluatedParameters} ({int(self.totalDCAScore / self.totalEvaluatedParameters * 100)}%)')

        # setup dataframe
        self.series = pd.Series(self.series, index = self.columns)
        self.result = pd.DataFrame(columns = self.columns)
        self.result = self.result.append(self.series, ignore_index = True)

    def getResults(self) -> pd.DataFrame:
        return self.result