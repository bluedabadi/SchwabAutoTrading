import pandas as pd
from datetime import datetime

from options.option_chains import OptionChains
from configs.utils import StockInstruction

PRICE_HISTORY_COLUMNS = [
    "date",
    "volume",
    "open",
    "high",
    "low",
    "close"
]

class Stocks(object):
    def __init__(self, position_json=None) -> None:
        self.option_chains = None
        self.price_history = None
        self.price_history_df = None
        self.percent_week_change = None
        self.percent_month_change = None
        if position_json is None:
            return
        # First make sure it is an equity;
        if position_json.get('instrument').get('assetType') != 'EQUITY':
            raise ValueError("Not an equity")
        instrument = position_json.get('instrument')
        self.ticker = instrument.get('symbol')
        self.quantity = position_json.get('longQuantity')
        self.stock_price = position_json.get('marketValue') / self.quantity
        self.percent_day_change = position_json.get('currentDayProfitLossPercentage')

    # Initialize a stock object from a quote json; for the stock that we don't have a position;
    @staticmethod
    def initialize_from_quote_json(ticker, quote_json):
        stock = Stocks()
        stock.ticker = ticker
        stock.stock_price = quote_json[ticker].get('quote').get('lastPrice')
        stock.quantity = 0
        stock.percent_day_change = quote_json[ticker].get('regular').get('regularMarketPercentChange')
        return stock


    # Store option_chains in the stocks class because one stock can have multiple options;
    # Therefore we can not store in the Options class;
    def get_option_chains(self, client) -> OptionChains:
        if self.option_chains is None:
            option_chains_json = client.option_chains(self.ticker).json()
            self.option_chains = OptionChains(option_chains_json)
        return self.option_chains
    
    def get_price_history(self, client, start_date, end_date) -> dict:
        if self.price_history is None:
            self.price_history = client.price_history(symbol=self.ticker, 
                            periodType='month', 
                            period=1, 
                            frequencyType='daily',
                            frequency=1,
                            startDate=start_date,
                            endDate=end_date
                            ).json()
        # The calculation of percent_week_change and percent_month_change are done here;
        # First convert the json file to pandas dataframe;
        self.price_history_df = pd.DataFrame.from_dict(self.price_history['candles'])
        # needs to convert the timestamp to datetime;
        self.price_history_df['date'] = self.price_history_df['datetime'].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
        self.price_history_df = self.price_history_df[PRICE_HISTORY_COLUMNS].sort_values(by='date', ascending=True)
        # calculate the last week and last month average close price;
        last_week_average_close_price = self.price_history_df['close'].iloc[-5:].mean()
        last_month_average_close_price = self.price_history_df['close'].iloc[0:].mean()
        self.percent_week_change = 100 * (self.stock_price - last_week_average_close_price) / last_week_average_close_price
        self.percent_month_change = 100 * (self.stock_price - last_month_average_close_price) / last_month_average_close_price
        # print(self.ticker, self.percent_day_change, self.percent_week_change, self.percent_month_change)

        return self.price_history
    
    @staticmethod
    def create_a_stock_order(ticker: str, quantity: int, price: float, instruction: StockInstruction = StockInstruction.BUY) -> dict:
        order = {
            "orderType": "LIMIT", 
            "session": "NORMAL", 
            "duration": "DAY", 
            "orderStrategyType": "SINGLE", 
            "price": price,
            "orderLegCollection": [{
            "instruction": str(instruction), 
            "quantity": quantity, 
            "instrument": {"symbol": ticker, "assetType": "EQUITY"}
            }]
        }
        return order