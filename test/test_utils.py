from datetime import datetime, timedelta

from configs.utils import theta_scatter_plot


def test_theta_scatter_plot():
    import matplotlib.pyplot as plt
    deltas = [-0.2, -0.1, 0, 0.1, 0.2]
    theta_decay_percentages = [-0.1, -0.05, 0, 0.05, 0.1]
    strike_prices = [10, 20, 30, 40, 500]
    expiration_dates = [datetime.now().date() + timedelta(days=10), 
                        datetime.now().date() + timedelta(days=20), 
                        datetime.now().date() + timedelta(days=30), 
                        datetime.now().date() + timedelta(days=365), 
                        datetime.now().date() + timedelta(days=50)]
    tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']
    fig, ax = plt.subplots()
    ax = theta_scatter_plot(ax, deltas, theta_decay_percentages, expiration_dates, strike_prices, tickers, 'Delta / Theta Decay Percentage Scatter Plot')
    # show the graph;
    plt.show()
    return None


if __name__ == '__main__':
    test_theta_scatter_plot()