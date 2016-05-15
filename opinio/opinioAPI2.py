from flask import Flask

app = Flask(__name__)

author = 'Sumit'
#!flask/bin/python
from flask import Flask, jsonify
from flask import request
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import string
import random
import datetime


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getCategoryWithOffersOnDate(date, clientId, offerId):
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    clientsDb = db.Clients
    clientInfo = clientsDb.find({"_id": ObjectId(clientId), "Offers.ValidStartDate": {"$lte": date},
                    "Offers.ValidEndDate": {"$gte": date}})
    categories = []
    for data in clientInfo:
        offers = data['Offers']
        for x in offers:
            if (date >= x['ValidStartDate'] and date <= x['ValidEndDate'] and str(x['OfferId']) != offerId):
                categories.append({'categoryId':x['CategoryId'], 'discount':x['DiscountPercent']})
    connection.close()
    return categories


def getItemsWithOffersOnDate(date, clientId, offerId):
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    clientsDb = db.Clients
    clientInfo = clientsDb.find({"_id": ObjectId(clientId), "Offers.ValidStartDate": {"$lte": date},
                    "Offers.ValidEndDate": {"$gte": date}, 'ApplicableOnSpecificProductsOnly': True})
    items = []

    for data in clientInfo:
        offers = data['Offers']
        for x in offers:
            if (date >= x['ValidStartDate'] and date <= x['ValidEndDate'] and str(x['OfferId']) != offerId and x['ApplicableOnSpecificProductsOnly'] == True):
                items.append({'itemId':x['ProductId'], 'discount':x['DiscountPercent']})
    connection.close()
    return items

