from __future__ import division
from sys import exit
from math import sqrt
from numpy import array
from scipy.optimize import fmin_l_bfgs_b
from pandas import read_csv

def RMSE(params, *args):

	Y = args[0]
	type = args[1]
	rmse = 0

	alpha, beta, gamma = params
	m = args[2]
	a = [sum(Y[0:m]) / float(m)] # 为0的情况
	b = [(sum(Y[m:2 * m]) - sum(Y[0:m])) / m ** 2]

	if type == 'a':

		s = [Y[i] - a[0] for i in range(m)]
		y = [a[0] + b[0] + s[0]]

		for i in range(len(Y)):

			a.append(alpha * (Y[i] - s[i]) + (1 - alpha) * (a[i] + b[i]))
			b.append(beta * (a[i + 1] - a[i]) + (1 - beta) * b[i])
			s.append(gamma * (Y[i] - a[i] - b[i]) + (1 - gamma) * s[i])
			y.append(a[i + 1] + b[i + 1] + s[i + 1])

	elif type == 'm':

		s = [Y[i] / a[0] for i in range(m)]
		y = [(a[0] + b[0]) * s[0]]

		for i in range(len(Y)):

			a.append(alpha * (Y[i] / s[i]) + (1 - alpha) * (a[i] + b[i]))
			b.append(beta * (a[i + 1] - a[i]) + (1 - beta) * b[i])
			s.append(gamma * (Y[i] / (a[i] + b[i])) + (1 - gamma) * s[i])
			y.append((a[i + 1] + b[i + 1]) * s[i + 1])

	else:

		exit('Type must be either linear, additive or multiplicative')

	rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(Y, y[:-1])]) / len(Y))

	return rmse

Y = [2,4,8,0,2,5,0,0,0,0,0,0,3,6,4,6,4,17,10,8,21,17,27,15,21,31,35,43,70,66,68,60,39,51,36,33,24,15,21,17,10,22,12,9,22,29,10,4]
m = 24
initial_values = array([0.3, 0.1, 0.1])
boundaries = [(0, 1), (0, 1), (0, 1)]
type = 'a' # 加性

param = fmin_l_bfgs_b(RMSE, x0 = initial_values, args = (Y, type, m), bounds = boundaries, approx_grad = True)
print(param[:2])