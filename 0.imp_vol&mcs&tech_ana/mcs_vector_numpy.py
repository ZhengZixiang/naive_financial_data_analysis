# -*- coding: utf-8 -*-
"""
Mote-Carlo Simulation with vector
"""
import numpy as np

from math import exp, sqrt, log
from time import time

t0 = time()
np.random.seed(20000)
S0 = 100.0
K = 105.0
T = 1.0
r = 0.05
sigma = 0.2
M = 50
dt = T / M
I = 250000

S = np.zeros((M+1, I))
S[0] = S0
for t in range(1, M+1):
    z = np.random.standard_normal(I)
    S[t] = S[t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * z)

C0 = exp(-r * T) * np.sum(np.maximum(S[-1] - K, 0)) / I
tpy = time() - t0
print("European Option Value %7.3f" % C0)
print("Duration in seconds %7.3f" % tpy)
