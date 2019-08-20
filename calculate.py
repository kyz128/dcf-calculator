import numpy as np
from scrape import *
from decimal import Decimal
from time_pred import *
from scipy.optimize import minimize

op_cash, capex= collect_fcf_data(cash_url, browser)
fcf= op_cash-capex
revenue, ebitda= collect_terminal_val_data(income_url, browser)
ebitda_margin= ebitda/revenue
stats= get_financial_stats(stats_url, browser)
interest= get_interest_expense(interest_url, browser)

def get_growth_rates(ebitda_margin):
	growth_rates= []
	for i in range(1, len(ebitda_margin)):
		diff= (ebitda_margin[i] - ebitda_margin[i-1])
		growth_rates.append(diff/ebitda_margin[i-1])
	return np.array(growth_rates)

def get_wacc(e, d, tax_rate, beta, krf, rp, interest):
	equity_portion= e/(d+e)
	debt_portion= d/(d+e)
	equity_cost= beta*rp + krf
	debt_cost= (interest/d)*(1-tax_rate)
	return equity_cost*equity_portion + debt_cost*debt_portion

def caculate_terminal_val(g, last_fcf, wacc):
	return last_fcf*(1+g)/(wacc-g)


def mse(params, series):
	alpha, beta= params[0], params[1]
	preds= double_exp_smoothing(series, alpha, beta)
	return np.mean((preds-series)**2)

g= np.mean(get_growth_rates(ebitda_margin))
beta= stats['Beta (3Y Monthly)']
shares= stats['Shares Outstanding']
tax_rate= Decimal(.21)
e= stats['Market Cap (intraday)']
d= stats['Total Debt']
rp= Decimal(0.06)
krf= Decimal(0.02)
interest= interest['Interest Expense']
wacc= get_wacc(e, d, tax_rate, beta, krf, rp, interest)
# Find optimal alpha and beta for time series prediction
guess= [1.0, 1.0]
res= minimize(mse, guess, args= (np.log(fcf.astype(float)),), bounds= ((0,1), (0,1)), method='SLSQP')
a, b= res.x
# Get forecasted fcf 
preds= double_exp_smoothing(fcf.astype(float), a, b)
terminal_value= caculate_terminal_val(float(g), preds[-1], float(wacc))
intrinsic_val= np.sum(preds) + terminal_value
estimated_share= float(intrinsic_val)/float(shares)
print(estimated_share)