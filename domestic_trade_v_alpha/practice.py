import domestic_trade as api
evlu = api.get_evaluation()
print(evlu[0]['asst_icdc_amt'])