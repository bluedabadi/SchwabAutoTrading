EARNING_CALENDAR_RESPONSE_JSON = {
    "meta": {
        "version": "v1.0",
        "status": 200,
        "copywrite": "https://apicalls.io",
        "date": "2024-07-12",
        "processedTime": "2024-07-08T01:48:08.165909Z"
    },
    "body": [
        {
            "lastYearReportDate": "7/14/2023",
            "lastYearEPS": "$4.37",
            "time": "time-pre-market",
            "symbol": "JPM",
            "name": "J P Morgan Chase & Co",
            "marketCap": "$599,288,369,668",
            "fiscalQuarterEnding": "Jun/2024",
            "epsForecast": "$4.20",
            "numberOfEstimates": "8"
        },
        {
            "lastYearReportDate": "7/14/2023",
            "lastYearEPS": "$1.25",
            "time": "time-pre-market",
            "symbol": "WFC",
            "name": "Wells Fargo & Company",
            "marketCap": "$211,479,889,616",
            "fiscalQuarterEnding": "Jun/2024",
            "epsForecast": "$1.27",
            "numberOfEstimates": "8"
        }
    ]
}

TWO_LEGS_ORDER_JSON =  {'session': 'NORMAL', 
                        'duration': 'DAY', 
                        'orderType': 'NET_CREDIT', 
                        'complexOrderStrategyType': 'CUSTOM', 
                        'quantity': 1.0, 
                        'filledQuantity': 1.0, 
                        'remainingQuantity': 0.0, 
                        'requestedDestination': 'AUTO', 
                        'destinationLinkName': 'WEXM', 
                        'price': 0.3, 
                        'orderLegCollection': [
                            {'orderLegType': 'OPTION', 'legId': 1, 'instrument': {'assetType': 'OPTION', 'cusip': '0EQNR.JI40032710', 'symbol': 'EQNR  241018C00032710', 'description': 'Equinor A S A            00500 10/18/2024 $32.71 Call', 'instrumentId': 212592918, 'type': 'VANILLA', 'putCall': 'CALL', 'underlyingSymbol': 'EQNR', 'optionDeliverables': [{'symbol': 'EQNR', 'deliverableUnits': 100.0}]}, 'instruction': 'BUY_TO_CLOSE', 'positionEffect': 'CLOSING', 'quantity': 1.0}, 
                            {'orderLegType': 'OPTION', 'legId': 2, 'instrument': {'assetType': 'OPTION', 'cusip': '0EQNR.JI40030710', 'symbol': 'EQNR  241018C00030710', 'description': 'Equinor A S A            00500 10/18/2024 $30.71 Call', 'instrumentId': 212685896, 'type': 'VANILLA', 'putCall': 'CALL', 'underlyingSymbol': 'EQNR', 'optionDeliverables': [{'symbol': 'EQNR', 'deliverableUnits': 100.0}]}, 'instruction': 'SELL_TO_OPEN', 'positionEffect': 'OPENING', 'quantity': 1.0}
                        ], 
                        'orderStrategyType': 'SINGLE', 
                        'orderId': 1000700555512, 
                        'cancelable': False, 
                        'editable': False, 
                        'status': 'FILLED', 
                        'enteredTime': '2024-06-07T16:04:29+0000', 
                        'closeTime': '2024-06-07T16:04:32+0000', 
                        'accountNumber': 12345678, 
                        'orderActivityCollection': [
                            {'activityType': 'EXECUTION', 'activityId': 82067796845, 'executionType': 'FILL', 'quantity': 1.0, 'orderRemainingQuantity': 0.0, 
                            'executionLegs': [
                                {'legId': 2, 'quantity': 1.0, 'mismarkedQuantity': 0.0, 'price': 0.5, 'time': '2024-06-07T16:04:32+0000', 'instrumentId': 212685896}, 
                                {'legId': 1, 'quantity': 1.0, 'mismarkedQuantity': 0.0, 'price': 0.2, 'time': '2024-06-07T16:04:32+0000', 'instrumentId': 212592918}
                            ]}
                        ]}


ONE_LEG_ORDER_JSON = {'session': 'NORMAL', 
                       'duration': 'DAY', 
                       'orderType': 'LIMIT', 
                       'complexOrderStrategyType': 'NONE', 
                       'quantity': 1.0, 
                       'filledQuantity': 1.0, 
                       'remainingQuantity': 0.0, 
                       'requestedDestination': 'AUTO', 
                       'destinationLinkName': 'CDRG', 
                       'price': 3.05, 
                       'orderLegCollection': [{'orderLegType': 'OPTION', 'legId': 1, 'instrument': {'assetType': 'OPTION', 'cusip': '0COIN.RE40240000', 'symbol': 'COIN  240614P00240000', 'description': 'COINBASE GLOBAL INC 06/14/2024 $240 Put', 'instrumentId': 218034259, 'type': 'VANILLA', 'putCall': 'PUT', 'underlyingSymbol': 'COIN', 'optionDeliverables': [{'symbol': 'COIN', 'deliverableUnits': 100.0}]}, 'instruction': 'SELL_TO_OPEN', 'positionEffect': 'OPENING', 'quantity': 1.0}], 
                       'orderStrategyType': 'SINGLE', 
                       'orderId': 1000701344867, 
                       'cancelable': False, 
                       'editable': False, 
                       'status': 'FILLED', 
                       'enteredTime': '2024-06-07T16:26:04+0000', 
                       'closeTime': '2024-06-07T16:26:21+0000', 
                       'accountNumber': 12345678, 
                       'orderActivityCollection': [{'activityType': 'EXECUTION', 'activityId': 82069626524, 'executionType': 'FILL', 'quantity': 1.0, 'orderRemainingQuantity': 0.0, 
                                                    'executionLegs': [{'legId': 1, 'quantity': 1.0, 'mismarkedQuantity': 0.0, 'price': 3.05, 'time': '2024-06-07T16:26:21+0000', 'instrumentId': 218034259}]
                                                    }]
                       }


