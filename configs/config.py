class Config(object):
    APP_KEY = 'add_you_own_key_here'
    APP_SECRET = 'add_you_own_secret_here'
    # This is a token for getting earnings calendar from apicalls.io
    # It's optional if the earning tickers are in data/earnings_calendar.json
    # already or you don't do earnings trade;
    API_CALLS_TOKEN = 'add_you_own_key_here'


TRUST_ACCOUNT_NUMBER = 'add_your_account_number_here'
IRA_ACCOUNT_NUMBER = 'add_your_account_number_here'

# The difference between ROLL_OUT and THE_WHEEL is that ROLL_OUT will close the losing trade
# and open a new trade with the same ticker, while THE_WHEEL will let the losing trade assigned,
# and then sell covered calls or cash-secured puts.
# IF you are using a margin account, you should stick with ROLL_OUT; if you have enough cash, do THE_WHEEL.
# Please consider tax implications when choosing THE_WHEEL.
ACCOUNT_TRADING_STRATEGY_MAP = {
    TRUST_ACCOUNT_NUMBER: "ROLL_OUT",
    IRA_ACCOUNT_NUMBER: "THE_WHEEL",
}

TICKERS_OF_IV_50_70 = ["AFRM", "AI", "BHC", "BITO", "CAR", "CELH", "CHWY", "DELL", "FSLR",
                       "HOOD", "JBLU", "LYFT", "MDB", "MRNA", "ONON", "ROKU", "SLB", "SNAP", "SOFI",
                       "SPOT", "TSLA", "U", "W", "Z"]
TICKERS_OF_IV_70_100 = ["RDDT", "COIN", "UPST", "SOUN", "TDOC", "XPEV", "ARDX", "SMCI", "ARM", "HIMS",
                        "ACMR", "MPW", "ZIM", "BILI", "SEDG", "RUN", "SOXL", "AG", "RIVN", "RIOT",
                        "PCT", "VKTX", "IONQ", "MARA", "HLF", "ENVX"]
TICKERS_OF_IV_100_and_above = ["IBRX", "CLSK",
                               "CIFR", "NVAX", "IREN", "BBIO", "OKLO", "HE"]
TICKERS_FOR_THE_WHEEL = TICKERS_OF_IV_50_70 + \
    TICKERS_OF_IV_70_100 + TICKERS_OF_IV_100_and_above

STO_TRADE_SETTINGS = {
    TRUST_ACCOUNT_NUMBER: {
        "min_expiration_weeks": 4,
        "min_delta": 0.16,
        "max_delta": 0.24,
        "min_premium_percentage": 0.01,
        "max_delta_for_btc": 0.14,
    },
    IRA_ACCOUNT_NUMBER: {
        "min_expiration_weeks": 1,
        "min_delta": 0.2,
        "max_delta": 0.3,
        "min_premium_percentage": 0.01,
        "max_delta_for_btc": 0.16,
    },
    # If it is earnings trade, the expiration date is the Friday after the earnings date.
    "EARNINGS": {
        "min_expiration_weeks": 0,
        "min_delta": 0.14,
        "max_delta": 0.24,
        "min_premium_percentage": 0.005,
        "max_delta_for_btc": 0.12,
    }
}
# Some Magic Numbers
BID_ASK_SPREAD_MAX = 0.8
VOLUME_INTEREST_MIN = 1
ROLLOUT_WINNING_TRADE_PREMIUM_INCREASE = 0.1
ROLLOUT_LOSING_TRADE_STRIKE_PRICE_LOWER_PERCENTAGE = 0.02
ROLLOUT_LOSING_TRADE_PREMIUM_INCREASE = 0.3
STO_PUT_COUNT_MAX = 3
