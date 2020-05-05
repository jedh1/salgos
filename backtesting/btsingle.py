import datetime
import time
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from .strategies import *
from pandas_datareader import data as pdr
import yfinance as yf
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import bokeh.layouts
from bokeh.embed import components
from bokeh.models import HoverTool
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr

yf.pdr_override()

def btsingle(stock_in, start_date_in, end_date_in, pfast, pslow):
    start_time = time.time()
    cerebro = bt.Cerebro()

    #Set data parameters and add to Cerebro
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname='backtesting/stockdata/AAPL.csv',
    #     fromdate=datetime.datetime(2016, 1, 1),
    #     todate=datetime.datetime(2017, 12, 25),
    #     )
    dataframe = pdr.get_data_yahoo(stock_in, start=start_date_in, end=end_date_in)
    data = bt.feeds.PandasData(dataname = dataframe)
    cerebro.adddata(data)

    #Add strategy to Cerebro
    cerebro.addstrategy(MAcrossover, pfast=pfast, pslow=pslow)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')

    #Default position size
    cerebro.addsizer(bt.sizers.SizerFix, stake=3)


    #Run Cerebro Engine
    start_portfolio_value = cerebro.broker.getvalue()


    results = cerebro.run(tradehistory=True)

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    print('Starting Portfolio Value: %.2f' % start_portfolio_value)
    print('Final Portfolio Value: %.2f' % end_portfolio_value)
    print('PnL: %.2f' % pnl)
    print("Program took", round(time.time() - start_time,1), "seconds")
    sharpe_ratio = round(results[0].analyzers.sharpe.get_analysis()['sharperatio'], 3)

    buy_date, buy_price, sell_date, sell_price = [], [], [], []
    for item in results[0].order_buy_history:
        buy_date.append(item[0])
        buy_price.append(item[1])
    for item in results[0].order_sell_history:
        sell_date.append(item[0])
        sell_price.append(item[1])
    buy_date = pd.to_datetime(buy_date)
    sell_date = pd.to_datetime(sell_date)
    buy_source = ColumnDataSource(data=dict(
        buy_date_col = buy_date,
        buy_price_col = buy_price,
    ))
    sell_source = ColumnDataSource(data=dict(
        sell_date_col = sell_date,
        sell_price_col = sell_price,
    ))

    #plot strategy
    plot = figure(title = '', x_axis_label= 'Date', x_axis_type='datetime', y_axis_label= 'Price (US$)', plot_width=800, plot_height=400)
    # plot.sizing_mode = 'scale_both'
    plot_buy = plot.triangle(x='buy_date_col', y='buy_price_col', size = 5, color = "green", source=buy_source)
    plot_sell = plot.inverted_triangle(x='sell_date_col', y='sell_price_col', size = 5, color = "red", source=sell_source)
    hover_buy = HoverTool(
        renderers=[plot_buy],
        tooltips=[
            ('Date', '$x{%F}'),
            ('Buy price', '$@buy_price_col{%0.00f}'),
            ],
        formatters={
            '$x': 'datetime',
            '@buy_price_col' : 'printf',
        },
        mode='mouse')
    hover_sell = HoverTool(
        renderers=[plot_sell],
        tooltips=[
            ('Date', '$x{%F}'),
            ('Sell price', '$@sell_price_col{%0.00f}'),
            ],
        formatters={
            '$x': 'datetime',
            '@sell_price_col' : 'printf',
        },
        mode='mouse')
    plot.add_tools(hover_buy, hover_sell)

    #plot stock data
    stock = pdr.get_data_yahoo(stock_in, start=start_date_in, end=end_date_in)
    stock_dates = pd.to_datetime(stock.index)
    stock_close = stock['Close']
    plot_stock = plot.line(x=stock_dates, y=stock_close, line_width=1)
    script, div = components(plot)
    print(sharpe_ratio)
    return script, div, sharpe_ratio
