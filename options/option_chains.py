import json
import datetime
import pandas as pd

from configs.config import BID_ASK_SPREAD_MAX, VOLUME_INTEREST_MIN, ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE
from configs.utils import OptionType

OPTION_CHAINS_COLUMNS =[
    "symbol",
    "ticker",
    "stock_price",
    "expiration_date",
    "option_type",
    "strike_price",
    "option_price",
    "delta",
    "gamma",
    "theta",
    "vega",
    "bid",
    "ask",
    "totalVolume",
    "openInterest",
]
EXISTING_OPTION_CHAINS_COLUMNS = [
    "symbol",
    "delta",
    "gamma",
    "theta",
    "vega",
    "bid",
    "ask",
    "totalVolume",
    "openInterest",
]


class OptionChains(object):
    def __init__(self, option_chains_json) -> None:
        self.option_chains_json = option_chains_json
        self.call_option_chains_json = option_chains_json.get('callExpDateMap')
        self.put_option_chains_json = option_chains_json.get('putExpDateMap')
        # build a pandas dataframe with the option chains json for both put and call options
        self.option_chains_df = pd.DataFrame(columns=OPTION_CHAINS_COLUMNS)
        option_chain_dict_list = []
        for option_chains in [self.call_option_chains_json, self.put_option_chains_json]:
            for expiration_date_key in option_chains.keys():
                expiration_date_value = datetime.datetime.strptime(expiration_date_key[:10], '%Y-%m-%d')
                option_chains_for_date = option_chains[expiration_date_key]
                for strike_key in option_chains_for_date.keys():
                    option_chains_for_date_and_strike = option_chains_for_date[strike_key][0]
                    # create a new dictionary with a subset of the keys in the option_chains_for_date_and_strike
                    option_chain_dict = {key: option_chains_for_date_and_strike[key] for key in EXISTING_OPTION_CHAINS_COLUMNS}
                    option_chain_dict['ticker'] = option_chains_json["symbol"]
                    option_chain_dict['stock_price'] = option_chains_json["underlyingPrice"]
                    option_chain_dict['expiration_datetime'] = expiration_date_value
                    option_chain_dict['strike_price'] = float(strike_key)
                    option_chain_dict['option_price'] = (option_chain_dict['bid'] + option_chain_dict['ask'])/2
                    option_chain_dict['option_type'] = OptionType.CALL if option_chains == self.call_option_chains_json else OptionType.PUT
                    option_chain_dict_list.append(option_chain_dict)
        self.option_chains_df = pd.DataFrame.from_dict(option_chain_dict_list)
        self.option_chains_df["expiration_date"] = self.option_chains_df["expiration_datetime"].dt.date
        # reorganize the columns and set the index as "symbol"
        self.option_chains_df = self.option_chains_df[OPTION_CHAINS_COLUMNS]
        self.option_chains_df.set_index("symbol", inplace=True)
        return

    # Get the delta from the option symbol;
    def get_delta_from_option_symbol(self, option_symbol: str) -> float:
        if option_symbol not in self.option_chains_df.index:
            return None
        return self.option_chains_df.loc[option_symbol].get('delta')
    
    def get_theta_from_option_symbol(self, option_symbol: str) -> float:
        if option_symbol not in self.option_chains_df.index:
            return None
        return self.option_chains_df.loc[option_symbol].get('theta')
    
    # This is a filter function to filter out the options that are not good for trading; 
    def filter_option_candidates(self) -> pd.DataFrame:
       # Filter out the strike prices that openInterest is 0 and bid-ask spread is too large;
       data_df = self.option_chains_df[self.option_chains_df["openInterest"] > VOLUME_INTEREST_MIN]
       data_df = data_df[abs(data_df["bid"] - data_df["ask"]) < BID_ASK_SPREAD_MAX]
       return data_df

    # The expiration date needs to be larger than the min_expiration_date; and the delta is 
    # between min_delta and max_delta; and the premium percentage is larger than min_premium_percentage;
    def get_option_candidates_from_expiration_date_and_delta_range(self, 
                                                                   min_expiration_date: datetime.datetime, 
                                                                   min_delta: float = 0.16, 
                                                                   max_delta: float = 0.24, 
                                                                   min_premium_percentage: float = 0.01,
                                                                   min_premium: float = ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE, 
                                                                   option_type: OptionType = OptionType.PUT) -> list[dict]:
        data_df = self.filter_option_candidates()
        data_df = data_df[data_df["option_type"] == option_type]
        # filter out the options that are not in the expiration date range
        data_df = data_df[data_df["expiration_date"] >= min_expiration_date]
        # filter out the options that are not in the delta range
        data_df = data_df[(data_df["delta"].abs() >= min_delta) & (data_df["delta"].abs() <= max_delta)]
        # filter out the options that are not in the premium percentage range
        data_df = data_df[data_df["option_price"] > min_premium]
        data_df = data_df[data_df["option_price"] > min_premium_percentage * data_df["strike_price"]]
        # sort the options by expiration date, premium, and delta
        data_df = data_df.sort_values(by=["expiration_date", "option_price", "delta"])
        # print(data_df[["ticker", "expiration_date", "strike_price", "option_price"]])
        return data_df.to_dict(orient='records')
    
    # works for losing put options; The strike price needs to be smaller than the max strike price;
    # and the premium needs to be larger than the min_premium;
    def get_put_option_candidates_from_max_strike_price_and_min_premium(self,
                                                                        max_strike_price: float,
                                                                        min_premium: float) -> list[dict]:
        data_df = self.filter_option_candidates()
        data_df = data_df[data_df["option_type"] == OptionType.PUT]
        # filter out the options that are larger than the max strike price
        data_df = data_df[data_df["strike_price"] <= max_strike_price]
        # filter out the options that are not in the premium percentage range
        data_df = data_df[data_df["option_price"] >= min_premium]
        # sort the options by expiration date, premium, and delta
        data_df = data_df.sort_values(by=["expiration_date", "option_price", "delta"])
        return data_df.to_dict(orient='records')
    
    # works for call options; The strike price needs to be larger than the min_strike_price;
    # and the premium percentage needs to be larger than the min_premium_percentage;
    def get_call_option_candidates_from_min_strike_price_and_min_premium_percentage(self,
                                                                                    min_strike_price: float,
                                                                                    min_premium: float = ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE,
                                                                                    min_premium_percentage: float = 0.01) -> list[dict]:
        data_df = self.filter_option_candidates()
        data_df = data_df[data_df["option_type"] == OptionType.CALL]
        # filter out the options that are smaller than the min strike price
        data_df = data_df[data_df["strike_price"] >= min_strike_price]
        # filter out the options that are not in the premium percentage range
        data_df = data_df[data_df["option_price"] >= min_premium_percentage * data_df["strike_price"]]
        data_df = data_df[data_df["option_price"] >= min_premium]
        # sort the options by expiration date, premium, and delta
        data_df = data_df.sort_values(by=["expiration_date", "option_price", "delta"])
        # print(data_df[["ticker", "expiration_date", "strike_price", "option_price", "bid", "ask"]])
        return data_df.to_dict(orient='records')
