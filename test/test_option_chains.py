import json
import datetime

from options.option_chains import OptionChains

def get_option_chains():
    # read the option chains json from a file
    with open('./data/duol_option_chains.json') as f:
        option_chains_json = json.load(f)
    option_chains = OptionChains(option_chains_json)
    return option_chains

def test_get_delta_from_option_symbol():
    option_chains = get_option_chains()
    assert option_chains.get_delta_from_option_symbol("DUOL  240719P00200000") == -0.299

def test_get_option_candidates_from_expiration_date_and_delta_range():
    option_chains = get_option_chains()

    min_expiration_date = datetime.date(2024, 7, 18)
    # test get_option_candidates_from_expiration_date_and_delta_range
    option_candidates = option_chains.get_option_candidates_from_expiration_date_and_delta_range(min_expiration_date=min_expiration_date)
    assert len(option_candidates) == 2
    candidate_0 = option_candidates[0]
    assert candidate_0['expiration_date'] == datetime.date(2024, 7, 19)
    assert candidate_0['strike_price'] == 195.0
    assert candidate_0['option_price'] == 4.15
    candidate_1 = option_candidates[1]
    assert candidate_1['expiration_date'] == datetime.date(2024, 8, 16)
    assert candidate_1['strike_price'] == 180.0
    assert candidate_1['option_price'] == 7.5

def test_get_put_option_candidates_from_max_strike_price_and_min_premium():
    option_chains = get_option_chains()

    # test get_put_option_candidates_from_max_strike_price_and_min_premium
    put_option_candidates = option_chains.get_put_option_candidates_from_max_strike_price_and_min_premium(
        max_strike_price=200.0, min_premium=4.0)
    assert len(put_option_candidates) == 3
    candidate_2 = put_option_candidates[2]
    assert candidate_2['expiration_date'] == datetime.date(2024, 8, 16)
    assert candidate_2['strike_price'] == 180.0
    assert round(candidate_2['option_price'], 2) == 7.5


def test_get_call_option_candidates_from_min_strike_price_and_min_premium_percentage():
    option_chains = get_option_chains()

    # test get_call_option_candidates_from_min_strike_price_and_min_premium_percentage
    call_option_candidates = option_chains.get_call_option_candidates_from_min_strike_price_and_min_premium_percentage(
        min_strike_price=250.0, min_premium_percentage=0.02)
    # The reason we don't have "DUOL  240816P00260000" is because the open interest is 0s
    assert len(call_option_candidates) == 1
    candidate_0 = call_option_candidates[0]
    assert candidate_0['expiration_date'] == datetime.date(2024, 8, 16)
    assert candidate_0['strike_price'] == 270.0
    assert round(candidate_0['option_price'], 2) == 5.85

if __name__ == '__main__':
    test_get_delta_from_option_symbol()
    test_get_option_candidates_from_expiration_date_and_delta_range()
    test_get_put_option_candidates_from_max_strike_price_and_min_premium()
    test_get_call_option_candidates_from_min_strike_price_and_min_premium_percentage()
    print("Everything passed")