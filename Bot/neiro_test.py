import datetime

from binance.client import Client
import datetime
client = Client("W4oUfz3kd65ORroNiswhGM0ZPq6inh07jPTIdOr57PVxocG3myRnDd9FjevU6vE2",
                "0B5baGfncJzYTfa9zejj1k1fE9y4SVrHAySrjFNC53mXhq2MHNiVt1pTnsIEJNbh")


orders = client.get_historical_trades(symbol="RVNBTC")
quo = 0
for o in orders:
    if o['isBuyerMaker'] == True:
        print(o)
        quo += float(o['quoteQty'])

print(datetime.datetime.fromtimestamp(orders[0]['time']/1000))
print(quo)