def updateOrderStat(userId, parentCategoryId, itemId, offerDiscount, orderDateTime,clientId, offerId):
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    usersDb = db.Users
    rejectedOffersItems = getItemsWithOffersOnDate(orderDateTime, clientId, offerId)
    rejectedOffersCat = getCategoryWithOffersOnDate(orderDateTime, clientId, offerId)

    userInfoList = usersDb.find({'_id':ObjectId(userId)}).limit(1)
    categoryAvgDiscount = offerDiscount
    categoryMinDiscount = offerDiscount
    categoryMaxDiscount = offerDiscount
    purchaseCount = 1

    itemsAvgDiscount = offerDiscount
    itemsMinDiscount = offerDiscount
    itemsMaxDiscount = offerDiscount
    purchaseCountItem = 1
    for x in userInfoList:
        newEntry = True
        for data in x['Interests']['Ordered']['Categories']:
            if str(data['CategoryId']) == str(parentCategoryId):
                if data['MinDiscount'] < categoryMinDiscount:
                    categoryMinDiscount = data['MinDiscount']
                if data['MaxDiscount'] > categoryMaxDiscount:
                    categoryMaxDiscount = data['MaxDiscount']
                categoryAvgDiscount = ((data['AvgDiscount']*data['PurchaseCount'])+offerDiscount)/(data['PurchaseCount']+1)
                purchaseCount += data['PurchaseCount']
                newEntry = False
        if newEntry == False:

            usersDb.update_one({'_id': ObjectId(userId), 'Interests.Ordered.Categories.CategoryId': ObjectId(parentCategoryId)},
                               {'$set': { 'Interests.Ordered.Categories': {'AvgDiscount':categoryAvgDiscount,
                                         'MaxDiscount':categoryMaxDiscount,
                                         'MinDiscount':categoryMinDiscount,
                                         'PurchaseCount':purchaseCount}}})
        else:
            entry = {'CategoryId': ObjectId(parentCategoryId),
                     'AvgDiscount':categoryAvgDiscount,
                                         'MaxDiscount':categoryMaxDiscount,
                                         'MinDiscount':categoryMinDiscount,
                                         'PurchaseCount':purchaseCount,
                                         'AvoidCount':0,
                                         'AvoidAvgDiscount': 0,
                                         'AvoidMinDiscount': 0,
                                         'AvoidMaxDiscount': 0 }
            usersDb.update_one({'_id': ObjectId(userId)}, {'$push': {'Interests.Ordered.Categories': entry}})

        newEntry = True
        for data in x['Interests']['Ordered']['Items']:
            if str(data['ItemId']) == str(itemId):
                if data['MinDiscount'] < itemsMinDiscount:
                    itemsMinDiscount = data['MinDiscount']
                if data['MaxDiscount'] > itemsMaxDiscount:
                    itemsMaxDiscount = data['MaxDiscount']
                itemsAvgDiscount = ((data['AvgDiscount']*data['PurchaseCount'])+offerDiscount)/(data['PurchaseCount']+1)
                purchaseCountItem += data['PurchaseCount']
                newEntry = False
        if newEntry == False:

            usersDb.update_one({'_id': ObjectId(userId), 'Interests.Ordered.Items.ItemId': ObjectId(itemId)},
                               {'$set': { 'Interests.Ordered.Items': {'AvgDiscount':itemsAvgDiscount,
                                         'MaxDiscount':itemsMaxDiscount,
                                         'MinDiscount':itemsMinDiscount,
                                         'PurchaseCount':purchaseCountItem}}})
        else:
            usersDb.update_one({'_id': ObjectId(userId) },
                               {'$push': {'Interests.Ordered.Items':
                                              {'ItemId': ObjectId(itemId),
                                         'AvgDiscount':itemsAvgDiscount,
                                         'MaxDiscount':itemsMaxDiscount,
                                         'MinDiscount':itemsMinDiscount,
                                         'PurchaseCount':purchaseCountItem,
                                         'AvoidCount':0,
                                         'AvoidAvgDiscount':0,
                                         'AvoidMinDiscount':0,
                                         'AvoidMaxDiscount': 0}}})
    # Category Part
    rejectedCats = []
    rejectedCatsDict = {}
    for x in rejectedOffersCat:
        rejectedCats.append(str(x['categoryId']))
        rejectedCatsDict[str(x['categoryId'])]=x['discount']
    for x in userInfoList:
        for data in x['Interests']['Ordered']['Categories']:
            if str(data['CategoryId']) in rejectedCatsDict:
                avoidMinDiscount = rejectedCatsDict[str(data['CategoryId'])]
                avoidMaxDiscount = rejectedCatsDict[str(data['CategoryId'])]
                avoidAvgDiscount = rejectedCatsDict[str(data['CategoryId'])]
                avoidCount = 1
                offerDiscount = rejectedCatsDict[str(data['CategoryId'])]
                if data['AvoidMinDiscount'] < avoidMinDiscount:
                    avoidMinDiscount = data['AvoidMinDiscount']
                if data['AvoidMaxDiscount'] > avoidMaxDiscount:
                    avoidMaxDiscount = data['AvoidMaxDiscount']
                avoidAvgDiscount = ((data['AvoidAvgDiscount']*data['AvoidCount'])+offerDiscount)/(data['AvoidCount']+1)
                avoidCount += data['AvoidCount']
                usersDb.update_one({'_id': ObjectId(userId) },
                               {'$set': { 'Interests.Ordered.Categories':{'CategoryId': ObjectId(str(data['CategoryId'])),
                                         'AvoidCount':avoidCount,
                                         'AvoidAvgDiscount':avoidAvgDiscount,
                                         'AvoidMinDiscount':avoidMinDiscount,
                                         'AvoidMaxDiscount':avoidMaxDiscount}}})
                rejectedCatsDict.pop(str(data['CategoryId']), None)
        for key,value in rejectedCatsDict.iteritems():
            avoidMinDiscount = value
            avoidMaxDiscount = value
            avoidAvgDiscount = value
            avoidCount = 1
            offerDiscount = value
            usersDb.update_one({'_id': ObjectId(userId) },
                               {'$push': { 'Interests.Ordered.Categories':{'CategoryId': ObjectId(key),
                                         'AvgDiscount':0,
                                         'MaxDiscount':0,
                                         'MinDiscount':0,
                                         'PurchaseCount':0,
                                         'AvoidCount':avoidCount,
                                         'AvoidAvgDiscount':avoidAvgDiscount,
                                         'AvoidMinDiscount':avoidMinDiscount,
                                         'AvoidMaxDiscount':avoidMaxDiscount}}})

    # Items Part
    rejectedItems = []
    rejectedItemsDict = {}
    for x in rejectedOffersItems:
        rejectedItems.append(str(x['itemId']))
        rejectedItemsDict[str(x['itemId'])] = x['discount']
    for x in userInfoList:
        for data in x['Interests']['Ordered']['Items']:
            if str(data['ItemId']) in rejectedItemsDict:
                avoidMinDiscount = rejectedItemsDict[str(data['ItemId'])]
                avoidMaxDiscount = rejectedItemsDict[str(data['ItemId'])]
                avoidAvgDiscount = rejectedItemsDict[str(data['ItemId'])]
                avoidCount = 1
                offerDiscount = rejectedItemsDict[str(data['ItemId'])]
                if data['AvoidMinDiscount'] < avoidMinDiscount:
                    avoidMinDiscount = data['AvoidMinDiscount']
                if data['AvoidMaxDiscount'] > avoidMaxDiscount:
                    avoidMaxDiscount = data['AvoidMaxDiscount']
                avoidAvgDiscount = ((data['AvoidAvgDiscount']*data['AvoidCount'])+offerDiscount)/(data['AvoidCount']+1)
                avoidCount += data['AvoidCount']
                usersDb.update_one({'_id': ObjectId(userId) },
                               {'$set': { 'Interests.Ordered.Items':{'ItemId': ObjectId(str(data['ItemId'])),
                                         'AvoidCount':avoidCount,
                                         'AvoidAvgDiscount':avoidAvgDiscount,
                                         'AvoidMinDiscount':avoidMinDiscount,
                                         'AvoidMaxDiscount':avoidMaxDiscount}}})
                rejectedItemsDict.pop(str(data['ItemId']), None)
        for key,value in rejectedItemsDict.iteritems():
            avoidMinDiscount = value
            avoidMaxDiscount = value
            avoidAvgDiscount = value
            avoidCount = 1
            offerDiscount = value
            usersDb.update_one({'_id': ObjectId(userId) },
                               {'$push': {'Interests.Ordered.Items':{'ItemId': ObjectId(key),
                                         'AvgDiscount':0,
                                         'MaxDiscount':0,
                                         'MinDiscount':0,
                                         'PurchaseCount':0,
                                         'AvoidCount':avoidCount,
                                         'AvoidAvgDiscount':avoidAvgDiscount,
                                         'AvoidMinDiscount':avoidMinDiscount,
                                         'AvoidMaxDiscount':avoidMaxDiscount}}})


    return
