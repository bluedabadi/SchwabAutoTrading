from pathlib import Path


def theta_scatter_plot(ax, deltas, theta_decay_percentages, expiration_dates, strike_prices, tickers, subtitle):
    # Plotting the scatter plot
    # The size of the circle is proportional to the strike price;
    # The color of the circle is by the number days to the expiration date;
    scatter = ax.scatter(expiration_dates, theta_decay_percentages, s=strike_prices, c=deltas, alpha=0.5)
    # Produce a legend for the number of days to expiration (colors). Even though there are many different
    # colors, we only want to show 5 of them in the legend.
    legend1 = ax.legend(*scatter.legend_elements(num=8),
                        loc="upper center", title="Deltas")
    ax.add_artist(legend1)

    # Produce a legend for the strike price (sizes). Because we want to show the prices
    # in dollars, we use the *func* argument to supply the inverse of the function
    # used to calculate the sizes from above. The *fmt* ensures to show the price
    # in dollars. Note how we target at 5 elements here, but obtain only 4 in the
    # created legend due to the automatic round prices that are chosen for us.
    kw = dict(prop="sizes", num=5, color=scatter.cmap(0.7), fmt="$ {x:.2f}",
            func=lambda s: s)
    legend2 = ax.legend(*scatter.legend_elements(**kw),
                        loc="upper right", title="Strike Price")
    ax.add_artist(legend2)
    # Add ticker to each point
    for i, ticker in enumerate(tickers):
        ax.annotate(ticker, (expiration_dates[i], theta_decay_percentages[i]))
    ax.set_xlabel('Expiration Date')
    ax.set_ylabel('Theta Decay Percentage')
    ax.set_title(f'{subtitle}')
    return ax

# create an enum class for the option type, either put or call;
class OptionType:
    CALL = 'C'
    PUT = 'P'


# create an enum class for the option instruction, either buy to open, sell to open, buy to close, or sell to close;
class OptionInstruction:
    BUY_TO_OPEN = 'BUY_TO_OPEN'
    SELL_TO_OPEN = 'SELL_TO_OPEN'
    BUY_TO_CLOSE = 'BUY_TO_CLOSE'
    SELL_TO_CLOSE = 'SELL_TO_CLOSE'

class StockInstruction:
    BUY = 'BUY'
    SELL = 'SELL'

class TradeReason:
    BTC_FROM_WINNING = 'btc_from_winning'
    BTC_FROM_LOSING = 'btc_from_losing'
    STO_FROM_WINNING = 'sto_from_winning'
    STO_FROM_LOSING = 'sto_from_losing'
    STO_FROM_LARGE_PRICE_CHANGE = 'sto_from_large_price_change'
    STO_FROM_EARNINGS = 'sto_from_earnings'
    STO_FROM_other = 'sto_from_other'
    ROLLOUT_FROM_WINNING = 'rollout_from_winning'
    ROLLOUT_FROM_LOSING = 'rollout_from_losing'

TOP_LEVEL_DIR = Path(__file__).parent.parent