# -*- coding: utf-8 -*-
"""
Mote-Carlo Simulation with pure python
"""
from time import time
from math import exp, sqrt, log
from random import gauss, seed

seed(20000)
t0 = time()
S0 = 100
K = 100.
T = 1.0
r = 0.05
sigma = 0.2
M = 50  # 时间段数
dt = T / M
I = 250000  # 路径数

S = []
for i in range(I):
    path = []  # 生成新的路径
    for t in range(M + 1):
        if t == 0:
            path.append(S0)
        else:
            z = gauss(0.0, 1.0)  # 布朗运动
            St = path[t-1] * exp((r - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * z)
            path.append(St)
    S.append(path)

C0 = exp(-r * T) * sum([max(path[-1]-K, 0) for path in S]) / I

tpy = time() - t0
print("European Option Value %7.3f" % C0)
print("Duration in seconds %7.3f" % tpy)
