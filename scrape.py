from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from re import sub
from decimal import Decimal
import numpy as np 

cash_url='https://www.macrotrends.net/stocks/charts/AAPL/apple/cash-flow-statement'
income_url= 'https://www.macrotrends.net/stocks/charts/AAPL/apple/income-statement?freq=A'
stats_url= "https://finance.yahoo.com/quote/AAPL/key-statistics?p=AAPL"

interest_url="https://finance.yahoo.com/quote/AAPL/financials?p=AAPL"

options = Options()
options.add_argument("--headless")
browser= webdriver.Chrome('/Users/kimberlyzhang/Documents/chromedriver', options=options)

def currency_to_num(currency):
	return sub(r'[^\d.]', '', currency)

def billion_to_e(num):
	return Decimal(sub(r'B', 'e9', num))

def collect_fcf_data(url, browser):
	browser.get(url)
	soup= BeautifulSoup(browser.page_source, 'lxml')
	op_cash_row= soup.select('#row9jqxgrid > div:nth-child(n+3) > div')
	capex_row= soup.select('#row10jqxgrid > div:nth-child(n+3) > div')
	op_cash= [Decimal(currency_to_num(i.get_text()) + 'e6') for i in op_cash_row]
	capex= [Decimal(currency_to_num(i.get_text())+'e6') for i in capex_row]
	return np.array(op_cash), np.array(capex)

def collect_terminal_val_data(url, browser):
	browser.get(url)
	soup= BeautifulSoup(browser.page_source, 'lxml')
	revenue_row= soup.select('#row0jqxgrid > div:nth-child(n+3) > div')
	ebitda_row= soup.select('#row16jqxgrid > div:nth-child(n+3) > div')
	revenue= [Decimal(currency_to_num(i.get_text()) + 'e6') for i in revenue_row]
	ebitda= [Decimal(currency_to_num(i.get_text()) + 'e6') for i in ebitda_row]
	return np.array(revenue), np.array(ebitda)

def get_financial_stats(url, browser):
	browser.get(url)
	soup= BeautifulSoup(browser.page_source, 'lxml')
	targets= ["Market Cap (intraday)", "PEG Ratio (5 yr expected)", "Enterprise Value/EBITDA", "Total Debt", "Beta (3Y Monthly)", "50-Day Moving Average", "200-Day Moving Average"]
	res= {}
	stored= soup.find_all('td')
	for i, val in enumerate(stored):
		if len(res.keys()) == len(targets):
			break
		text= val.find("span")
		if text and text.get_text() in targets:
			res[text.get_text()]= billion_to_e(stored[i+1].get_text())
	return res

def get_interest_expense(url, browser):
	browser.get(url)
	soup= BeautifulSoup(browser.page_source, 'lxml')
	stored= soup.find_all('td')
	res= {}
	for i, val in enumerate(stored):
		text= val.get_text()
		if text == 'Interest Expense':
			res[text]= Decimal(currency_to_num(stored[i+1].get_text()) + 'e3')
			break
	return res



