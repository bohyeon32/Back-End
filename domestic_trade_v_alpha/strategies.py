import datetime
import domestic_trade as api
from time_mean import time_mean
import time

def volatility_breakthrough():
    symbol_list = ["005930","035720","000660","005380","035420","003550","015760"] # 매수 희망 종목 리스트
    total_cash = float(api.get_balance(True)) # 보유 현금 조회
    stock_dict = api.get_stock_balance(True) # 보유 주식 조회
    target_buy_count = 3 # 매수할 종목 수
    buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
    STOP_LOSS_RATIO = 2

    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            api.send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_start: # 잔여 수량 매도
            for sym, data in stock_dict.items():
                api.sell(sym, data['hldg_qty'])
                api.send_message(f"{sym} 잔여수량 매도합니다.")
        if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
            for sym in symbol_list:  
                if sym in stock_dict.keys():
                    stock = api.get_stock_balance(False)[sym]
                    loss = float(stock['evlu_pfls_rt'])
                    if loss < -STOP_LOSS_RATIO:
                        result = api.sell(sym,int(stock['hldg_qty']))
                        if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                else:
                    if len(stock_dict) < target_buy_count:
                        target_price = api.get_target_price(sym)
                        current_price = api.get_current_price(sym)
                        if target_price < current_price:
                            buy_qty = 0  # 매수할 수량 초기화
                            buy_qty = buy_amount//current_price
                            if buy_qty > 0:
                                api.send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict = api.get_stock_balance(True)
                                    time.sleep(10)
            if t_now.minute == 30 and t_now.second <= 5: 
                api.get_stock_balance(True)
        if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            for sym, data in stock_dict.items():
                api.sell(sym, data['hldg_qty'])
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            api.send_message("프로그램을 종료합니다.")
            evaluation = api.get_evaluation()
            myseed = float(evaluation[0]['nass_amt'])   #순자산금액
            with open('Daily Record.p','a') as recordfile:
                recordfile.write(f"{t_now.date()}-{myseed}\n")
            break

