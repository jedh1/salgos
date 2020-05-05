from django.shortcuts import render
from django.http import HttpResponse
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import bokeh.layouts
from bokeh.embed import components
from bokeh.models import HoverTool
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr

from .btsingle import btsingle

# Create your views here.
def index(request):
    x1 = [ 1, 2, 3, 4, 5 ]
    y1 = [ 1, 2, 3, 4, 5 ]
    x2 = [ 1, 2, 3 ]
    y2 = [ 2, 4, 6 ]
    plot = figure(title = 'Line Graph', x_axis_label= 'X-Axis', y_axis_label= 'Y-Axis', plot_width=400, plot_height =400)
    #plot line
    plot.line( x1, y1, line_width = 2, color = "blue" )
    plot.inverted_triangle( x2, y2, line_width = 2, color = "red" )
    hover = HoverTool(tooltips=[('x', '@x'),
                                ('y', '@y')],
                            mode='vline')
    plot.add_tools(hover)

    #Store components
    script, div = components(plot)
    return render(request,'backtesting/index.html', {'script':script, 'div':div} )

def test(request):
    #input variables
    stock_in = 'TSLA'
    start_date_in = '2016-01-01'
    end_date_in = '2016-12-25'
    pfast = 10
    pslow = 50

    #run strategy
    results, roi = btsingle(stock_in, start_date_in, end_date_in, pfast, pslow)
    #obtain data from strategy
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
    plot = figure(title = 'Strategy', x_axis_label= 'Date', x_axis_type='datetime', y_axis_label= 'Price')
    plot.sizing_mode = 'stretch_both'
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

    return render(request,'backtesting/test.html', {'script':script, 'div':div, 'roi':roi})
