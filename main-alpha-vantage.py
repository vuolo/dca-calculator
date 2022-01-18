import numpy as np # numerical computing library
import pandas as pd # data science library
import json # to read from local json data
import requests # library for HTTP requests in Python
import xlsxwriter # library to write to excel
import math # math module
import os

from secrets import ALPHA_VANTAGE_API_TOKEN

symbol = 'CGC'.upper()
USE_LOCAL_DATA = False # True to use local json data saved in /data/{symbol}/; False to use API below
BASE_API_URL = f'https://www.alphavantage.co/query?apikey={ALPHA_VANTAGE_API_TOKEN}&symbol={symbol}'

# make directory: data/{symbol}
try:
    os.mkdir(f'data/{symbol}')
except OSError as error:
    pass

# make directory: data/{symbol}/excel
try:
    os.mkdir(f'data/{symbol}/excel')
except OSError as error:
    pass

# load financial statements
if USE_LOCAL_DATA:
    # load income statement
    income_statement_file = open(f'data/{symbol}/INCOME_STATEMENT.json')
    income_statement_data = json.load(income_statement_file)
    income_statement_file.close()

    # load balance sheet
    balance_sheet_file = open(f'data/{symbol}/BALANCE_SHEET.json')
    balance_sheet_data = json.load(balance_sheet_file)
    balance_sheet_file.close()

    # load cash flow
    cash_flow_file = open(f'data/{symbol}/CASH_FLOW.json')
    cash_flow_data = json.load(cash_flow_file)
    cash_flow_file.close()
else:
    # fetch income statement & save data to .json in data/{symbol}/
    income_statement_api_url = f'{BASE_API_URL}&function=INCOME_STATEMENT'
    income_statement_data = requests.get(income_statement_api_url).json()
    with open(f'data/{symbol}/INCOME_STATEMENT.json', 'w') as outfile:
        json.dump(income_statement_data, outfile)

    # fetch balance sheet & save data to .json in data/{symbol}/
    balance_sheet_api_url = f'{BASE_API_URL}&function=BALANCE_SHEET'
    balance_sheet_data = requests.get(balance_sheet_api_url).json()
    with open(f'data/{symbol}/BALANCE_SHEET.json', 'w') as outfile:
        json.dump(balance_sheet_data, outfile)

    # fetch cash flow & save data to .json in data/{symbol}/
    cash_flow_api_url = f'{BASE_API_URL}&function=CASH_FLOW'
    cash_flow_data = requests.get(cash_flow_api_url).json()
    with open(f'data/{symbol}/CASH_FLOW.json', 'w') as outfile:
        json.dump(cash_flow_data, outfile)

# ----------------------------------------------------------------------
# Begin Parameter Calculations:
# IS → Income Statement, BS → Balance Sheet, CFS → Cash Flow Statement

# init column and series
columns = ['Ticker']
series = [symbol]
parameter_answers = []
total_dca_score = 0
total_evaluated_parameters = 0

# sort financial statements in ascending order 
income_statement_data['annualReports'].reverse()
balance_sheet_data['annualReports'].reverse()
cash_flow_data['annualReports'].reverse()

# make all annual reports the same length for correct comparisons
min_length_annual_reports = min(len(income_statement_data['annualReports']), len(balance_sheet_data['annualReports']), len(cash_flow_data['annualReports']))
while len(income_statement_data['annualReports']) > min_length_annual_reports:
    income_statement_data['annualReports'].pop(0)
while len(balance_sheet_data['annualReports']) > min_length_annual_reports:
    balance_sheet_data['annualReports'].pop(0)
while len(cash_flow_data['annualReports']) > min_length_annual_reports:
    cash_flow_data['annualReports'].pop(0)

# ----------- 1. Inventory & Net Earnings (BS & CFS)
# > 1.1 Inventory and EBITDA on a steady rise. Pull Inventory and EBITDA values from the BS and CFS respectively. Check for steady increase of values over the past 4 years.
# >> +1 → I&NE on a steady and consistent rise
# > 1.2 No Research and Development (R&D) under operating expenses on IS.
# >> +1 → No R&D

# add parameter title to column
columns.append('[1.1] Steady Inventory & Net Earnings Rise?')

