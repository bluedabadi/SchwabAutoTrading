from datetime import datetime
import requests
import json
from os import path
import yfinance as yf

from configs.config import Config
from configs.utils import TOP_LEVEL_DIR


class EarningsCalendar:
    def __init__(self) -> None:
        self.earnings_calendar_json = {}
        # read earnings_calendar.json first;
        self.earnings_calendar_json_path = path.join(TOP_LEVEL_DIR, "data/earnings_calendar.json")
        # if the earnings_calendar.json exists, read it;
        if path.exists(self.earnings_calendar_json_path):
            with open(self.earnings_calendar_json_path, "r", encoding="utf-8") as f:
                self.earnings_calendar_json = json.load(f)
                f.close()
        self.url = 'https://apicalls.io/api/v1/markets/calendar/earnings'
        self.headers = {'Authorization': f'Bearer {Config.API_CALLS_TOKEN}'}
        return None
    
    def get_earning_tickers(self, date: datetime.date) -> list[str]:
        # check if the date is in the earnings_calendar.json
        # but format date to string YYYY-MM-DD first;
        date = date.strftime("%Y-%m-%d")
        if date in self.earnings_calendar_json.keys():
            self.earning_tickers = self.earnings_calendar_json[date]
            return self.earning_tickers
        # if the date is not in the earnings_calendar.json, make an API call to get the earnings
        params = {'date': date}
        response = requests.request('GET', self.url, headers=self.headers, params=params)
        self.earnings_json = response.json()
        # verify whether the response is successful
        if response.status_code != 200 or not self.earnings_json.get('body'):
            print(f"API call failed with status code {response.status_code} or no earnings for date {date}")
            return None
        # save the earnings json to the earnings_calendar.json
        self.earning_tickers = [earning['symbol'] for earning in self.earnings_json['body']]
        self.earnings_calendar_json[date] = self.earning_tickers
        with open(self.earnings_calendar_json_path, "w", encoding="utf-8") as f:
            json.dump(self.earnings_calendar_json, f, ensure_ascii=False, indent=4)
            f.close()
        return self.earning_tickers
    
    @staticmethod
    def generate_earnings_calendar_from_yahoo_finance(symbol_list):
        earnings_calendar_map = {}
        for symbol in symbol_list:
            ticker = yf.Ticker(symbol)
            earning_date = ticker.calendar.get('Earnings Date')
            if earning_date:
                earning_date = earning_date[0]
                # only care about the future earnings
                if earning_date < datetime.date(datetime.now()):
                    continue
                # convert it to string, in the format of "YYYY-MM-DD"
                earning_date = earning_date.strftime("%Y-%m-%d")
                if earning_date not in earnings_calendar_map:
                    earnings_calendar_map[earning_date] = [symbol]
                else:
                    earnings_calendar_map[earning_date].append(symbol)
        # write this map to a json file
        earnings_calendar_json_path = path.join(TOP_LEVEL_DIR, "data/earnings_calendar.json")
        with open(earnings_calendar_json_path, "w", encoding="utf-8") as f:
            json.dump(earnings_calendar_map, f, ensure_ascii=False, indent=4, sort_keys=True)
            f.close()

