import backtrader as bt

# class PrintClose(bt.Strategy):
#     def __init__(self):
#         #Keep a reference to the "close" line in the data[0] dataseries
#         self.dataclose = self.datas[0].close
#
#     def log(self, txt, dt=None):
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s, %s' % (dt.isoformat(), txt)) #Print date and close
#
#     def next(self):
#         #Log closing price to 2 decimals
#         self.log('Close: %.2f' % self.dataclose[0])

class MAcrossover(bt.Strategy):
    #Moving average parameters
    params = (('pfast',20),('pslow',50),)
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        # Order variable will contain ongoing order details/status
        self.order = None
        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                        period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                        period=self.params.pfast)
        self.order_buy_history, self.order_sell_history = [], []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            #Active Buy/Sell order submitted/accepted - Nothing to do
            return
        #Check if an order has been completed
        #Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.order_buy_history.append([self.datas[0].datetime.date(0).isoformat(), order.executed.price])
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
                self.bar_executed = len(self)
                self.order_sell_history.append([self.datas[0].datetime.date(0).isoformat(), order.executed.price])
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        #Reset orders
        self.order = None

    def next(self):
        if self.order:
            return
        #Check if we are in the market
        if not self.position:
            #We are not in the market, look for a signal to OPEN trades
            #If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                #Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            #Otherwise if the 20 SMA is below the 50 SMA
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
            #Keep track of the created order to avoid a 2nd order
            self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()

# class Screener_SMA(bt.Analyzer):
#     params = (('period',20), ('devfactor',2),)
#
#     def start(self):
#         self.bband = {data: bt.indicators.BollingerBands(data, period=self.params.period, devfactor=self.params.devfactor) for data in self.datas}
#
#     def stop(self):
#         self.rets['over'] = list()
#         self.rets['under'] = list()
#
#     for data, band in self.bband.items():
#         node = data._name, data.close[0], round(band.lines.bot[0], 2)
#         if data > band.lines.bot:
#             self.rets['over'].append(node)
#         else:
#             self.rets['under'].append(node)