# get all inventory values
inventories = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    if balance_sheet_data['annualReports'][i]['inventory'] != 'None':
        inventories.append(int(balance_sheet_data['annualReports'][i]['inventory']))

# don't include inventory in calculations if the inventory isn't reported
has_inventory = 1 if len(inventories) > 0 else 0

# calculate average inventory percent change (if present)
if has_inventory:
    inventory_percent_changes = []
    for i in range(1, len(balance_sheet_data['annualReports'])):
        # validate we are comparing actual numbers and not against missing data
        if balance_sheet_data['annualReports'][i]['inventory'] == 'None' or balance_sheet_data['annualReports'][i - 1]['inventory'] == 'None':
            continue
        inventory_percent_changes.append((int(balance_sheet_data['annualReports'][i]['inventory']) - int(balance_sheet_data['annualReports'][i - 1]['inventory'])) / int(balance_sheet_data['annualReports'][i - 1]['inventory']))
    average_inventory_percent_change = sum(inventory_percent_changes) / len(inventory_percent_changes)

# calculate average ebitda percent change
ebitda_percent_changes = []
for i in range(1, len(income_statement_data['annualReports'])):
    ebitda_percent_changes.append((int(income_statement_data['annualReports'][i]['ebitda']) - int(income_statement_data['annualReports'][i - 1]['ebitda'])) / int(income_statement_data['annualReports'][i - 1]['ebitda']))
average_ebitda_percent_change = sum(ebitda_percent_changes) / len(ebitda_percent_changes)

# add parameter answer to series
if not has_inventory:
    parameter_answers.append(1 if average_ebitda_percent_change > 0 else 0)