def moving_average_swing():
    symbol_list = ["005930","035720","000660","005380","035420","003550","015760"] # 매수 희망 종목 리스트
    total_cash = float(api.get_balance(True)) # 보유 현금 조회
    stock_dict = api.get_stock_balance(True) # 보유 주식 조회
    target_buy_count = 3 # 매수할 종목 수
    buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
    STOP_LOSS_RATIO = 10

    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            api.send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_exit :  # AM 09:00 ~ PM 03:15 : 매수
            for sym in symbol_list:
                current_price = api.get_current_price(sym)
                bollinger = api.get_moving_average(sym)
    
                # sell
                if sym in stock_dict.keys():
                    stock = api.get_stock_balance(False)[sym]
                    loss = float(stock['evlu_pfls_rt'])
                    if loss < -STOP_LOSS_RATIO:
                        api.sell(sym,int(stock['hldg_qty']))
                    if current_price < bollinger[0]+bollinger[1]*2:
                        result = api.sell(sym,int(stock['hldg_qty']))
                        if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                
                # buy
                else:
                    if len(stock_dict) < target_buy_count:
                        if current_price < bollinger[0]-bollinger[1]*2:
                            buy_qty = 0  # 매수할 수량 초기화
                            buy_qty = buy_amount//current_price
                            if buy_qty > 0:
                                api.send_message(f"{sym} 목표가 달성({bollinger[0]-bollinger[1]*2} < {current_price}) 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict = api.get_stock_balance(True)
                                    time.sleep(10)
            if t_now.minute == 30 and t_now.second <= 5: 
                api.get_stock_balance(True)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            api.send_message("프로그램을 종료합니다.")
            evaluation = api.get_evaluation()
            myseed = float(evaluation[0]['nass_amt'])   #순자산금액
            with open('Daily Record.p','a') as recordfile:
                recordfile.write(f"{t_now.date()}-{myseed}\n")
            break

def volume_power_5min_mean():
    symbol_list = ["005930","035720","000660","005380","035420","003550","015760"] # 매수 희망 종목 리스트
    total_cash = float(api.get_balance(True)) # 보유 현금 조회
    stock_dict = api.get_stock_balance(True) # 보유 주식 조회
    target_buy_count = 3 # 매수할 종목 수
    buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
    volume_5min_mean= {sym:time_mean(5) for sym in symbol_list}

    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            api.send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_exit:  # AM 09:00 ~ PM 03:15 : 매수
            # update volume mean
            if t_now.second <= 5:
                for sym in symbol_list:
                    volpow = api.get_volume_power(sym)
                    volume_5min_mean[sym].push(volpow)
                time.sleep(10)

            for sym in symbol_list:
                now_volpow = api.get_volume_power(sym)

                # sell
                if sym in stock_dict.items():
                    stock = api.get_stock_balance(False)[sym]
                    if now_volpow < volume_5min_mean[sym].mean and volume_5min_mean[sym].enough:
                        result = api.sell(sym,int(stock['hldg_qty']))
                        if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                
                # buy
                else:
                    if len(stock_dict) < target_buy_count:
                        if now_volpow > volume_5min_mean[sym].mean and volume_5min_mean[sym].enough:
                            buy_qty = 0
                            buy_qty = buy_amount//api.get_current_price(sym)
                            if buy_qty > 0:
                                api.send_message(f"{sym} 체결강도 x크로스 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict = api.get_stock_balance(True)
                                    time.sleep(10)
                if t_now.minute == 30 and t_now.second <= 5: 
                    api.get_stock_balance(True)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            api.send_message("프로그램을 종료합니다.")
            evaluation = api.get_evaluation()
            myseed = float(evaluation[0]['nass_amt'])   #순자산금액
            with open('Daily Record.p','a') as recordfile:
                recordfile.write(f"{t_now.date()}-{myseed}\n")
            break

def volume_power_over_100():
    symbol_list = ["005930","035720","000660","005380","035420","003550","015760"] # 매수 희망 종목 리스트
    total_cash = float(api.get_balance(True)) # 보유 현금 조회
    stock_dict = api.get_stock_balance(True) # 보유 주식 조회
    target_buy_count = 3 # 매수할 종목 수
    buy_amount = total_cash / target_buy_count  # 종목별 주문 금액 계산
    volume_5min_mean= {sym:time_mean(5) for sym in symbol_list}

    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            api.send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_exit :  # AM 09:00 ~ PM 03:15 : 매수
            # update volume mean
            if t_now.second <= 5:
                for sym in symbol_list:
                    volpow = api.get_volume_power(sym)
                    volume_5min_mean[sym].push(volpow)
                time.sleep(1000)
            
            for sym in symbol_list:
                now_volpow = api.get_volume_power(sym)

                # sell
                if sym in stock_dict.items():
                    stock = api.get_stock_balance(False)[sym]
                    if now_volpow < 100:
                        result = api.sell(sym,int(stock['hldg_qty']))
                        if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                
                # buy
                else:
                    if len(stock_dict) < target_buy_count:
                        if now_volpow > 100:
                            buy_qty = 0
                            buy_qty = buy_amount//api.get_current_price(sym)
                            if buy_qty > 0:
                                api.send_message(f"{sym} 체결강도 100이상, 매수를 시도합니다.")
                                result = api.buy(sym, buy_qty)
                                if result:
                                    stock_dict = api.get_stock_balance(True)
                                    time.sleep(10)
                if t_now.minute == 30 and t_now.second <= 5: 
                    api.get_stock_balance(True)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            api.send_message("프로그램을 종료합니다.")
            evaluation = api.get_evaluation()
            myseed = float(evaluation[0]['nass_amt'])   #순자산금액
            with open('Daily Record.p','a') as recordfile:
                recordfile.write(f"{t_now.date()}-{myseed}\n")
            break

def re_balance_portfolio():
    symbol = "005930"
    total_asset = float(api.get_evaluation()[0]['nass_amt']) # 보유 현금 조회
    stock_dict = api.get_stock_balance(True) # 보유 주식 조회

    while True:
        t_now = datetime.datetime.now()
        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        t_opening = t_now.replace(hour=9, minute=1, second=0, microsecond=0)
        t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()
        if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            api.send_message("주말이므로 프로그램을 종료합니다.")
            break
        if t_9 < t_now < t_opening:
            if not(symbol in stock_dict.keys()):
                    buy_qty = (total_asset/2)//current_price
                    result = api.buy(symbol, buy_qty)
                    if result:
                            stock_dict = api.get_stock_balance(True)
                    time.sleep(1000)

        if t_opening < t_now < t_exit :  # AM 09:00 ~ PM 03:20 : 매수
            stock_dict = api.get_stock_balance(False)
            if len(stock_dict) == 0:
                new_balance = total_asset/2
                current_price = float(api.get_current_price(symbol))
                qty = new_balance//current_price
                result = api.buy(symbol, qty)
                if result:
                        stock_dict = api.get_stock_balance(True)
                        time.sleep(10)
            if (t_now.hour == 15 and t_now.minute == 15 and t_now.second <= 5) or (abs(float(stock_dict[symbol]['evlu_erng_rt'])) >= 3) :
                new_balance = total_asset/2
                unbalanced = new_balance - float(stock_dict[symbol]['evlu_amt'])
                current_price = float(api.get_current_price(symbol))
                qty = unbalanced//current_price
                if qty < 0:
                    result = api.sell(symbol, -(qty+1))
                    if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                elif qty > 0:
                    buy_qty = unbalanced // current_price
                    result = api.buy(symbol, qty)
                    if result:
                            stock_dict = api.get_stock_balance(True)
                            time.sleep(10)
                time.sleep(1000)
            if t_now.minute == 30 and t_now.second <= 5: 
                    api.get_stock_balance(True)
        if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            api.send_message("프로그램을 종료합니다.")
            evaluation = api.get_evaluation()
            myseed = float(evaluation[0]['nass_amt'])   #순자산금액
            with open('Daily Record.p','a') as recordfile:
                recordfile.write(f"{t_now.date()}-{myseed}\n")
            break

strategy_code = 1

if strategy_code == 0:
    volatility_breakthrough()
elif strategy_code == 1:
    re_balance_portfolio()
elif strategy_code == 2:
    volume_power_5min_mean()
elif strategy_code == 3:
    moving_average_swing()