# This file contains some simple algorithms that screen stocks to sell puts and calls;
import datetime
import json

from configs.config import TICKERS_OF_OWNED_STOCKS
from options.stocks import Stocks


class StockScreener:
    def __init__(self, client, tickers_to_scan) -> None:
        self.tickers_to_scan = tickers_to_scan
        self.stocks = []
        self.put_sell_candidates = set()
        self.call_sell_candidates = set()
        for ticker in self.tickers_to_scan:
            quote_json = client.quote(ticker).json()
            stock = Stocks.initialize_from_quote_json(ticker, quote_json)
            stock.get_price_history(client, datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now())
            self.stocks.append(stock)
        return
    
    def day_change_larger_than_x_percent(self, x_percent: float) -> dict:
        stock_candidates = [stock for stock in self.stocks if abs(stock.percent_day_change) > x_percent]
        put_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_day_change < 0]
        call_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_day_change > 0 ]
        self.put_sell_candidates.update(set(put_sell_candidates))
        self.call_sell_candidates.update(set(call_sell_candidates))
        # since I can only sell covered calls, I only return put candidates.
        return {"put": put_sell_candidates, "call": call_sell_candidates}
    
    def week_change_larger_than_x_percent(self, x_percent: float) -> dict:
        stock_candidates = [stock for stock in self.stocks if abs(stock.percent_week_change) > x_percent]
        put_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_week_change < 0]
        call_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_week_change > 0 ]
        self.put_sell_candidates.update(set(put_sell_candidates))
        self.call_sell_candidates.update(set(call_sell_candidates))
        # since I can only sell covered calls, I only return put candidates.
        return {"put": put_sell_candidates, "call": call_sell_candidates}
    
    def month_change_larger_than_x_percent(self, x_percent: float) -> dict:
        stock_candidates = [stock for stock in self.stocks if abs(stock.percent_month_change) > x_percent]
        put_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_month_change < 0]
        call_sell_candidates = [stock.ticker for stock in stock_candidates if stock.percent_month_change > 0 ]
        self.put_sell_candidates.update(set(put_sell_candidates))
        self.call_sell_candidates.update(set(call_sell_candidates))
        # since I can only sell covered calls, I only return put candidates.
        return {"put": put_sell_candidates, "call": call_sell_candidates}
    
    def run(self, day_change=5, week_change=10, month_change=20) -> dict:
        tickers_to_sell_option_dict = self.day_change_larger_than_x_percent(x_percent=day_change)
        print(f"Day change > {day_change}%, {tickers_to_sell_option_dict}")
        tickers_to_sell_option_dict = self.week_change_larger_than_x_percent(x_percent=week_change)
        print(f"Week change > {week_change}%, {tickers_to_sell_option_dict}")
        tickers_to_sell_option_dict = self.month_change_larger_than_x_percent(x_percent=month_change)
        print(f"Month change > {month_change}%, {tickers_to_sell_option_dict}")
        return {"put": self.put_sell_candidates, "call": self.call_sell_candidates}
