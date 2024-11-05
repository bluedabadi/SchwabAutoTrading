# This file determins your option positions is winning or losing and if so, close the position and open a new one;
# The new position is determined by either the delta, expiration date, premium percentage or the strike price and premium;
import schwabdev
from time import sleep
import pandas as pd

from configs.config import Config, TRUST_ACCOUNT_NUMBER, ACCOUNT_TRADING_STRATEGY_MAP, TICKERS_FOR_THE_WHEEL, STO_TRADE_SETTINGS, STO_PUT_COUNT_MAX, ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE
from configs.utils import OptionType, TradeReason, sum_of_option_strike_prices
from options.options import Options
from options.stocks import Stocks


ORDER_COLUMNS = [
    "account_number",
    "symbol",
    "quantity",
    "option_instruction",
    "option_price",
    "option_profit"
]


class TradeOptions:
    def __init__(self) -> None:
        self.client = schwabdev.Client(
            Config.APP_KEY, Config.APP_SECRET, "https://127.0.0.1", update_tokens_auto=True)
        # update tokens automatically (except refresh token)
        # self.client.update_tokens_auto()
        self.linked_accounts = self.client.account_linked().json()
        self.account_number_to_hash = {}
        # We keep track of all the put options we sold to open; so we don't sell more than 3 puts;
        self.position_tracker = {}
        self.available_funds_by_account = {}
        self.options_by_account = {}
        self.ticker_to_stock_map_by_account = {}
        self.total_tickers = set()
        for account in self.linked_accounts:
            # this will get the first linked account
            account_hash = account.get('hashValue')
            account_number = account.get('accountNumber')
            self.account_number_to_hash[account_number] = account_hash
            self.position_tracker[account_number] = {}
            # Process the positions for each account;
            positions = self.client.account_details(
                account_hash, fields="positions").json()
            self.available_funds_by_account[account_number] = positions.get(
                'securitiesAccount').get('currentBalances').get('availableFunds', 0)
            positions = positions.get('securitiesAccount').get('positions')
            options, ticker_to_stock_map = self.process_positions(
                account_number, positions)
            self.options_by_account[account_number] = options
            self.ticker_to_stock_map_by_account[account_number] = ticker_to_stock_map
            self.total_tickers = self.total_tickers.union(
                set(ticker_to_stock_map.keys()))
        self.order_ids = []
        self.order_dict_list = []
        return
    
    def get_existing_tickers(self) -> set:
        return self.total_tickers

    def trade_an_order(self, account_number, order, option_profit=None, trade_reason=TradeReason.STO_FROM_other) -> None:
        # round the option price to 2 decimal places; otherwise it's not accepted by the Schwab API;
        order['price'] = round(order['price'], 2)
        account_hash = self.account_number_to_hash.get(account_number)

        print(order)
        accept_order = input(
            "|\n|****** Do you want to place the order? (y/n): ")
        if accept_order.lower() != 'y':
            print("****** Order not placed.")
            return
        # place the order
        resp = self.client.order_place(account_hash, order)
        print(f"****** Response code: {resp}")
        # get the order ID - if order is immediately filled then the id might not be returned
        order_id = resp.headers.get('location', '/').split('/')[-1]
        print(f"****** Order id: {order_id}")
        self.order_ids.append(order_id)
        sleep(5)

        # store the order information into self.order_df
        leg_2_symbol = '' if len(order.get('orderLegCollection')) == 1 else "/" + \
            order.get('orderLegCollection')[1].get('instrument').get('symbol')
        order_dict = {
            "account_number": account_number,
            "trade_reason": str(trade_reason),
            "symbol": order.get('orderLegCollection')[0].get('instrument').get('symbol') + leg_2_symbol,
            "quantity": order.get('orderLegCollection')[0].get('quantity'),
            # "option_instruction": order.get('orderLegCollection')[0].get('instruction'),
            "option_price": order.get('price'),
            "option_profit": option_profit if option_profit else "N/A"
        }
        self.order_dict_list.append(order_dict)

        return

    def trade_all_accounts(self) -> None:
        for account_number in self.account_number_to_hash.keys():
            # For the trust account, we close the winning options,
            # and roll out the losing options because we have no scash in the account;
            print(f"\n\n\nProcessing account {account_number}")
            if ACCOUNT_TRADING_STRATEGY_MAP.get(account_number) == "THE_WHEEL":
                self.process_winning_trades(
                    account_number, self.options_by_account[account_number], self.ticker_to_stock_map_by_account[account_number])
                # Now we sell cash-secured puts and covered calls;
                self.selL_cc_and_csp(
                    account_number, self.ticker_to_stock_map_by_account[account_number])
            else:
                self.process_winning_trades(
                    account_number, self.options_by_account[account_number], self.ticker_to_stock_map_by_account[account_number])
                self.process_losing_trades(
                    account_number, self.options_by_account[account_number], self.ticker_to_stock_map_by_account[account_number])
        return

    def constrain_to_current_positions(self, account_number, ticker_list) -> list[str]:
        result_ticker_list = []
        if not ticker_list:
            return result_ticker_list
        for ticker in ticker_list:
            if not self.position_tracker[account_number].get(ticker):
                continue
            result_ticker_list.append(ticker)
        return result_ticker_list

    # Sell to open a put/call option for the tickers in tickers_to_sell_dict
    # at account number account_number;
    def sto_given_tickers(self, account_number, tickers_to_sell_dict, trade_reason=TradeReason.STO_FROM_LARGE_PRICE_CHANGE) -> None:
        sto_trade_setting = STO_TRADE_SETTINGS.get(
            "EARNINGS") if trade_reason == TradeReason.STO_FROM_EARNINGS else STO_TRADE_SETTINGS.get(account_number)
        if not tickers_to_sell_dict:
            print("No tickers to sell options.")
            return
        for put_or_call in tickers_to_sell_dict.keys():
            for ticker in tickers_to_sell_dict.get(put_or_call):
                option_type = OptionType.PUT if put_or_call == "put" else OptionType.CALL
                options_with_this_ticker_and_type = []
                num_of_options = 0
                if self.position_tracker[account_number].get(ticker) and self.position_tracker[account_number].get(ticker).get(str(option_type)):
                    options_with_this_ticker_and_type = self.position_tracker[account_number].get(
                        ticker).get(str(option_type))
                    num_of_options = len(self.position_tracker[account_number].get(
                        ticker).get(str(option_type)))
                if option_type == OptionType.PUT and num_of_options >= STO_PUT_COUNT_MAX:
                    print(
                        f"We have sold {STO_PUT_COUNT_MAX} puts for stock {ticker}, skip.")
                    continue
                elif option_type == OptionType.CALL:  # we only sell covered calls;
                    if not self.position_tracker[account_number].get(ticker) or not self.position_tracker[account_number].get(ticker).get("stock"):
                        print(f"We don't have {ticker} stocks, skip calls.")
                        continue
                    covered_calls = self.position_tracker[account_number].get(
                        ticker).get("stock")/100 - num_of_options
                    if covered_calls < 2:
                        print(
                            f"We don't have enough {ticker} stocks, skip calls.")
                        continue
                stock_quote = self.client.quote(ticker).json()
                stock = Stocks.initialize_from_quote_json(ticker, stock_quote)
                print(f"*** sell 1 {put_or_call} for {ticker}")
                candidate, sto_order = Options.sto_an_option_order(
                    ticker=ticker,
                    option_type=option_type,
                    option_chains=stock.get_option_chains(self.client),
                    min_expiration_weeks=sto_trade_setting.get(
                        "min_expiration_weeks"),
                    min_delta=sto_trade_setting.get("min_delta"),
                    max_delta=sto_trade_setting.get("max_delta"),
                    min_premium_percentage=sto_trade_setting.get(
                        "min_premium_percentage")
                )
                # It's possible that we can't find a suitable option to sell to open, so we need to check if sto_order is None;
                if not sto_order:
                    print(
                        f"******* Can't find a suitable option candidate to sell to open for {ticker}, skip.")
                    continue
                symbol = sto_order.get('orderLegCollection')[
                    0].get('instrument').get('symbol')
                # if current positions have the same symbol, we don't sell to open again;
                if symbol in options_with_this_ticker_and_type:
                    print(f"******* We have sold {symbol}, skip.")
                    continue
                self.trade_an_order(TRUST_ACCOUNT_NUMBER,
                                    sto_order, trade_reason=trade_reason)
        return

    def display_all_orders(self) -> None:
        if not self.order_dict_list:
            print("No orders to display.")
            return
        order_df = pd.DataFrame.from_dict(self.order_dict_list).sort_values(
            by=["account_number", "trade_reason", "symbol"])
        # ignore the index
        order_df.reset_index(drop=True, inplace=True)
        # print the order_df
        print(order_df)
        return

    def process_winning_trades(self, account_number, options, ticker_to_stock_map) -> None:
        if not options:
            return
        for option in options:
            if not option.is_gain_larger_than_50_percent():
                continue

            equity = ticker_to_stock_map.get(option.ticker)
            try:
                option_chains = equity.get_option_chains(self.client)
                delta = option_chains.get_delta_from_option_symbol(
                    option.option_symbol)
                option.set_delta(delta)
                # open a new position, same as fresh start;
                sto_trade_setting = STO_TRADE_SETTINGS.get(account_number)

                if not option.is_winning(sto_trade_setting.get("max_delta_for_btc")):
                    continue
                # We close the winning position and open a new position;
                print(
                    f"*** Option {option.option_symbol} with delta {option.delta} is winning, will close and open a new position.")
                btc_order = option.create_btc_order()
                candidate, sto_order = option.sto_after_a_win(
                    option_chains,
                    min_expiration_weeks=sto_trade_setting.get(
                        "min_expiration_weeks"),
                    min_delta=sto_trade_setting.get("min_delta"),
                    max_delta=sto_trade_setting.get("max_delta"),
                    min_premium_percentage=sto_trade_setting.get(
                        "min_premium_percentage"),
                    min_premium=option.option_market_price +
                    ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE,
                )
                # It's possible that we can't find a suitable option to sell to open, so we need to check if sto_order is None;
                if not sto_order:
                    print(
                        f"****** Can't find a suitable option candidate to sell to open, only buy to close.")
                    self.trade_an_order(account_number,
                                        btc_order,
                                        option_profit=option.profit,
                                        trade_reason=TradeReason.BTC_FROM_WINNING)
                    continue
                # Otherwise roll out the order; the benefit of having two legs order is due to large spread;
                rollout_order = option.create_a_rollout_order(
                    candidate.get('expiration_date'),
                    candidate.get('strike_price'),
                    candidate.get('option_price'))
                self.trade_an_order(account_number,
                                    rollout_order,
                                    option_profit=option.profit,
                                    trade_reason=TradeReason.ROLLOUT_FROM_WINNING)
            except Exception as e:
                print(
                    f"Failed at process winning trade {option.option_symbol}, error: {e}")
        return

    def process_losing_trades(self, account_number, options, ticker_to_stock_map) -> None:
        if not options:
            return
        for option in options:
            if not option.is_losing():
                continue
            print(
                f"*** Option {option.option_symbol} is losing, will roll out to further date.")
            # We get option chains data for the option;
            equity = ticker_to_stock_map.get(option.ticker)
            try:
                option_chains = equity.get_option_chains(self.client)
                # We close the losing position and open a new position;
                btc_order = option.create_btc_order()
                # open a new position, strike price is 2% less than the original strike price;
                # Find the expiration date with this strike price has premium > the current option price.
                candidate, sto_order = option.sto_after_btc_a_loss(
                    option_chains)
                if not sto_order:
                    print(
                        f"****** Can't find a suitable option candidate to sell to open, only buy to close.")
                    self.trade_an_order(
                        account_number, btc_order, option_profit=option.profit, trade_reason=TradeReason.BTC_FROM_LOSING)
                    continue
                # Otherwise roll out the order; the benefit of having two legs order is due to large spread;
                rollout_order = option.create_a_rollout_order(
                    candidate.get('expiration_date'),
                    candidate.get('strike_price'),
                    candidate.get('option_price'))
                self.trade_an_order(account_number,
                                    rollout_order,
                                    option_profit=option.profit,
                                    trade_reason=TradeReason.ROLLOUT_FROM_LOSING)
            except Exception as e:
                print(
                    f"Failed at process losing trade {option.option_symbol}, error: {e}")
        return

    # This function is written for the wheel strategy; we sell cash-secured puts and covered calls based on the
    # stocks we own and TICKERS_FOR_THE_WHEEL;
    def selL_cc_and_csp(self, account_number, ticker_to_stock_map, trade_reason=TradeReason.STO_FROM_THE_WHEEL) -> None:
        sto_trade_setting = STO_TRADE_SETTINGS.get(account_number)
        # first sell covered calls; the covered call price should be larger than the cost basis;
        for ticker in self.position_tracker[account_number].keys():
            ticker_info = self.position_tracker[account_number].get(ticker)
            num_stocks = ticker_info.get("stock", 0)
            call_options = ticker_info.get(str(OptionType.CALL), [])
            num_of_call_options = len(call_options)
            num_cc_to_sell = int(num_stocks/100) - num_of_call_options
            if num_cc_to_sell < 1:
                continue
            # WE have at least 100 shares of stock to sell covered calls;
            stock = ticker_to_stock_map.get(ticker)
            cost_basis = stock.avg_cost_basis * stock.quantity
            current_call_options_price_total = sum_of_option_strike_prices(
                call_options, option_type=OptionType.CALL)
            min_strike_price = (
                cost_basis/100 - current_call_options_price_total)/num_cc_to_sell
            min_strike_price = max(min_strike_price, stock.stock_price)
            print(
                f"*** sell {num_cc_to_sell} covered calls for {ticker} with min_strike_price: {min_strike_price}")
            candidate, sto_order = Options.sto_an_option_order(
                ticker=ticker,
                option_type=OptionType.CALL,
                option_chains=stock.get_option_chains(self.client),
                quantity=num_cc_to_sell,
                min_expiration_weeks=sto_trade_setting.get(
                    "min_expiration_weeks"),
                min_delta=sto_trade_setting.get("min_delta"),
                max_delta=sto_trade_setting.get("max_delta"),
                min_premium_percentage=sto_trade_setting.get(
                    "min_premium_percentage"),
                cost_basis=min_strike_price
            )
            # It's possible that we can't find a suitable option to sell to open, so we need to check if sto_order is None;
            if not sto_order:
                print(
                    f"****** Can't find a suitable option candidate to sell to open for {ticker}, skip.")
                continue
            self.trade_an_order(account_number, sto_order,
                                trade_reason=trade_reason)

        # Now check how much cash we have and sell cash-secured puts;
        available_balance = self.available_funds_by_account[account_number]
        print(f"Cash available for trading: {available_balance}")
        if available_balance <= 0:
            print(f"We don't have cash to sell cash-secured puts, skip.")
            return
        # put ticker candidates are the stocks we own and TICKERS_FOR_THE_WHEEL and we don't have put options;
        put_ticker_candidates = set(self.position_tracker[account_number].keys()).union(
            set(TICKERS_FOR_THE_WHEEL))
        # we should sort the put_ticker_candidates by the stock price, so we sell puts for the cheaper stocks first;
        put_ticker_and_price_list = []
        for ticker in put_ticker_candidates:
            stock_quote = self.client.quote(ticker).json()
            stock = Stocks.initialize_from_quote_json(ticker, stock_quote)
            put_ticker_and_price_list.append((ticker, stock.stock_price))
        # sort the list by the stock price;
        put_ticker_and_price_list.sort(key=lambda x: x[1])
        if available_balance <= put_ticker_and_price_list[0][1] * 100:
            print(
                f"We don't have enough cash to sell cash-secured puts, skip.")
            return
        for ticker, price in put_ticker_and_price_list:
            ticker_info = self.position_tracker[account_number].get(ticker)
            num_of_put_options = 0
            if ticker_info:
                num_of_put_options = len(ticker_info.get(str(OptionType.PUT), []))
                num_stocks = ticker_info.get("stock", 0)
                print(f"ticker {ticker} has {num_stocks} stocks and {num_of_put_options} put options.")
            if num_of_put_options + num_stocks / 100 >= STO_PUT_COUNT_MAX:
                continue
            stock_quote = self.client.quote(ticker).json()
            stock = Stocks.initialize_from_quote_json(ticker, stock_quote)
            print(f"*** sell 1 cash-secured puts for {ticker}")
            candidate, sto_order = Options.sto_an_option_order(
                ticker=ticker,
                option_type=OptionType.PUT,
                option_chains=stock.get_option_chains(self.client),
                quantity=1,
                min_expiration_weeks=sto_trade_setting.get(
                    "min_expiration_weeks"),
                min_delta=sto_trade_setting.get("min_delta"),
                max_delta=sto_trade_setting.get("max_delta"),
                min_premium_percentage=sto_trade_setting.get(
                    "min_premium_percentage")
            )
            # It's possible that we can't find a suitable option to sell to open, so we need to check if sto_order is None;
            if not sto_order:
                print(
                    f"****** Can't find a suitable option candidate to sell to open for {ticker}, skip.")
                continue
            strike_price = candidate.get('strike_price')
            available_balance -= strike_price * 100
            if available_balance < 0:
                print(
                    f"******* We don't have enough cash to sell cash-secured puts for {ticker}, skip.")
                break
            self.trade_an_order(account_number, sto_order,
                                trade_reason=trade_reason)

    def process_positions(self, account_number, positions) -> tuple:
        option_positions = []
        ticker_to_stock_map = {}
        if not positions:
            return None, None
        for position in positions:
            if position.get('instrument').get('assetType') == 'OPTION':
                option = Options(position)
                option_positions.append(option)
                position_list = [option.option_symbol] * \
                    abs(int(option.short_quantity))
                if not self.position_tracker[account_number].get(option.ticker):
                    self.position_tracker[account_number][option.ticker] = {
                        str(option.option_type): position_list}
                elif not self.position_tracker[account_number].get(option.ticker).get(str(option.option_type)):
                    self.position_tracker[account_number][option.ticker][str(
                        option.option_type)] = position_list
                else:
                    current_position_list = self.position_tracker[account_number].get(
                        option.ticker).get(str(option.option_type))
                    self.position_tracker[account_number][option.ticker][str(
                        option.option_type)] = current_position_list + position_list
            elif position.get('instrument').get('assetType') == 'EQUITY':
                stock = Stocks(position)
                ticker_to_stock_map[stock.ticker] = stock
                if not self.position_tracker[account_number].get(stock.ticker):
                    self.position_tracker[account_number][stock.ticker] = {
                        "stock": stock.quantity}
                else:
                    self.position_tracker[account_number][stock.ticker]["stock"] = stock.quantity

        # Afterwards, we add the stock price to the option positions;
        for option in option_positions:
            stock = ticker_to_stock_map.get(option.ticker)
            # If the stock is not in the map, we need to get the stock price from the Schwab API;
            if not stock:
                stock_quote = self.client.quote(option.ticker).json()
                stock = Stocks.initialize_from_quote_json(
                    option.ticker, stock_quote)
            option.set_stock_price(stock.stock_price)
            ticker_to_stock_map[option.ticker] = stock
        return option_positions, ticker_to_stock_map
