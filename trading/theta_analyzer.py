### The main reason of selling option trades is due to theta decay. 
# A reasonable target is to have a theta decay of 0.1% of the account value per day.
# Since there are 250 trading days in a year, the annual theta decay is 25% of the account value.
# This file is used to analyze the theta decay of the options in an account.
from datetime import datetime, timedelta

from configs.utils import theta_scatter_plot, OptionType

class ThetaAnalyzer:
    def __init__(self, client, options: list, ticker_to_stock_map: dict) -> None:
        self.options = options
        self.ticker_to_stock_map = ticker_to_stock_map
        # The sum of the theta of all the puts and calls in the account;
        self.total_theta = 0
        # The sum of the strike prices of all the puts and calls in the account;
        self.total_principal = 0
        self.total_put_principal = 0
        # The theta decay rate of the account;
        self.total_theta_decay_percentage = 0
        self.predicted_return_per_year = 0
        if not self.options:
            print("No options in the account.")
            return None
        theta_decay_percentage_list = []
        for option in self.options:
            stock = self.ticker_to_stock_map.get(option.ticker)
            if stock is None:
                continue
            option_chains = stock.get_option_chains(client)
            delta = option_chains.get_delta_from_option_symbol(option.option_symbol)
            option.set_delta(delta)
            theta = option_chains.get_theta_from_option_symbol(option.option_symbol)
            option.set_theta(theta)
            if option.theta:
                option.theta_decay_percentage = - option.theta * 100 / option.strike_price
                self.total_theta += option.theta * option.short_quantity * 100
                self.total_principal += option.strike_price * option.short_quantity * 100
                # if the option is a put, we add the principal to a put_principal;
                if option.option_type == OptionType.PUT:
                    self.total_put_principal += option.strike_price * option.short_quantity * 100
                theta_decay_percentage_list.append((option.option_symbol, option.theta_decay_percentage))
        self.total_theta_decay_percentage = - self.total_theta * 100 / self.total_principal
        print(f"Total principal: {self.total_principal}, Total theta: {self.total_theta}, Theta decay percentage: {self.total_theta_decay_percentage}")
        print(f"Total put principal: {self.total_put_principal}; total call principal: {self.total_principal - self.total_put_principal}")
        self.predicted_return_per_year = self.total_theta_decay_percentage * 250 * self.total_principal / 100
        print(f"With this setting, even if the stock price does not change, the account value will increase ${self.predicted_return_per_year} in a year.")

        # Find the top 5 options with the highest theta decay percentage,
        # and the top 5 options with the lowest theta decay percentage;
        theta_decay_percentage_list.sort(key=lambda x: x[1], reverse=True)
        print("Top 5 options with the highest theta decay percentage:")
        for i in range(5):
            print(theta_decay_percentage_list[i])
        print("Top 5 options with the lowest theta decay percentage:")
        for i in range(1, 6):
            print(theta_decay_percentage_list[-i])
        return None
    

    def scatter_plot(self):
        import matplotlib.pyplot as plt
        """
        Scatter plot all the options in the account, with x_axis delta and y_axis theta/strike_price.
        """
        if not self.options:
            print("No options in the account.")
            return None
        # x_axis is delta, y_axis is theta/strike_price; plot the scatter plot;
        deltas = [float(option.delta) for option in self.options if option.theta and option.delta ]
        theta_decay_percentages = [float(option.theta_decay_percentage) for option in self.options if option.theta and option.delta]
        strike_prices = [float(option.strike_price) for option in self.options if option.theta and option.delta]
        expiration_dates = [option.expiration_date for option in self.options if option.theta and option.delta]
        tickers = [option.ticker for option in self.options if option.theta and option.delta]

        delta_null_count = deltas.count(None)
        theta_null_count = theta_decay_percentages.count(None)
        strike_null_count = strike_prices.count(None)
        print(f"delta_null_count: {delta_null_count}, theta_null_count: {theta_null_count}, strike_null_count: {strike_null_count}")


        # plot 1x2 subplots;
        fig, ax = plt.subplots(2, 1, figsize=(10, 10))
        subtitle = f"Scatte Plot for All Positions"
        ax[0] = theta_scatter_plot(ax=ax[0], 
                                   deltas=deltas, 
                                   theta_decay_percentages=theta_decay_percentages, 
                                   strike_prices=strike_prices, 
                                   expiration_dates=expiration_dates, 
                                   tickers=tickers,
                                   subtitle=subtitle)
        
        till_60_days = datetime.now().date() + timedelta(days=60)
        deltas = [float(option.delta) for option in self.options if option.theta and option.delta and option.expiration_date <= till_60_days]
        theta_decay_percentages = [float(option.theta_decay_percentage) for option in self.options if option.theta and option.delta and option.expiration_date <= till_60_days]
        strike_prices = [float(option.strike_price) for option in self.options if option.theta and option.delta and option.expiration_date <= till_60_days]
        expiration_dates = [option.expiration_date for option in self.options if option.theta and option.delta and option.expiration_date <= till_60_days]
        tickers = [option.ticker for option in self.options if option.theta and option.delta and option.expiration_date <= till_60_days]
        subtitle = f"Scatter Plot for Positions Before {till_60_days}"
        ax[1] = theta_scatter_plot(ax=ax[1], 
                                   deltas=deltas, 
                                   theta_decay_percentages=theta_decay_percentages, 
                                   strike_prices=strike_prices, 
                                   expiration_dates=expiration_dates, 
                                   tickers=tickers,
                                   subtitle=subtitle)

        fig.suptitle(f"Total Theta Decay Perc: {round(self.total_theta_decay_percentage, 2)}, Expected Annual Return: {round(self.predicted_return_per_year, 2)}")
        plt.show()
        return None