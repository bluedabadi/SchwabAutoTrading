

class Config(object):
    APP_KEY = 'add_you_own_key_here'
    APP_SECRET = 'add_you_own_secret_here'

TRUST_ACCOUNT_NUMBER = 'add_your_account_number_here'
IRA_ACCOUNT_NUMBER = 'add_your_account_number_here'


TICKERS_OF_IV_50_70 = ["AFRM", "AI", "BHC", "BITO", "CAR", "CELH", "CHWY", "DELL", "FSLR", "GPS",
                       "HOOD", "JBLU", "LYFT", "MDB", "MRNA", "ONON", "ROKU", "SLB", "SNAP", "SOFI", 
                        "SPOT", "TSLA", "U", "W", "Z" ]
TICKERS_OF_IV_70_100 = ["RDDT", "COIN", "UPST", "SOUN", "TDOC", "XPEV", "ARDX", "SMCI", "ARM", "HIMS",
                        "ACMR", "MPW", "ZIM", "BILI", "SEDG", "RUN", "SOXL", "AG", "RIVN", "RIOT",
                         "PCT", "VKTX", "IONQ", "MARA", "HLF", "ENVX"]
TICKERS_OF_IV_100_and_above = ["MSTR", "IBRX", "CLSK", "CIFR", "NVAX", "IREN", "BBIO", "OKLO",
                               "HE"]
TICKERS_OF_OWNED_STOCKS = ['DQ', 'ENPH', 'JD', 'SQM', 'XPEV']

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
}
# Some Magic Numbers
BID_ASK_SPREAD_MAX = 0.6
VOLUME_INTEREST_MIN = 1
ROLLOUT_LOSING_TRADE_STRIKE_PRICE_LOWER_PERCENTAGE = 0.02
ROLLOUT_LOSING_TRADE_PREMIUM_INCREASE = 0.3
STO_PUT_COUNT_MAX = 3

