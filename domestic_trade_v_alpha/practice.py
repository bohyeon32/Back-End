import domestic_trade as api
stock_dict = api.get_stock_balance(True)
print(float(stock_dict["005930"]['evlu_erng_rt']))