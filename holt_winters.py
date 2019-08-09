import numpy as np

series= [3,10, 12, 13, 12, 10, 12]

def simple_average(series):
	return np.sum(series)/len(series)

def moving_average(series, n):
	#size n sliding window
	return np.sum(series[-n:])/len(series)

def weighted_moving_average(series, weights):
	if np.sum(weights) != 1:
		return "Error! Weights should sum up to 1."
	n= len(weights)
	return np.dot(series[-n:], weights)

def single_exp_smoothing(series, alpha):
	#alpha is the smoothing factor aka starting weight to use
	#also dictates how much weight give to most recently observed vs. last expected
	#weigh the entire series
	#problem with weights not adding up
	#formula y_hat= alpha*y_x + (1-alpha)*y_hat_prev
	res= [series[0]]
	for i in range(1, len(series)):
		res.append(alpha*series[i] + (1-alpha)*res[i-1])
	return res

###################################################################
# Up until now calculating the level (l), otherwise known as expected value or y-intercept
#Trend or slope: either additive or multiplicative 
#(e.g. cost 20 more or 5% more). Multiplicative more stable. Ratio of two y values. 
# Formula: l_x= alpha*y_x + (1-alpha)*y_hat_prev
#	 	   b_x= beta(l_x- l_x_prev) + (1-beta)*b_x_prev
#		   y_hat= l_x + b_x
###################################################################
def double_exp_smoothing(series, alpha, beta):
	init_trend= [series[1]- series[0]]
	init_level= [series[0]]
	for i in range(1, len(series)):
		init_level.append(alpha*series[i] + (1-alpha)*(init_level[i-1] + init_trend[i-1]))
		init_trend.append(beta*(init_level[i]- init_level[i-1]) + (1-beta)*init_trend[i-1])
	return np.array(init_trend) + np.array(init_level)
###################################################################
#L= season length, s= season component; the part that repeats itself at the same offset into season; len(s) = L
#Formula: l_x= alpha*(y_x - s_x%L) + (1-alpha)*(l_x_prev + b_x_prev)
#		  b_x= beta*(l_x - l_x_prev) + (1-beta)*(b_x_prev)
#		  s_x%L= gamma*(y_x - l_x) + (1-gamma)*(s_x%L)
# 		  y_hat= l_x + m*b_x + s_(x+m)modL 
###################################################################
season_series = [30,21,29,31,40,48,53,47,37,39,31,29,17,9,20,24,27,
				 35,41,38,27,31,27,26,21,13,21,18,33,35,40,36,22,24,
				 21,20,17,14,17,19,26,29,40,31,20,24,18,26,17,9,17,21,
				 28,32,46,33,23,28,22,27,18,8,17,21,31,34,44,38,31,30,
				 26,32]
# m is any integer; can forecast any number of points into the future
#L= 12
def get_avg_of_trend_avg(series, L):
	#Formula: b0= 1/L*[(y_L+1- y_1)/L + (y_L+2- y_2)/L +...]
	trend_avg= []
	for i in range(L):
		trend_avg.append((series[i+L]- series[i])/L)
	trend_avg= np.sum(trend_avg)
	return 1/L*(trend_avg)

def init_season_comp(series, L):
	season_avg= []
	normalized_val= []
	res= []
	num_seasons= len(series)//L
	for i in range(num_seasons):
		season_avg.append(np.mean(series[i*L:i*L+L]))
	for i in range(num_seasons):
		#can change to np.divide here for multiplicative version
		normalized_val.append(np.subtract(series[i*L:i*L+L], season_avg[i]))
	normalized_val= np.array(normalized_val)
	for i in range(L):
		res.append(np.sum(normalized_val[:, i])/num_seasons)
	return res

def holt_winters(series, alpha, beta, gamma, L, m):
	pred= []
	for i in range(len(series) + m):
		if i==0:
			level= [series[0]]
			trend= [get_avg_of_trend_avg(series, L)]
			seasonals= init_season_comp(series, L)
			pred.append(series[0])
			continue
		elif i < len(series):
			y= series[i]
			level.append(alpha*(y-seasonals[i%L]) + (1-alpha)*(level[-1]+ trend[-1]))
			trend.append(beta*(level[i]- level[i-1]) + (1-beta)*trend[-1])
			seasonals[i%L]= (gamma*(y-level[-1]) + (1-gamma)*seasonals[i%L])	
			pred.append(level[-1]+ trend[-1] + seasonals[i%L])
		else:
			m= i-len(series) + 1
			pred.append(level[-1] + m*trend[-1] + seasonals[i%L])	
	return pred	
