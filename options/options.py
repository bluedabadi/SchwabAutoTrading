from datetime import datetime, timedelta


from options.option_chains import OptionChains
from configs.config import ROLLOUT_LOSING_TRADE_PREMIUM_INCREASE, ROLLOUT_LOSING_TRADE_STRIKE_PRICE_LOWER_PERCENTAGE
from configs.utils import OptionType, OptionInstruction


class Options(object):
    # From Schwab position json, we create an Options object;
    def __init__(self, position_json):
        # First make sure it is an option;
        if position_json.get('instrument').get('assetType') != 'OPTION':
            raise ValueError("Not an option")
        instrument = position_json.get('instrument')
        self.option_symbol = instrument.get('symbol')
        # underlying symbol is in the format of '$TICKER $DATE $CALL/PUT $STRIKE'
        self.ticker = instrument.get('underlyingSymbol')
        symbol_combined = self.option_symbol.split(' ')[-1]
        # date format is 'YYMMDD'
        self.expiration_date = datetime.strptime(symbol_combined[0:6], '%y%m%d').date()
        # option type is either 'CALL' or 'PUT'
        self.option_type = OptionType.CALL if instrument.get('putCall') == 'CALL' else OptionType.PUT
        # strike price is in the format of price*1000 and we divide by 1000 to get the decimal
        # if it is 24.5, it is 24500 in the symbol;
        self.strike_price = int(symbol_combined[7:])/1000

        # option premium at the time of SELL TO OPEN
        self.option_cost = position_json.get('averagePrice')
        self.short_quantity = position_json.get('shortQuantity')
        # Normally I only short options, so I make sure the quantity is positive;
        assert self.short_quantity > 0
        # current market price of the option
        self.option_market_price = position_json.get('marketValue')/100/-self.short_quantity
        self.profit = self.option_cost - self.option_market_price
        # Where do we get the stock price? We can get it from the Schwab API;
        self.stock_price = 0
        # How do we get the Greeks of an option? We can get it from the Schwab API;
        self.delta = 0
        self.position_json = position_json

    def set_stock_price(self, stock_price) -> None:
        self.stock_price = stock_price
        return

    def set_delta(self, delta) -> None:
        self.delta = delta
        return

    def is_gain_larger_than_50_percent(self) -> bool:
        return self.option_market_price < 0.5 * self.option_cost
    
    # Our definition of winning is if the option market price is less than 0.5 * option cost
    # and delta of the trade is >= - 0.14 if it's PUT; <= 0.14 if it's CALL;
    # This delta value is different for different accounts;
    def is_winning(self, max_delta_for_btc: float = 0.14) -> bool:
        delta_satisified = abs(self.delta) <= max_delta_for_btc
        return self.is_gain_larger_than_50_percent() and delta_satisified
    
    # Our definition of losing (only for puts) is if the extrinsic value is less than 0.5% of the strike price;
    # Also the expiration date is within 2 weeks; 
    def is_losing(self) -> bool:
        # number of days between today and the expiration date;
        days_to_expiration = (self.expiration_date - datetime.today().date()).days
        if days_to_expiration > 14 or self.option_type == OptionType.CALL:
            return False
        intrinsic_value = max(self.strike_price - self.stock_price, 0) if self.option_type == OptionType.PUT else max(self.stock_price - self.strike_price, 0)
        if intrinsic_value == 0:
            return False
        extrinsic_value = self.option_market_price - intrinsic_value
        return True if extrinsic_value < 0.5 * self.strike_price/100 else False
    
    # buy to close this option;
    def create_btc_order(self) -> dict:
        order = Options.create_an_option_order(self.ticker, 
                                               self.expiration_date, 
                                               self.strike_price, 
                                               self.option_market_price, 
                                               abs(self.short_quantity), 
                                               self.option_type, 
                                               OptionInstruction.BUY_TO_CLOSE)
        # also calculate the gain of this trade;
        self.profit = (self.option_cost - self.option_market_price) * abs(self.short_quantity) * 100
        return order
    
    # Use this function to STO an option after a win;
    def sto_after_a_win(self, 
                        option_chains: OptionChains, 
                        min_expiration_weeks: int = 4, 
                        min_delta: float = 0.16, 
                        max_delta: float = 0.24, 
                        min_premium_percentage: float = 0.01) -> dict:
        # open a new position, same as fresh start;
        if self.option_type == OptionType.PUT:
            return Options.sto_an_option_order(self.ticker, 
                                            option_chains,
                                            abs(self.short_quantity), 
                                            self.option_type, 
                                            min_expiration_weeks, 
                                            min_delta, 
                                            max_delta, 
                                            min_premium_percentage)
        option_candidates = option_chains.get_call_option_candidates_from_min_strike_price_and_min_premium_percentage(
            min_strike_price=self.strike_price,
            min_premium_percentage=min_premium_percentage)
        if not option_candidates:
            print("No option candidates")
            return None, None
        # pick the first one and create an order;
        candidate = option_candidates[0]
        order = Options.create_an_option_order(self.ticker,
                                               candidate.get('expiration_date'),
                                               candidate.get('strike_price'),
                                               candidate.get('option_price'),
                                               abs(self.short_quantity),
                                               self.option_type,
                                               OptionInstruction.SELL_TO_OPEN)
        return candidate, order
    
    # Use this function to STO an option after a loss; 
    # The strike price is at least less than 0.98 * original strike price; and the premium is
    # larger than the original option_market_price + 0.3; and the expiration date is the closest 
    # date that satisfies the previous two conditions.  
    def sto_after_btc_a_loss(self, option_chains: OptionChains) -> tuple:
        if self.option_type != OptionType.PUT:
            print("Only put options are supported")
            return None, None
        # open a new position, strike price is 2% less than the original strike price;
        new_strike_price = self.strike_price * (1 - ROLLOUT_LOSING_TRADE_STRIKE_PRICE_LOWER_PERCENTAGE)
        # round to the nearest integer;
        new_strike_price = round(new_strike_price)
        # Find the expiration date with this strike price has premium > 
        # the current option price + 0.3.
        new_option_premium = self.option_market_price + ROLLOUT_LOSING_TRADE_PREMIUM_INCREASE
        option_candidates = option_chains.get_put_option_candidates_from_max_strike_price_and_min_premium(
            max_strike_price=new_strike_price, min_premium=new_option_premium)
        if not option_candidates:
            print("No option candidates")
            return None, None
        # pick the first one and create an order;
        candidate = option_candidates[0]
        order = Options.create_an_option_order(self.ticker,
                                                  candidate.get('expiration_date'),
                                                  candidate.get('strike_price'),
                                                  candidate.get('option_price'),
                                                  abs(self.short_quantity),
                                                  self.option_type,
                                                  OptionInstruction.SELL_TO_OPEN)   
        return candidate, order
    
    # Use this function to BTC current option and STO a new option;
    def create_a_rollout_order(self, 
                               new_expiration_date: datetime, 
                               new_strike_price: float, 
                               new_option_price: float):
        option_price = new_option_price - self.option_market_price
        order_type = 'NET_CREDIT' if option_price else 'NET_DEBIT'
        # create an order object for the Schwab API;
        sto_symbol = Options.form_an_option_symbol(self.ticker, new_expiration_date, new_strike_price, self.option_type)
        order_dict = {
            "orderType": order_type, 
            "session": "NORMAL", 
            "duration": "DAY", 
            "orderStrategyType": "SINGLE",
            "complexOrderStrategyType": 'CUSTOM',
            "price": option_price,
            'orderLegCollection': [{
                'orderLegType': 'OPTION', 
                'legId': 1,
                'instruction': str(OptionInstruction.BUY_TO_CLOSE), 
                'quantity': abs(self.short_quantity), 
                'instrument': {'assetType': 'OPTION', 'symbol': self.option_symbol}
                }, {
                'orderLegType': 'OPTION', 
                'legId': 2,
                'instruction': str(OptionInstruction.SELL_TO_OPEN), 
                'quantity': abs(self.short_quantity), 
                'instrument': {'assetType': 'OPTION', 'symbol': sto_symbol}
                }],
        }
        return order_dict 
    # sell to open an option of a certain ticker and option type; 
    # As for the expiration date,
    # we set it to the Friday after 4 weeks; And the strike price is chosen between delta [-0.24, -0.16];
    # And the premium is larger than 0.01 * strike price;
    # if there are multiple options, we choose the one with the smallest expiration date, premium and delta;
    @staticmethod
    def sto_an_option_order(ticker:str,
                            option_chains: OptionChains,
                            quantity: int = 1,
                            option_type: OptionType = OptionType.PUT,
                            min_expiration_weeks: int = 4, 
                            min_delta: float = 0.16, 
                            max_delta: float = 0.24, 
                            min_premium_percentage: float = 0.01) -> dict:    
        today_date = datetime.today().date()
        expiration_date = today_date + timedelta(days=(4 - today_date.weekday()) % 7 + 7*min_expiration_weeks)
        option_candidates = None
        # we need streaming data to get the delta, premium, and stock price;
        option_candidates = option_chains.get_option_candidates_from_expiration_date_and_delta_range(
            min_expiration_date=expiration_date,
            min_delta=min_delta,
            max_delta=max_delta,
            min_premium_percentage=min_premium_percentage,
            option_type=option_type)
        if not option_candidates:
            print("No option candidates")
            return None, None
        # pick the first one and create an order;
        candidate = option_candidates[0]
        order = Options.create_an_option_order(ticker,
                                               candidate.get('expiration_date'),
                                               candidate.get('strike_price'),
                                               candidate.get('option_price'),
                                               quantity,
                                               option_type,
                                               OptionInstruction.SELL_TO_OPEN)
        return candidate, order


    @staticmethod
    def create_an_option_order(ticker: str, 
                          expiration_date: datetime, 
                          strike_price: float, 
                          option_price: float, 
                          quantity: int = 1, 
                          option_type: OptionType = OptionType.PUT, 
                          instruction: OptionInstruction = OptionInstruction.SELL_TO_OPEN) -> dict:
        symbol = Options.form_an_option_symbol(ticker, expiration_date, strike_price, option_type)
        # create an order object for the Schwab API;
        order_dict = {
            "orderType": "LIMIT", 
            "session": "NORMAL", 
            "duration": "DAY", 
            "orderStrategyType": "SINGLE",
            "complexOrderStrategyType": 'NONE',
            "price": option_price,
            'orderLegCollection': [{
                'instruction': str(instruction), 
                'quantity': quantity, 
                'instrument': {'assetType': 'OPTION', 'symbol': symbol}
            }]
        }
        return order_dict
    
    @staticmethod
    def form_an_option_symbol(ticker: str, 
                          expiration_date: datetime, 
                          strike_price: float, 
                          option_type: OptionType = OptionType.PUT) -> str:
        # symbol looks like: 'RDDT  240719P00050500'
        formatted_expiration_date =expiration_date.strftime("%y%m%d") 
        int_strike_price = str(int(strike_price*1000))
        num_zeros = 8 - len(int_strike_price)
        formatted_strike_price = ''.join(['0' for i in range(num_zeros)]) + int_strike_price
        num_spaces = 6 - len(ticker)
        formatted_ticker = ticker + ''.join([' ' for i in range(num_spaces)])
        symbol = f"{formatted_ticker}{formatted_expiration_date}{str(option_type)}{formatted_strike_price}" 
        return symbol