'''
# def updateBrowsingStat(userId, parentCategoryId, itemId, viewedDateTime):

    # return
'''








# def find
app = Flask(__name__)


@app.route('/shortlistMsg', methods=['POST'])
def shortListMsgs():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    clientsDb = db.Clients
    usersDb = db.Users
    currDate = datetime.datetime.now()
    clientInfo = clientsDb.find({"Offers.ValidStartDate": {"$lte": datetime.datetime.now()},
                "Offers.ValidEndDate": {"$gte": datetime.datetime.now()}})
    categories = []
    for data in clientInfo:
        offers = data['Offers']
        for x in offers:
            if (currDate >= x['ValidStartDate'] and currDate <= x['ValidEndDate']):
                categories.append({'CategoryId':x['CategoryId'], 'discount':x['DiscountPercent'], 'OfferId': x['OfferId'], 'ClientId': data['_id']})

    clientInfo = clientsDb.find({"Offers.ValidStartDate": {"$lte": currDate},
                    "Offers.ValidEndDate": {"$gte": currDate}, 'ApplicableOnSpecificProductsOnly': True})
    items = []

    for data in clientInfo:
        offers = data['Offers']
        for x in offers:
            if (currDate >= x['ValidStartDate'] and currDate <= x['ValidEndDate'] and x['ApplicableOnSpecificProductsOnly'] == True):
                items.append({'ItemId':x['ProductId'], 'discount':x['DiscountPercent'], 'OfferId': x['OfferId'], 'ClientId': data['_id']})
    finalRes = []
    for x in categories:
        usersInfo = usersDb.find({'Interested.Ordered.Categories.AvgDiscount' :{'$lt': x['discount']}})
        for y in usersInfo:
            finalRes.append({'UserName':y['UserName'], 'UserId': y['_id'], 'OfferId': x['OfferId'], 'ClientId': x['ClientId']})

    for x in items:
        usersInfoItems = usersDb.find({'Interested.Ordered.Categories.AvgDiscount' :{'$lt': x['discount']}})
        for y in usersInfo:
            finalRes.append({'UserName':y['UserName'], 'UserId': y['_id'], 'OfferId': x['OfferId'], 'ClientId': x['ClientId']})

    return json.dumps(finalRes)


