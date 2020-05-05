import datetime
import time
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from datetime import date
from strategies import *

cerebro = bt.Cerebro(optreturn=False)

#Set data parameters and add to Cerebro
data = bt.feeds.YahooFinanceCSVData(
    dataname='stockdata/spy.csv',
    fromdate=datetime.datetime(2015, 1, 2),
    todate=datetime.datetime(2016, 12, 23))
cerebro.adddata(data)

#Add strategy to Cerebro
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
cerebro.optstrategy(MAcrossover, pfast=range(5,
30), pslow=range(50, 150))

#Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == '__main__':
    optimized_runs = cerebro.run()

    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 10000,2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append([strategy.params.pfast,
                strategy.params.pslow, PnL, sharpe['sharperatio']])

    sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3],
        reverse=True)
    for line in sort_by_sharpe[:5]:
        print(line)
