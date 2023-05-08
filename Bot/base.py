import pymongo
from bson import ObjectId

from datetime import datetime
from datetime import timedelta


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

class Base:
    def __init__(self, classterMongo):
        self.classterMongo = classterMongo
        self.classter = pymongo.MongoClient(self.classterMongo)


    def regBot(self, valute_par, total_sum_invest,name, sum_invest, step,min_price,max_price):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        post = {
            "valute_par": valute_par,
            "name": name,
            "sum_invest": float(sum_invest),
            "total_sum_invest": float(total_sum_invest),
            'orders':[],
            "step":step/100000000,
            "full_orders": {}, # [{"bye":0.0..30,"sell":0.0..31},{"bye":0.0..30,"sell":False}]
            "count_hev": 0,  # записывать количество
            'spent':0,
            'spent_true':0,
            "bye_order":False,
            'on': True,
            "reinvest":True,
            "total_profit":0,
            "cikle_count":0,
            "min_price":min_price,
            "max_price":max_price,
            "base_sum_invest":float(sum_invest),
            "base_total_sum_invest":float(total_sum_invest),
            "earned": 0,
            "last_price":[]
        }

        return Bots.insert_one(post).inserted_id


    def getAllBots(self):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        return Bots.find({}).sort("cikle_count", -1)

    def getBot(self, id):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        return Bots.find_one({"_id": ObjectId(id)})


    def addOrderBye(self,bot_id,order):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]
        spent = float(order["origQty"])*float(order["price"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$inc": {"total_sum_invest": -spent}})
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$push":{'orders':order['orderId']}})
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set":{'bye_order':True}})
        Orders.insert_one({"bot_id":ObjectId(bot_id),"bye_id":order['orderId'],"bye":order,"sell":False,"sell_id":False,"profit":0,"erned":0,"is_bye":False,"finish":False})


    def addOrderSell(self,bot_id,order_bye,order_sell):
        db = self.classter["SnakeBot"]
        Orders = db["Orders"]
        Bots = db["Bots"]
        print(f"order_sell: {order_sell}")
        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_bye["orderId"])
        print(orders)
        orders.append(order_sell['orderId'])

        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set":{'bye_order':False}})
        Orders.update_one({"bot_id": ObjectId(bot_id),"bye_id":order_bye["orderId"]}, {"$set": {"sell": order_sell,"bye":order_bye,"sell_id":order_sell["orderId"],"is_bye":True}})

    def reloadOrderSell(self, bot_id, order_sell_old, order_sell_new):
        db = self.classter["SnakeBot"]
        Orders = db["Orders"]
        Bots = db["Bots"]
        print(f"order_Reload: {order_sell_new}")
        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_sell_old["orderId"])
        print(orders)
        orders.append(order_sell_new['orderId'])

        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})
        Orders.update_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell_old["orderId"]},
                          {"$set": {"sell": order_sell_new, "sell_id": order_sell_new["orderId"], "is_bye": True}})


    def reloadSumInvest(self,bot_id,order_bye):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        add = float(order_bye["origQty"]) * float(order_bye["price"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$inc": {"total_sum_invest": +add}})
    def reloadOrderBye(self,bot_id,order_bye,order_bye_new):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]

        Orders.delete_one({"bot_id": ObjectId(bot_id),"bye_id":order_bye["orderId"]})

        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_bye["orderId"])
        print(orders)
        orders.append(order_bye_new['orderId'])

        spent = float(order_bye_new["origQty"]) * float(order_bye_new["price"])

        Bots.update_one({"_id": ObjectId(bot_id)}, {"$inc": {"total_sum_invest": -spent}})
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})
        Orders.insert_one(
            {"bot_id": ObjectId(bot_id), "bye_id": order_bye_new['orderId'], "bye": order_bye_new, "sell": False, "sell_id": False,
             "profit": 0, "erned": 0, "is_bye": False, "finish": False})


    def dropOrder(self,bot_id,order_bye):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_bye["orderId"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})

    def findOrder(self,bot_id):
        db = self.classter["SnakeBot"]
        Orders = db["Orders"]

        Orders.find({"bot_id": ObjectId(bot_id), "finish":  False})

    def Sell(self,bot_id,order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]
        Send = db["Send"]

        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_sell["orderId"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})
        bt = Bots.find_one({"_id": ObjectId(bot_id)})

        order = Orders.find_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]})
        print(f"from Sell: {order}")

        erned = float(order_sell["cummulativeQuoteQty"])-float(order['bye']["cummulativeQuoteQty"])
        profit = 1-(float(order['bye']["cummulativeQuoteQty"])/float(order_sell["cummulativeQuoteQty"]))

        try:
            full_orders = Bots.find_one({"_id": ObjectId(bot_id)})['full_orders']
            if order['bye']["price"] in full_orders:
                Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"full_orders": {order['bye']["price"]:order['bye']["cummulativeQuoteQty"]}}})
            else:
                full_orders[order['bye']["price"]] = order['bye']["cummulativeQuoteQty"]
                Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"full_orders":full_orders}})
        except:
            Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"full_orders":{order['bye']["price"]:order['bye']["cummulativeQuoteQty"]}}})


        print(f"erned: {erned}")
        print(f"profit: {profit}")
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$inc": {'total_sum_invest': +float(order_sell["cummulativeQuoteQty"]),"earned":+erned,"total_profit":+profit*100,"cikle_count":+1}})
        Orders.update_one({"bot_id": ObjectId(bot_id), "sell_id":order_sell["orderId"]},{"$set": {"profit": profit*100,"erned":erned, "finish": True}})
        Send.insert_one({"bot":bt['name'],"valute_par":bt['valute_par'],"profit":profit*100,"erned":erned,"bye":order['bye']["cummulativeQuoteQty"],"price_bye":order['bye']["price"],"sell":order_sell["cummulativeQuoteQty"],"price_sell":order_sell["price"],"send":False})


    def reinv50Math(self,order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]

        order_bye = float(Orders.find_one({"sell_id":order_sell['orderId']})['bye']['cummulativeQuoteQty'])
        profit = (float(order_sell['cummulativeQuoteQty']) - order_bye)*0.5
        inv_sum = float(order_sell['cummulativeQuoteQty']) - profit

        return {"inv_sum":toFixed(inv_sum,8),"profit":toFixed(profit,8)}

    def setLastPrice(self,bot_id,price):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        print(f"last_price: {price} bot: {bot_id}")
        last_prices = Bots.find_one({"_id": ObjectId(bot_id)})['last_price']
        if price in last_prices:
            pass
        else:
            Bots.update_one({"_id": ObjectId(bot_id)},{"$push":{"last_price":price}})

    def dropLastPrice(self,bot_id,order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]
        last_price = str(Orders.find_one({"bot_id": ObjectId(bot_id),"sell_id":order_sell["orderId"]})['bye']["price"])
        last_prices = Bots.find_one({"_id": ObjectId(bot_id)})['last_price']
        try:
            last_prices.remove(last_price)
        except:
            pass

        Bots.update_one({"_id": ObjectId(bot_id)},{"$set":{"last_price":last_prices}})


    def dropLastPriceBye(self,bot_id,order_bye):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]
        last_price = str(
            Orders.find_one({"bot_id": ObjectId(bot_id), "bye_id": order_bye["orderId"]})['bye']["price"])
        last_prices = Bots.find_one({"_id": ObjectId(bot_id)})['last_price']
        try:
            last_prices.remove(last_price)
        except:
            pass

        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"last_price": last_prices}})


    def dropLastPriceSell(self,bot_id,order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]

        order_bye = Orders.find_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]})['bye']
        Orders.delete_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]})

        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_sell["orderId"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})

        Bots.update_one({"_id": ObjectId(bot_id)},
                        {"$inc": {'total_sum_invest': +float(order_bye['price'])*float(order_sell['origQty'])}})
        last_price = str(order_bye['price'])
        last_prices = Bots.find_one({"_id": ObjectId(bot_id)})['last_price']
        last_prices.remove(last_price)
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"last_price": last_prices}})

    def reloadSell(self,bot_id,order_sell,new_order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]

        order_bye = Orders.find_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]})['bye']
        Orders.delete_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]})

        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_sell["orderId"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})

        Bots.update_one({"_id": ObjectId(bot_id)},
                        {"$inc": {'total_sum_invest': +float(new_order_sell['price']) * float(order_sell['origQty'])}})
        last_price = str(order_bye['price'])
        last_prices = Bots.find_one({"_id": ObjectId(bot_id)})['last_price']
        last_prices.remove(last_price)
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {"last_price": last_prices}})


    def reloadSell_test(self,bot_id,order_sell,new_order_sell):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]
        Orders = db["Orders"]
        orders = Bots.find_one({"_id": ObjectId(bot_id)})['orders']
        orders.remove(order_sell["orderId"])
        Bots.update_one({"_id": ObjectId(bot_id)}, {"$set": {'orders': orders}})

        Bots.update_one({"_id": ObjectId(bot_id)}, {"$push": {'orders': new_order_sell["orderId"]}})

        Orders.update_one({"bot_id": ObjectId(bot_id), "sell_id": order_sell["orderId"]},{"$set":{"sell":new_order_sell,"sell_id":new_order_sell["orderId"]}})

    def UpdateSymbolInfo(self,client):
        inf = client.get_exchange_info()
        db = self.classter["SnakeBot"]
        Symbols = db["Symbols"]
        Symbols.delete_many({})

        for i in inf['symbols']:
            Symbols.insert_one(i)

    def GetSymbolInfo(self,symbol):
        db = self.classter["SnakeBot"]
        Symbols = db["Symbols"]

        return Symbols.find_one({"symbol":symbol})
