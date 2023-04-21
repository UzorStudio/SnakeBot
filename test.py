from datetime import datetime, timedelta

from binance.client import Client
import numpy as np


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2",
                "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")


def calculate_indicators2(data, period_rsi=14, period_bb=20, std_multiplier=2):
    prices = [float(d[4]) for d in data]
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [change if change > 0 else 0 for change in changes]
    losses = [-change if change < 0 else 0 for change in changes]
    avg_gain = sum(gains[:period_rsi]) / period_rsi
    avg_loss = sum(losses[:period_rsi]) / period_rsi
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    for i in range(period_rsi, len(prices) - 1):
        gain = changes[i] if changes[i] > 0 else 0
        loss = -changes[i] if changes[i] < 0 else 0
        avg_gain = ((avg_gain * (period_rsi - 1)) + gain) / period_rsi
        avg_loss = ((avg_loss * (period_rsi - 1)) + loss) / period_rsi
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = rsi + (100 / (1 + rs)) - 100

    prices = [float(d[4]) for d in data]
    sma = []
    upper_band = []
    lower_band = []
    for i in range(period_bb - 1, len(prices)):
        sma.append(sum(prices[i - period_bb + 1:i + 1]) / period_bb)
        std = std_multiplier * np.std(prices[i - period_bb + 1:i + 1])
        upper_band.append(sma[-1] + std)
        lower_band.append(sma[-1] - std)

    if rsi > 70 and prices[-1] > upper_band[-1]:
        return f"Цена слишком завышена, ожидается падение цены. Рекомендуется продавать.\nRSI: {rsi:.2f}, Price: {prices[-1]:.2f}, Upper Band: {upper_band[-1]:.2f}"
    elif rsi < 30 and prices[-1] < lower_band[-1]:
        return f"Цена слишком занижена, ожидается рост цены. Рекомендуется покупать.\nRSI: {rsi:.2f}, Price: {prices[-1]:.2f}, Lower Band: {lower_band[-1]:.2f}"
    elif prices[-1] > upper_band[-1]:
        return f"Ожидается падение цены.\nRSI: {rsi:.2f}, Price: {prices[-1]:.2f}, Upper Band: {upper_band[-1]:.2f}"
    elif prices[-1] < lower_band[-1]:
        return f"Ожидается рост цены.\nRSI: {rsi:.2f}, Price: {prices[-1]:.2f}, Lower Band: {lower_band[-1]:.2f}"
    else:
        return "Neutral"


def calculate_indicators(data, period_rsi=14, period_bb=20, std_multiplier=2):
    """Здесь data - массив свечей, period_rsi и period_bb - периоды для RSI и Bollinger Bands соответственно, std_multiplier - множитель стандартного отклонения для Bollinger Bands.
Функция возвращает текстовое описание прогнозируемого направления движения цены. Например, если она возвращает "Bearish", то можно ожидать, что цена пойдет вниз."""
    # Calculate RSI
    prices = [float(d[4]) for d in data]
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [change if change > 0 else 0 for change in changes]
    losses = [-change if change < 0 else 0 for change in changes]
    avg_gain = sum(gains[:period_rsi]) / period_rsi
    avg_loss = sum(losses[:period_rsi]) / period_rsi
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    for i in range(period_rsi, len(prices) - 1):
        gain = changes[i] if changes[i] > 0 else 0
        loss = -changes[i] if changes[i] < 0 else 0
        avg_gain = ((avg_gain * (period_rsi - 1)) + gain) / period_rsi
        avg_loss = ((avg_loss * (period_rsi - 1)) + loss) / period_rsi
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = rsi + (100 / (1 + rs)) - 100

    # Calculate Bollinger Bands
    prices = [float(d[4]) for d in data]
    sma = []
    upper_band = []
    lower_band = []
    for i in range(period_bb - 1, len(prices)):
        sma.append(sum(prices[i - period_bb + 1:i + 1]) / period_bb)
        std = std_multiplier * np.std(prices[i - period_bb + 1:i + 1])
        upper_band.append(sma[-1] + std)
        lower_band.append(sma[-1] - std)

    # Predict price direction
    if rsi > 70 and prices[-1] > upper_band[-1]:
        return f"Цена слишком завышена ожидаеться падение, рекомендую продавать \nrsi: {rsi} price: {prices[-1]} Bollinger Bands: {upper_band[-1]}"  # Возможно нужно продавать
    elif rsi < 30 and prices[-1] < lower_band[-1]:
        return f"Цена слишком занижена ожидаеться рост, рекомендую купить \nrsi: {rsi} price: {prices[-1]} Bollinger Bands: {upper_band[-1]}"  # Возможно нужно покупать
    elif prices[-1] > upper_band[-1]:
        return f"Ожидается падение цены \nrsi: {rsi} price: {prices[-1]} Bollinger Bands: {upper_band[-1]}"  # цена пойдет вниз
    elif prices[-1] < lower_band[-1]:
        return f"Ожидается Рост цены \nRSI: {rsi} Цена: {prices[-1]} Bollinger Bands: {upper_band[-1]}"  # Рост цены
    else:
        return "Neutral"


def calculate_rsi(data, period=14):
    prices = [float(d[4]) for d in data]
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [change if change > 0 else 0 for change in changes]
    losses = [-change if change < 0 else 0 for change in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        return 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        for i in range(period, len(prices) - 1):
            gain = changes[i] if changes[i] > 0 else 0
            loss = -changes[i] if changes[i] < 0 else 0
            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = rsi + (100 / (1 + rs)) - 100
        return rsi


print(1.3999999999999798e-06+0.0001)

#creation_time = datetime.fromtimestamp(1680545449041 / 1000)
#time_diff = datetime.now() - creation_time
#print(time_diff > timedelta(hours=5))
#symbols = client.get_symbol_ticker()
#for s in symbols:
#    data = client.get_klines(symbol=s["symbol"], limit=24, interval=Client.KLINE_INTERVAL_1HOUR)
#    viv = calculate_indicators(data,period_rsi=24)
#    if viv == "Neutral":
#        pass
#    else:
#        print("____________________")
#        print(f"{s['symbol']} {s['price']} {viv}")
#        print("____________________")

