# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import time

from datetime import datetime
from math import log, sqrt, exp
from scipy import stats


def bsm_call_value(S0, K, T, r, sigma):
    """
    期权报价
    :param S0: 标的资产在0时刻的价格水平
    :param K: 期权的执行价格
    :param T: 期权的到期期限
    :param r: 常数的无风险短期利率
    :param sigma: 资产常数的隐含波动率（标准差）
    """
    S0 = float(S0)
    d1 = (log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = (log(S0 / K) + (r - 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    value = (S0 * stats.norm.cdf(d1, 0.0, 1.0) - K * exp(-r * T) * stats.norm.cdf(d2, 0.0, 1.0))
    return value


def bsm_vega(S0, K, T, r, sigma):
    """
    期权定价公式关于波动率的一阶导数称为期权的Vega
    """
    S0 = float(S0)
    d1 = (log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    vega = S0 * stats.norm.pdf(d1, 0.0, 1.0) * sqrt(T)
    return vega


def bsm_call_imp_vol(S0, K, T, r, C0, sigma_est, iter=100):
    """
    求隐含波动率

    :param C0: 欧式看涨期权价格
    :param sigma_est: sigma迭代初值
    :param iter: 迭代次数
    """
    for i in range(iter):
        sigma_est -= ((bsm_call_value(S0, K, T, r, sigma_est) - C0)
            / bsm_vega(S0, K, T, r, sigma_est))
    return sigma_est


if __name__ == '__main__':
    V0 = 17.6639
    r = 0.01

    h5 = pd.HDFStore('../resource/vstoxx_data_31032014.h5')
    futures_data = h5['futures_data']  # 期货价格 一个到期日一份合约
    options_data = h5['options_data']  # 期权数据 到期日和执行价格
    h5.close()

    # print(futures_data)
    # print(options_data.info())
    # print(options_data[['DATE', 'MATURITY', 'TTM', 'STRIKE', 'PRICE']].head())

    # 对每一个期权合约计算imp_vol，要求期权的执行价格不远离forward price
    # 执行价格不能定价错误 F(1-tol) < K < F(1+tol)
    options_data['IMP_VOL'] = 0.0
    tol = 0.5  # tolerance
    for option in options_data.index:
        forward = futures_data[futures_data['MATURITY'] ==
                               options_data.loc[option]['MATURITY']]['PRICE'].values[0]
        if forward * (1-tol) < options_data.loc[option]['STRIKE'] < forward * (1 + tol):
            imp_vol = bsm_call_imp_vol(V0,
                                       options_data.loc[option]['STRIKE'],
                                       options_data.loc[option]['TTM'],
                                       r,
                                       options_data.loc[option]['PRICE'],
                                       sigma_est=2.,
                                       iter=100)
            options_data['IMP_VOL'].loc[option] = imp_vol

    plot_data = options_data[options_data['IMP_VOL'] > 0]
    maturites = sorted(set(options_data['MATURITY']))

    plt.figure(figsize=(8, 6))
    for maturity in maturites:  # 迭代到期日
        data = plot_data[options_data['MATURITY'] == maturity]
        plt.plot(data['STRIKE'], data['IMP_VOL'], 'r.', label='_nolegend_')  # setting label='' also works
        plt.plot(data['STRIKE'], data['IMP_VOL'], label=pd.Timestamp(maturity).date(), lw=1.5)
    plt.grid(True)
    plt.xlabel('Strike')
    plt.ylabel('Implied volatility of volatility')
    plt.legend()
    plt.show()

    keep = ['PRICE', 'IMP_VOL']
    group_data = plot_data.groupby(['MATURITY', 'STRIKE'])[keep]
    # print(group_data)
    group_data = group_data.sum()
    print(group_data)