else:
    parameter_answers.append(1 if average_inventory_percent_change > 0 and average_ebitda_percent_change > 0 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# add parameter title to column
columns.append('[1.2] No Research and Development?')

# get all research and development values
research_and_developments = []
for i in range(0, len(income_statement_data['annualReports'])):
    if income_statement_data['annualReports'][i]['researchAndDevelopment'] != 'None':
        research_and_developments.append(int(income_statement_data['annualReports'][i]['researchAndDevelopment']))

# check if company has research and development
has_research_and_development = 1 if len(research_and_developments) > 0 else 0

# add parameter answer to series
parameter_answers.append(not has_research_and_development)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 2. Earning Power (BS & CFS)
# > Over the past 4 years pull values from EBITDA on the CFS and Current Liabilities on the BS.
# >> Does the company have a history of EBITDA being able to cover Current Liabilities in a given year?
# >> (EBITDA > Current Liabilities)

# add parameter title to column
columns.append('[2] Earning Power - History of EBITDA Covering Current Liabilities?')

# get ebitdas
ebitdas = []
for i in range(0, len(income_statement_data['annualReports'])):
    ebitdas.append(int(income_statement_data['annualReports'][i]['ebitda']))

# get current liabilities
current_liabilities = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    current_liabilities.append(int(balance_sheet_data['annualReports'][i]['totalCurrentLiabilities']))

# add parameter answer to series
parameter_answers.append(1 if np.all(np.asarray(ebitdas) > np.asarray(current_liabilities)) else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 3. Property/Plant/Equipment (BS)
# > Pull values of P/P/E under long-term assets from the BS.
# >> Do the values present a steady rise with no major jumps or spikes over the past 4 years?

# add parameter title to column
columns.append('[3] Steady Rise in Property/Plant/Equipment With No Major Spikes Not Verified by Goodwill?')

# function to find outliers from a list
def get_outliers(data, m = 2.5): # the larger m is, the less outliers are removed
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.0)
    return data[s >= m].tolist()

# calculate average property/plant/equipment change
property_plant_equipment_percent_changes = []
for i in range(1, len(balance_sheet_data['annualReports'])):
    # validate we are comparing actual numbers and not against missing data
    if balance_sheet_data['annualReports'][i]['propertyPlantEquipment'] == 'None' or balance_sheet_data['annualReports'][i - 1]['propertyPlantEquipment'] == 'None':
        continue
    property_plant_equipment_percent_changes.append((int(balance_sheet_data['annualReports'][i]['propertyPlantEquipment']) - int(balance_sheet_data['annualReports'][i - 1]['propertyPlantEquipment'])) / int(balance_sheet_data['annualReports'][i - 1]['propertyPlantEquipment']))
average_property_plant_equipment_percent_change = sum(property_plant_equipment_percent_changes) / len(property_plant_equipment_percent_changes)

# calculate number of outliers (to check for no major jumps/spikes)
property_plant_equipment_outliers = get_outliers(property_plant_equipment_percent_changes)
num_outliers = len(property_plant_equipment_outliers)

# get all goodwills values
goodwills = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    if balance_sheet_data['annualReports'][i]['goodwill'] != 'None':
        goodwills.append(int(balance_sheet_data['annualReports'][i]['goodwill']))

# check if company has goodwill reported
has_goodwill = 1 if len(goodwills) > 0 else 0

# if outlier(s) present, check if goodwill also increase/decreased for the outlier's year(s)
outliers_goodwill_verified = []
if num_outliers > 0 and has_goodwill:
    try:
        for i in range(0, len(property_plant_equipment_outliers)):
            outlier_year_index = property_plant_equipment_percent_changes.index(property_plant_equipment_outliers[i])
            if outlier_year_index == 0:
                if goodwills[1] - goodwills[0] >= 1000000: # check for million dollar increase
                    outliers_goodwill_verified.append(1) # mark as verified (million dollar increase)
                else:
                    outliers_goodwill_verified.append(0) # mark as unverified
            else:
                if goodwills[outlier_year_index] - goodwills[outlier_year_index - 1] >= 1000000: # check for million dollar increase
                    outliers_goodwill_verified.append(1) # mark as verified (million dollar increase)
                else:
                    outliers_goodwill_verified.append(0) # mark as unverified
    except:
        # errors here mean we cannot goodwill verify the spike
        outliers_goodwill_verified.append(0)
    parameter_answers.append(1 if average_property_plant_equipment_percent_change > 0 and np.all(np.asarray(outliers_goodwill_verified) == 1) else 0)
else:
    parameter_answers.append(1 if average_property_plant_equipment_percent_change > 0 and num_outliers == 0 else 0)

# add parameter answer to series
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 4. Return on Total Assets (%) (BS & CFS)
# > Found through using an equation consisting of the values of EBITDA from the CFS, and Total Assets from the BS over the past 4 years.
# >> RTA = EBITDA / Total Assets
# >> The use of this formula will give you a company’s RTA for that given year.
# >> Use the equation to find the RTA for each year over the past 4 years and find the average RTA. Low RTA 0% → 10%, Good RTA 11% → 17%, Great RTA 17% and up.

# add parameter titles to column
columns.append('[4.1] Good Average Return on Total Assets (≥ 11%)?')
columns.append('[4.2] Great Average Return on Total Assets (≥ 17%)?')

# calculate return on total assets
returns_on_total_assets = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    returns_on_total_assets.append(ebitdas[i] / int(balance_sheet_data['annualReports'][i]['totalAssets']))
average_returns_on_total_assets = sum(returns_on_total_assets) / len(returns_on_total_assets)

# add 4.1 parameter answer to series
parameter_answers.append(1 if average_returns_on_total_assets >= 0.11 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# add 4.2 parameter answer to series
parameter_answers.append(1 if average_returns_on_total_assets >= 0.17 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 5. Long-Term Debt (BS & CFS)
# > Use the equation below to measure whether the company has a healthy long-term debt amount; pulling values from Long-Term Debt from the BS and Total Assets from the BS.
# >> LTD to Total Assets Ratio = LTD / Total Assets
# >> Use this equation for each year over the past 4 years and find the average.
# >> Generally speaking, a business with a healthy average ratio would result in a value of 0.5 or less.
# >> Next, Find out how long it would take (how many years) for the most recent year’s EBITDA to pay off the same year’s Long-Term Debt amount. If it can pay off the debt within 4 years it is likely to have a “DCA”.

# add parameter title to column
columns.append('[5.1] Healthy Long-Term Debt?')

# calculate average long-term debt to total assets ratio
ltd_to_ta_ratios = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    # do not include years with long term debt = 'None'
    if balance_sheet_data['annualReports'][i]['longTermDebt'] == 'None':
        # num_years_skipped_shareholders_equity += 1
        continue
    ltd_to_ta_ratios.append(int(balance_sheet_data['annualReports'][i]['longTermDebt']) / int(balance_sheet_data['annualReports'][i]['totalAssets']))
average_ltd_to_ta_ratio = sum(ltd_to_ta_ratios) / len(ltd_to_ta_ratios)

# add parameter answer to series
parameter_answers.append(1 if average_ltd_to_ta_ratio <= 0.5 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# add parameter title to column
columns.append('[5.2] EBITDA Can Pay Off Long-Term Debt Within 4 Years?')

# calculate years to pay off long-term debt
last_years_ebitda = ebitdas[-1]
last_years_ltd = int(balance_sheet_data['annualReports'][-1]['longTermDebt'])

# add parameter answer to series
parameter_answers.append(1 if last_years_ltd / last_years_ebitda <= 4 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 6. (Treasury Stock Adjusted) Debt to Shareholder’s Equity Ratio (BS)
# > If the value for Shareholder’s Equity was negative any given year over the past 4 years disregard this parameter.
# >> Over the past 4 years, pull values of Total Liabilities from the BS, Total Shareholder’s Equity from the BS, and Treasury Stock from the BS in the equation below.
# >> Adjusted DSER =Total Liabilities / (Shareholder's Equity + Treasury Stock)
# >> Companies with a “DCA” generally have adjusted DSER values of  < 1.0 (ideally < 0.8)
# >> The value for Treasury Stock will be represented as a negative number under common equity on the BS. Turn that number positive and add it to Shareholder’s Equity on the bottom side of the equation.

# add parameter title to column
columns.append('[6.1] Has Negative Shareholder\'s Equity For Any Given Year?')

# get shareholders equities
shareholders_equities = []
num_years_skipped_shareholders_equity = 0
has_negative_shareholders_equity = 0
for i in range(0, len(balance_sheet_data['annualReports'])):
    # do not include years with total shareholders equity = 'None'
    if balance_sheet_data['annualReports'][i]['totalShareholderEquity'] == 'None':
        num_years_skipped_shareholders_equity += 1
        continue
    shareholders_equities.append(int(balance_sheet_data['annualReports'][i]['totalShareholderEquity']))
    if shareholders_equities[i - num_years_skipped_shareholders_equity] < 0:
        has_negative_shareholders_equity = 1

# add parameter answer to series
parameter_answers.append(1 if has_negative_shareholders_equity else 0)
series.append('Yes; Disregard Parameters 6.2 and 6.3' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No; Continue With Parameters 6.2 to 6.3')

# add parameter title to column
columns.append('[6.2] Good Average Treasury Stock Adjusted Debt to Shareholder\'s Equity Ratio (≤ 1.0)?')

# calculate average DSER (Debt to Shareholder's Equity)
dsers = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    # validate we are comparing actual numbers and not against missing data
    if balance_sheet_data['annualReports'][i]['totalShareholderEquity'] == 'None':
        continue
    dsers.append(int(balance_sheet_data['annualReports'][i]['totalLiabilities']) / (int(balance_sheet_data['annualReports'][i]['totalShareholderEquity']) + (0 if balance_sheet_data['annualReports'][i]['treasuryStock'] == 'None' else int(balance_sheet_data['annualReports'][i]['treasuryStock']))))
average_dser = sum(dsers) / len(dsers)

# add parameter answer to series
parameter_answers.append(-1 if has_negative_shareholders_equity else 1 if average_dser <= 1.0 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
if not has_negative_shareholders_equity:
    total_dca_score += parameter_answers[-1]
    total_evaluated_parameters += 1

# add parameter title to column
columns.append('[6.3] Ideal Adjusted Treasury Stock to Debt to Shareholders Ratio (≤ 0.8)?')

# add parameter answer to series
parameter_answers.append(-1 if has_negative_shareholders_equity else 1 if average_dser <= 0.8 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
if not has_negative_shareholders_equity:
    total_dca_score += parameter_answers[-1]
    total_evaluated_parameters += 1

# ----------- 7. Preferred Stock (BS)
# > Absence of Preferred Stock under common equity on the BS.

# add parameter title to column
columns.append('[7] Absence of Preferred Stock?')

# get all preferred stocks values
preferred_stocks = []
for i in range(0, len(cash_flow_data['annualReports'])):
    if cash_flow_data['annualReports'][i]['proceedsFromIssuanceOfPreferredStock'] != 'None':
        preferred_stocks.append(int(cash_flow_data['annualReports'][i]['proceedsFromIssuanceOfPreferredStock']))

print(preferred_stocks)

# check if company has preferred stock
has_preferred_stock = 1 if len(preferred_stocks) > 0 else 0

# add parameter answer to series
parameter_answers.append(not has_preferred_stock)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 8. Retained Earnings (BS)
# > Find the percent change of the Retained Earnings pool from one year to the next over the past 4 years on the BS. (Eg. year 1 →  year 2, year 2 →  year 3, year 3 →  year 4)
# >> Next, find the growth rate by taking the average of the percent changes over the past 4 years.
# >> Good Growth Rate: x ≥ 7%
# >> Above Average Growth Rate: x ≥ 13.5%
# >> Great Growth Rate: x ≥ 17%

# add parameter titles to column
columns.append('[8.1] Good Average Retained Earnings Growth Rate (≥ 7%)?')
columns.append('[8.2] Above Average Retained Earnings Growth Rate (≥ 13.5%)?')
columns.append('[8.3] Above Average Retained Earnings Growth Rate (≥ 17%)?')

# calculate average retained earnings
retained_earnings_percent_changes = []
for i in range(1, len(balance_sheet_data['annualReports'])):
    # validate we are comparing actual numbers and not against missing data
    if balance_sheet_data['annualReports'][i]['retainedEarnings'] == 'None' or balance_sheet_data['annualReports'][i - 1]['retainedEarnings'] == 'None':
        continue
    retained_earnings_percent_changes.append((int(balance_sheet_data['annualReports'][i]['retainedEarnings']) - int(balance_sheet_data['annualReports'][i - 1]['retainedEarnings'])) / int(balance_sheet_data['annualReports'][i - 1]['retainedEarnings']))
average_retained_earnings_percent_change = sum(retained_earnings_percent_changes) / len(retained_earnings_percent_changes)

# add 8.1 parameter answer to series
parameter_answers.append(1 if average_retained_earnings_percent_change >= 0.07 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# add 8.2 parameter answer to series
parameter_answers.append(1 if average_retained_earnings_percent_change >= 0.135 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# add 8.3 parameter answer to series
parameter_answers.append(1 if average_retained_earnings_percent_change >= 0.17 else 0)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 9. Treasury Stock (BS)
# > Presence of Treasury Stock under common equity on the BS.

# add parameter title to column
columns.append('[9] Presence of Treasury Stock?')

# get all treasury stocks values
treasury_stocks = []
for i in range(0, len(balance_sheet_data['annualReports'])):
    if balance_sheet_data['annualReports'][i]['treasuryStock'] != 'None':
        treasury_stocks.append(int(balance_sheet_data['annualReports'][i]['treasuryStock']))

# check if company has treasury stock
has_treasury_stock = 1 if len(treasury_stocks) > 0 else 0

# add parameter answer to series
parameter_answers.append(has_treasury_stock)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 10. Return on Shareholder’s Equity (BS & CFS)
# > Over the past 4 years, use the values of EBITDA on the CFS and Total Shareholder’s Equity on the BS to form the equation below.
# >> RSH = EBITDA / Total Shareholder's Equity
# >> A company presenting an RSH value greater than 23%.
# >> If the company has a negative value for Total Shareholder’s Equity you need to check if it is backed by a history of strong ebitda.
# >> If it isn’t backed by this it is most likely a mediocre business so do not reward the point.

# add parameter title to column
columns.append('[10] Good Average Return on Shareholder\'s Equity? (≥ 23%)')

# calculate average return on shareholder equity
returns_on_shareholders_equity = []
for i in range(0, len(shareholders_equities)):
    returns_on_shareholders_equity.append(ebitdas[i] / shareholders_equities[i])
average_return_on_shareholders_equity = sum(returns_on_shareholders_equity) / len(returns_on_shareholders_equity)

# check if average rsh is greater than 23%
has_good_average_rsh = 1 if average_return_on_shareholders_equity >= 0.23 else 0

# if company has a negative shareholders equity AND doesn't have a 'strong' ebitda ('strong' means > 0) then DO NOT AWARD POINT
if has_good_average_rsh and has_negative_shareholders_equity:
    has_good_average_rsh = 1 if np.all(np.asarray(ebitdas) > 0) else 0

# add parameter answer to series
parameter_answers.append(has_good_average_rsh)
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')
total_dca_score += parameter_answers[-1]
total_evaluated_parameters += 1

# ----------- 11. Goodwill (BS)
# > Increasing values of Goodwill under assets on the balance sheet over the past 4 years.

# add parameter title to column
columns.append('[11] Steady Rise in Goodwill?')

if len(goodwills) <= 1:
    parameter_answers.append(-1)
else:
    # calculate average retained earnings
    goodwill_percent_changes = []
    for i in range(1, len(balance_sheet_data['annualReports'])):
        # validate we are comparing actual numbers and not against missing data
        if balance_sheet_data['annualReports'][i]['goodwill'] == 'None' or balance_sheet_data['annualReports'][i - 1]['goodwill'] == 'None':
            continue
        goodwill_percent_changes.append((int(balance_sheet_data['annualReports'][i]['goodwill']) - int(balance_sheet_data['annualReports'][i - 1]['goodwill'])) / int(balance_sheet_data['annualReports'][i - 1]['goodwill']))
    average_goodwill_percent_change = sum(goodwill_percent_changes) / len(goodwill_percent_changes)

    parameter_answers.append(1 if average_goodwill_percent_change > 0 else 0)
    total_dca_score += parameter_answers[-1]
    total_evaluated_parameters += 1

# add parameter answer to series
series.append('Yes (1/1)' if parameter_answers[-1] == 1 else 'N/A' if parameter_answers[-1] == -1 else 'No (0/1)')

# add total column at end
columns.append('Total Durable Competitve Advantage Score')
series.append(f'{total_dca_score} / {total_evaluated_parameters} ({int(total_dca_score / total_evaluated_parameters * 100)}%)')

# display total durable competitive advantage score to terminal
print(f'Total Durable Competitve Advantage Score: {total_dca_score} / {total_evaluated_parameters} ({int(total_dca_score / total_evaluated_parameters * 100)}%)')

# setup dataframe
series = pd.Series(series, index = columns)
dataframe = pd.DataFrame(columns = columns)
dataframe = dataframe.append(series, ignore_index = True)
# dataframe.transpose() # swap rows and columns (transpose)

# ----------------------------------------------------------------------
# Begin Excel Output:

writer = pd.ExcelWriter(f'data/{symbol}/excel/{symbol.lower()}-dca-parameters.xlsx', engine = 'xlsxwriter')
dataframe.to_excel(writer, sheet_name = 'DCA Parameters', index = False)

font_color = '#ffffff'
background_color = '#000000'

USE_BORDER = False
string_format = writer.book.add_format(
    {
        # 'font_color': font_color,
        # 'bg_color': background_color,
        'border': 1 if USE_BORDER else 0,
        'center_across': True
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format': '$#,##0.00',
        # 'font_color': font_color,
        # 'bg_color': background_color,
        'border': 1 if USE_BORDER else 0,
        'center_across': True
    }
)

integer_format = writer.book.add_format(
    {
        'num_format': '#,##0',
        # 'font_color': font_color,
        # 'bg_color': background_color,
        'border': 1 if USE_BORDER else 0,
        'center_across': True
    }
)

float_format = writer.book.add_format(
    {
        'num_format': '#,##0.00',
        # 'font_color': font_color,
        # 'bg_color': background_color,
        'border': 1 if USE_BORDER else 0,
        'center_across': True
    }
)

yes_no_format = writer.book.add_format(
    {
        # 'font_color': font_color,
        # 'bg_color': background_color,
        'border': 1 if USE_BORDER else 0,
        'center_across': True
    }
)

# used to dynamically allocate column formats
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# loop through columns and set format
column_formats = {}
for i in range(len(columns)):
    # dynamically setup column formats
    column_formats[ALPHABET[i % 26] * ((i // 26) + 1)] = [columns[i],
        string_format if columns[i] == 'Ticker'
        else yes_no_format
    ]

# write data to excel document with correct formats
for column in column_formats.keys():
    writer.sheets['DCA Parameters'].set_column(f'{column}:{column}', len(column_formats[column][0]), column_formats[column][1])
    writer.sheets['DCA Parameters'].write(f'{column}1', column_formats[column][0], string_format)

# save excel document
writer.save()