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

def double_exp_smoothing(series):
	pass

def holt_winters(series):
	pass