DUOL_QUOTE_JSON = {'DUOL': {'assetMainType': 'EQUITY', 
                            'assetSubType': 'COE', 
                            'quoteType': 'NBBO', 
                            'realtime': True, 
                            'ssid': 74364805, 
                            'symbol': 'DUOL', 
                            'fundamental': {'avg10DaysVolume': 565460.0, 'avg1YearVolume': 689964.0, 'divAmount': 0.0, 'divFreq': 0, 'divPayAmount': 0.0, 'divYield': 0.0, 'eps': 0.35, 'fundLeverageFactor': 0.0, 'lastEarningsDate': '2024-05-08T04:00:00Z', 'peRatio': 223.39046}, 
                            'quote': {'52WeekHigh': 251.3, '52WeekLow': 121.89, 'askMICId': 'ARCX', 'askPrice': 214.2, 'askSize': 3, 'askTime': 1718742007619, 'bidMICId': 'ARCX', 'bidPrice': 210.49, 'bidSize': 2, 'bidTime': 1718742007619, 'closePrice': 211.83, 'highPrice': 213.97, 'lastMICId': 'XADF', 'lastPrice': 210.5827, 'lastSize': 1, 'lowPrice': 208.12, 'mark': 211.83, 'markChange': 0.0, 'markPercentChange': 0.0, 'netChange': -1.2473, 'netPercentChange': -0.58882122, 'openPrice': 211.02, 'postMarketChange': -1.2473, 'postMarketPercentChange': -0.58882122, 'quoteTime': 1718742007619, 'securityStatus': 'Closed', 'totalVolume': 353400, 'tradeTime': 1718753674813}, 
                            'reference': {'cusip': '26603R106', 'description': 'DUOLINGO INC A', 'exchange': 'Q', 'exchangeName': 'NASDAQ', 'isHardToBorrow': False, 'isShortable': True, 'htbRate': 0.0}, 
                            'regular': {'regularMarketLastPrice': 211.83, 'regularMarketLastSize': 34635, 'regularMarketNetChange': -0.04, 'regularMarketPercentChange': -0.01888307, 'regularMarketTradeTime': 1718740800350}}}


PUT_OPTION_JSON = {'shortQuantity': 1.0, 
               'averagePrice': 88.5409, 
               'currentDayProfitLoss': 97.599999999999, 
               'currentDayProfitLossPercentage': 1.2, 
               'longQuantity': 0.0, 
               'settledLongQuantity': 0.0, 
               'settledShortQuantity': -1.0, 
               'instrument': {'assetType': 'OPTION', 'cusip': '0NOW..WF40710000', 'symbol': 'NOW   241115P00710000', 'description': 'Service Now Inc 11/15/2024 $710 Put', 'netChange': 0.6436, 'type': 'VANILLA', 'putCall': 'PUT', 'underlyingSymbol': 'NOW'}, 
               'marketValue': -8030.0, 
               'maintenanceRequirement': 0.0, 
               'averageShortPrice': 91.9494, 
               'taxLotAverageShortPrice': 88.5409, 
               'shortOpenProfitLoss': 824.09, 
               'previousSessionShortQuantity': 1.0, 
               'currentDayCost': 0.0}


CALL_OPTION_JSON = {'shortQuantity': 1.0, 
                   'averagePrice': 0.8134, 
                   'currentDayProfitLoss': 0.0, 
                   'currentDayProfitLossPercentage': 0.0, 
                   'longQuantity': 0.0, 
                   'settledLongQuantity': 0.0, 
                   'settledShortQuantity': -1.0, 
                   'instrument': {'assetType': 'OPTION', 'cusip': '0SQM..FL40050000', 'symbol': 'SQM   240621C00050000', 'description': 'SOCIEDAD QUIMICA Y MINERA DE CHILE S A 06/21/2024 $50 Call', 'netChange': -0.0036, 'type': 'VANILLA', 'putCall': 'CALL', 'underlyingSymbol': 'SQM'}, 
                   'marketValue': -55.0, 
                   'maintenanceRequirement': 0.0, 
                   'averageShortPrice': 0.8134, 
                   'taxLotAverageShortPrice': 0.8134, 
                   'shortOpenProfitLoss': 26.34, 
                   'previousSessionShortQuantity': 1.0, 
                   'currentDayCost': 0.0}


EQUITY_JSON = {'shortQuantity': 0.0, 
               'averagePrice': 79.0566, 
               'currentDayProfitLoss': -56.5, 
               'currentDayProfitLossPercentage': -0.86, 
               'longQuantity': 100.0, 'settledLongQuantity': 100.0, 
               'settledShortQuantity': 0.0, 
               'instrument': {'assetType': 'EQUITY', 'cusip': '82509L107', 'symbol': 'SHOP', 'netChange': -0.565}, 
               'marketValue': 6490.5, 
               'maintenanceRequirement': 6490.5, 
               'averageLongPrice': 80.0, 
               'taxLotAverageLongPrice': 79.0566, 
               'longOpenProfitLoss': -1415.16, 
               'previousSessionLongQuantity': 100.0, 
               'currentDayCost': 0.0}
