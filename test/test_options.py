from datetime import datetime

from configs.utils import OptionType
from data.jsons_for_tests import PUT_OPTION_JSON, CALL_OPTION_JSON
from options.options import Options


def test_put_option():
    put_option = Options(PUT_OPTION_JSON)
    assert put_option.ticker == 'NOW'
    assert put_option.expiration_date == datetime.strptime('241115', '%y%m%d').date()
    assert put_option.option_type == OptionType.PUT
    assert put_option.strike_price == 710.0
    assert put_option.option_cost == 88.5409
    assert put_option.short_quantity == 1.0
    assert put_option.option_market_price == 80.30
    assert put_option.is_winning() == False

    assert put_option.is_gain_larger_than_50_percent() == False
    put_option.set_stock_price(700)
    assert put_option.is_losing() == False

def test_call_option():
    call_option = Options(CALL_OPTION_JSON)
    assert call_option.ticker == 'SQM'
    assert call_option.expiration_date == datetime.strptime('240621', '%y%m%d').date()
    assert call_option.option_type == OptionType.CALL
    assert call_option.strike_price == 50.0
    assert call_option.option_cost == 0.8134
    assert call_option.short_quantity == 1.0
    assert call_option.option_market_price == 0.55
    assert call_option.is_winning() == False

def test_create_an_option_order():
    ticker = 'RDDT'
    expiration_date = datetime.strptime('240719', '%y%m%d')
    strike_price = 50.5
    option_price = 0.75
    order_dict = Options.create_an_option_order(ticker, expiration_date, strike_price, option_price)
    assert order_dict['orderLegCollection'][0]['instrument']['symbol'] == 'RDDT  240719P00050500'
    assert order_dict['orderLegCollection'][0]['instruction'] == 'SELL_TO_OPEN'
    assert order_dict['price'] == 0.75
    assert order_dict['orderType'] == 'LIMIT'


if __name__ == '__main__':
    test_put_option()
    test_call_option()
    test_create_an_option_order()
    print("Everything passed")