@app.route('/insertUsersInfo', methods=['POST'])
def insertUsersInfo():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    usersDb = db.Users
    reqData = request.json
    clientId = reqData['ClientId']
    userDetails = reqData['UsersInfo']
    for data in userDetails:
        checkUser = usersDb.find({'ContactNo': data['ContactNo'], 'EmailId': data['EmailId']} )
        orderHistory = []
        browsingHistory = []
        userName = data['UserName']
        userLocation = data['UserPrimaryLocation']
        contactNo = data['ContactNo']
        emailId = data['EmailId']

        orderStat={}

        for x in data['OrderHistory']:
            parentCategoryRes = db.Products.find({'ParentCategoryName': x['ParentCategoryName'], 'ItemName': x['ItemName']}).limit(1)
            orderData = {}
            for y in parentCategoryRes:
                orderData['ParentCategoryId'] = y['ParentCategoryId']
                orderData['ParentCategoryName'] = y['ParentCategoryName']
                orderData['ItemName'] = y['ItemName']
                orderData['ItemId'] = y['_id']
            orderData['OrderDateTime'] = datetime.datetime.strptime(x['OrderDateTime'], "%d/%m/%Y %H:%M:%S.%f")
            orderData['OfferId'] = x['OfferId']
            orderData['OfferDiscount'] = x['OfferDiscount']
            orderData['BillingLocation'] = x['BillingLocation']
            orderData['OrderAmount'] = x['OrderAmount']
            orderData['UnitCount'] = x['UnitCount']
            orderData['ClientId'] = ObjectId(clientId)
            orderHistory.append(orderData)

        for x in data['BrowsingHistory']:
            parentCategoryRes = db.Products.find({'ParentCategoryName': x['ParentCategoryName'], 'ItemName': x['ItemName']}).limit(1)
            browsingData = {}
            for y in parentCategoryRes:
                browsingData['ParentCategoryId'] = y['ParentCategoryId']
                browsingData['ParentCategoryName'] = y['ParentCategoryName']
                browsingData['ItemName'] = y['ItemName']
                browsingData['ItemId'] = y['_id']
            browsingData['ViewedDateTime'] = datetime.datetime.strptime(x['ViewedDateTime'], "%d/%m/%Y %H:%M:%S.%f")
            browsingData['ClientId'] = ObjectId(clientId)
            browsingHistory.append(browsingData)
        userId = ''
        if checkUser.count() == 0:
            userData= {}
            userData['UserName'] = userName
            userData['UserPrimaryLocation'] = userLocation
            userData['UserLastLocation'] = userLocation
            userData['ContactNo'] = contactNo
            userData['EmailId'] = emailId
            userData['BrowsingHistory'] = browsingHistory
            userData['OrderHistory'] = orderHistory
            userData['SentMessages'] = {}
            userData['Interests'] = {'Ordered':{'Categories': [], 'Items': []}}
            userId += str(usersDb.save(userData))
        else:
            id = ''
            for a in checkUser:
                id += str(a['_id'])
            userId += str(id)
            usersDb.update_one({'_id':userId}, {'$push': {'BrowsingHistory': browsingHistory, 'OrderHistory': orderHistory}})
        connection.close()
        for x in orderHistory:

            updateOrderStat(userId, x['ParentCategoryId'], x['ItemId'], x['OfferDiscount'], x['OrderDateTime'], clientId, x['OfferId'])
        # for x in browsingHistory:
        #     updateBrowsingStat(userId, x['ParentCategoryId'], x['ItemId'], x['ViewedDateTime'])
    return "Users Info Updated Successfully"


