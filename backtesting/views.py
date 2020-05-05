from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from bokeh.plotting import figure, output_file, show, ColumnDataSource
import bokeh.layouts
from bokeh.embed import components
from bokeh.models import HoverTool
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr
from .forms import sma_search

from .btsingle import btsingle

# Create your views here.
def index(request):
    # If form is filled:
    if request.method == 'POST':
        form = sma_search(request.POST)
        if form.is_valid():
            # Create Search object
            stock_in = form.cleaned_data.get('ticker')
            start_date_in = form.cleaned_data.get('start_date')
            end_date_in = form.cleaned_data.get('end_date')
            pfast = form.cleaned_data.get('sma_fast')
            pslow = form.cleaned_data.get('sma_slow')
            error_count = 0

            #check form is valid:
            if start_date_in >= end_date_in:
                messages.error(request, 'Form error: End date must be later than start date,')
                error_count += 1

            if pfast >= pslow:
                messages.error(request, 'Form error: SMA, fast must be less than SMA, slow.')
                error_count += 1

            if error_count > 0:
                error_count = 0
                return redirect('index')

            try:
                script, div, sr = btsingle(stock_in, start_date_in, end_date_in, pfast, pslow)
            except:
                messages.error(request, 'Form error')
                return redirect('index')

            return render(request,'backtesting/test.html', {'script':script, 'div':div, 'sr':sr, 'ticker': stock_in.upper(), 'fsma': pfast, 'ssma': pslow})
    # initial form screen
    else:
        form = sma_search()
    return render(request, 'backtesting/index.html', {'form': form})

    #Store components
    script, div = components(plot)
    return render(request,'backtesting/index.html', {'script':script, 'div':div} )

def about(request):
    return render(request,'backtesting/about.html',)

def ex1(request):
    #input variables
    stock_in = 'TSLA'
    start_date_in = '2016-01-01'
    end_date_in = '2017-12-25'
    pfast = 7
    pslow = 66
    #run strategy
    script, div, sharpe_ratio = btsingle(stock_in, start_date_in, end_date_in, pfast, pslow)
    return render(request,'backtesting/test.html', {'script':script, 'div':div, 'sr':sharpe_ratio, 'ticker': stock_in, 'fsma': pfast, 'ssma': pslow})

def ex2(request):
    #input variables
    stock_in = 'SPY'
    start_date_in = '2016-01-01'
    end_date_in = '2019-12-25'
    pfast = 50
    pslow = 200
    #run strategy
    script, div, sharpe_ratio = btsingle(stock_in, start_date_in, end_date_in, pfast, pslow)
    return render(request,'backtesting/test.html', {'script':script, 'div':div, 'sr':sharpe_ratio, 'ticker': stock_in, 'fsma': pfast, 'ssma': pslow})
