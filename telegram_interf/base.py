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

    def regBot(self, valute_par, total_sum_invest, name, sum_invest, step, min_price, max_price):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        post = {
            "valute_par": valute_par,
            "name": name,
            "sum_invest": float(sum_invest),
            "total_sum_invest": float(total_sum_invest),
            'orders': [],
            "step": step / 100000000,
            "full_orders": [],  # [{"bye":0.0..30,"sell":0.0..31},{"bye":0.0..30,"sell":False}]
            "count_hev": 0,  # записывать количество
            'spent': 0,
            'spent_true': 0,
            "bye_order": False,
            'on': True,
            "reinvest": True,
            "total_profit": 0,
            "cikle_count": 0,
            "min_price": min_price,
            "max_price": max_price,
            "base_sum_invest": float(sum_invest),
            "base_total_sum_invest": float(total_sum_invest),
            "earned": 0,
            "last_price": []
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
    def dellBot(self,bot_id):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        Bots.delete_one({"_id": ObjectId(bot_id)})

    def offoronBot(self,bot_id,onoff):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        Bots.update_one({"_id": ObjectId(bot_id)},{"$set":{"on":onoff}})


    def offoronReivest(self,bot_id,reinv):
        db = self.classter["SnakeBot"]
        Bots = db["Bots"]

        Bots.update_one({"_id": ObjectId(bot_id)},{"$set":{"reinvest":reinv}})


    def getSend(self):
        db = self.classter["SnakeBot"]
        Send = db["Send"]

        return Send.find({"send":False})

    def setSend(self,send_id):
        db = self.classter["SnakeBot"]
        Send = db["Send"]

        Send.update_one({"_id":ObjectId(send_id)},{"$set":{"send":True}})

    def findOrder(self,bot_id):
        db = self.classter["SnakeBot"]
        Orders = db["Orders"]

        Orders.find({"bot_id": ObjectId(bot_id), "finish":  False})
