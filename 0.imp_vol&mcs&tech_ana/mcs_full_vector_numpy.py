# -*- coding: utf-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt

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

S = S0 * np.exp(np.cumsum((r-0.5*sigma**2)*dt + sigma*math.sqrt(dt)*np.random.standard_normal((M+1, I)), axis=0))
S[0] = S0
C0 = math.exp(-r * T) * np.sum(np.maximum(S[-1] - K, 0)) / I

tpy = time() - t0
print("European Option Value %7.3f" % C0)
print("Duration in seconds %7.3f" % tpy)

plt.plot(S[:, :10])
plt.grid(True)
plt.xlabel('time step')
plt.ylabel('index level')
plt.show()

plt.hist(S[-1], bins=50)
plt.grid(True)
plt.xlabel('index_level')
plt.ylabel('frequency')
plt.show()

plt.hist(np.maximum(S[-1]-K, 0), bins=50)
plt.grid(True)
plt.xlabel('option inner value')  # 期权内在价值
plt.ylabel('frequency')
plt.ylim(0, 50000)
plt.show()

print(sum(S[-1] < K))
