import logging

from binance.exceptions import BinanceAPIException
import base
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db = base.Base("mongodb://Roooasr:sedsaigUG12IHKJhihsifhaosf@mongodb:27017/")
#db = base.Base("localhost")

def PRICE_FILTER(symbol):
    i = db.GetSymbolInfo(symbol=symbol)
    for s in i["filters"]:
        # print(f"help: {s}")
        if s['filterType'] == 'PRICE_FILTER':
            return int(len(list(s['minPrice'].split("1")[0].replace("0.",""))))+1

def LOT_SIZE(symbol):
    i = db.GetSymbolInfo(symbol=symbol)
    for s in i["filters"]:
        # print(f"help: {s}")
        if s['filterType'] == 'LOT_SIZE':
            return int(len(list(s['stepSize'].split("1")[0].replace("0.",""))))+1

def MIN_NOTIONAL(symbol):
    i = db.GetSymbolInfo(symbol=symbol)
    for s in i["filters"]:
        # print(f"help: {s}")
        if s['filterType'] == 'NOTIONAL':
            return float(s['minNotional'])

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def Sell(client, symbol, quantity, price):
    quantity = float(quantity)
    #quantity = round(float(quantity), LOT_SIZE(symbol)-1)
    n1, n2 = str(quantity).split('.')
    quantity = float(f'{n1}.{n2[:LOT_SIZE(symbol)-1]}')
    print(quantity)
    order = client.order_limit_sell(
        symbol=symbol,
        quantity=quantity,
        price=price
    )
    return order

def Bye(client,symbol,quantity,price):
    quantity = round(float(quantity)/float(price),LOT_SIZE(symbol))
    price = toFixed(float(price),PRICE_FILTER(symbol))
    mnn = MIN_NOTIONAL(symbol)
    print(f"BYE func: {mnn} {quantity}")
    #print(f"qua: {quantity} {symbol}")
    #print(f"price: {price} {symbol}")
    if quantity >= 1:
       quantity = int(quantity)

    elif quantity <= mnn:
        quantity = mnn

    try:
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price= price
        )
        return order
    except BinanceAPIException as e:
        return 0