@app.route('/createOffers', methods=['POST'])
def createOffers():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    client = db.Clients
    data = request.json
    checkPrev = client.find({'_id': ObjectId(data['ClientId']), 'Offers.OfferId': data['OfferId'], 'Offers.OfferName': data['OfferName']})
    print checkPrev.count()
    if checkPrev.count() != 0:
        return 'Offer already stored'
    productIds = []
    for x in data['ProductNames']:
        idField = db.Products.find({'ItemName': x})
        id  = ''
        for a in idField:
            id += str(a['_id'])
        productIds.append(ObjectId(id))
    catid  = ''

    catidField = db.Categories.find({'CategoryName': data['CategoryName']})
    for a in catidField:
        catid += str(a['_id'])

    offer = {'OfferId': data['OfferId'], 'OfferName': data['OfferName'], 'CouponCode': data['CouponCode'], 'DiscountPercent': data['DiscountPercent'],
         'ApplicableOnCategory': data['ApplicableOnCategory'], 'ApplicableOnSpecificProductsOnly': data['ApplicableOnSpecificProductsOnly'],
             'ProductId': productIds, 'CategoryId': ObjectId(catid),
         'ValidStartDate': datetime.datetime.strptime(data['ValidStartDate'], "%d/%m/%Y %H:%M:%S.%f"),
             'ValidEndDate': datetime.datetime.strptime(data['ValidEndDate'], "%d/%m/%Y %H:%M:%S.%f")}

    client.update_one({'_id': ObjectId(data['ClientId'])}, {'$push': {'Offers': offer }})
    return 'Offer Created'
    # return 'Hello World!'

@app.route("/registerClient", methods=['POST'])
def registerClient():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    client = db.Clients
    data = request.json
    clientInfo = {'ClientName': data['Name'], 'Password': data['Password'], 'EmailId': data['EmailId'], 'ClientKey': id_generator(), 'Products': [], 'Offers': []}
    try:
        res = client.save(clientInfo)
    except pymongo.errors.DuplicateKeyError, e:
        print "One repeated User"
    return "Client Registered"

@app.route("/login", methods=['POST'])
def login():
    print request.content_encoding
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    client = db.Clients.find({'EmailId': request.json['EmailId'], 'Password': request.json['Password']}).limit(1)
    res = {}
    if client.count() != 0:
        for x in client:
            res['ClientName']= x['ClientName']
            res['Result'] = "Success"
            res['Key'] = x['ClientKey']
            res['ClientId'] = str(x['_id'])
    else:
        res['ClientName']= ''
        res['Result'] = "Failure"
        res['Key'] = ''
        res['ClientId'] = ''
    print res
    return json.dumps(res)


@app.route("/createProducts", methods=['POST'])
def createProducts():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    parentNameRes = db.Categories.find({'CategoryName':request.json['ParentCategoryName']}).limit(1)
    product = db.Products
    parentName = []
    for x in parentNameRes:
        parentName.append({'CategoryName':x['CategoryName'], 'CategoryId':x['_id']})

    data = request.json
    for x in data['ItemName']:
        entry = {'ItemName': x, 'ParentCategoryName': parentName[0]['CategoryName'], 'ParentCategoryId': parentName[0]['CategoryId']}
        try:
            res = product.save(entry)
            res1 = db.Clients.update_one({'_id': ObjectId(request.json['ClientId'])}, {'$push': {'Products':{'ItemId': ObjectId(res), 'ParentCategoryId': parentName[0]['CategoryId']}} })
        except pymongo.errors.DuplicateKeyError, e:
            print "One repeat name :"+x

    # print data
    return "stored"





@app.route("/getProducts", methods=['POST'])
def getProducts():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    products = db.Products.find({})
    res = {}
    for x in products:
        if x['ParentCategoryName'] not in res:
            res[x['ParentCategoryName']] = []
        res[x['ParentCategoryName']].append(x['ItemName'])
    return json.dumps(res)

@app.route("/getCategories", methods=['POST'])
def getCategories():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    cat = db.Categories.find({})
    res = []
    for x in cat:
        res.append(x['CategoryName'])
        # print x
    return json.dumps(res)

@app.route("/createCategories", methods=['POST'])
def createCategories():
    connection = MongoClient('localhost', 27017)
    db = connection['TrialDB']
    cat = db.Categories
    data = request.json
    for x in data['CategoryName']:
        entry = {'CategoryName': x}
        try:
            res = cat.save(entry)
        except pymongo.errors.DuplicateKeyError, e:
            print "One repeat name :"+x
    print data
    return "stored"





    return "Msgs Sent and DB Updated"
if __name__ == '__main__':
    app.run(host='0.0.0.0')
