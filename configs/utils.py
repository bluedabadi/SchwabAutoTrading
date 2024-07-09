from pathlib import Path

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
print(TOP_LEVEL_DIR)