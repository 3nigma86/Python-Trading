#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 09:45:42 2022

@author: enigma
"""

from flask import Flask, request
import requests
import json, os
import urllib.parse
import hashlib
import hmac
import base64
import time
import uuid
import math
import smtplib
import datetime
import csv
from time import sleep
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)
"""
SANDBOX
api_key = ''
api_secret = ''
api_passphrase = ""
url = 'https://openapi-sandbox.kucoin.com'
"""
api_key = ''
api_secret = ''
url = 'https://api.kucoin.com'
api_passphrase = ''
in_trade = []
side_tracker = []
id_tracker = []
total_size = []
growth = []
statistics = []
flag_up = False
wallet_timer = time.time()
wallet = 13000

file = open('trades.csv', 'r')
rd = csv.reader(file)
rows = 0
for row in rd:
    rows+=1
    cols = len(row)
file.close()
trade_group = [['0' for i in range(cols)] for j in range(rows)]
file = open('trades.csv','r')
rd = csv.reader(file)
i = 0
prefix = "GET"
for row in rd:
    path = '/api/v1/market/stats?symbol='+row[0]
    now = int(time.time() * 1000)
    data = ''
    data_json = json.dumps(data)
    str_to_sign = str(now) + prefix + path + data_json
    signature = base64.b64encode(
            hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
            }
    response = requests.request(prefix, url+path, headers=headers, data=data_json)
    response_json = json.loads(response.text)
    volume = response_json['data']['volValue']
    for j in range(0,len(row)):
        trade_group[i][j] = row[j]
    trade_group[i][1] = str(volume)
    i += 1
file.close()
prefix = 'DELETE'
path = '/api/v1/orders?tradeType=MARGIN_TRADE'
now = int(time.time() * 1000)
data = ''
data_json = json.dumps(data)
str_to_sign = str(now) + prefix + path + data_json
signature = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
        }
response = requests.request(prefix, url+path, headers=headers, data=data_json)
response_json = json.loads(response.text)
prefix = 'GET'
path = '/api/v1/margin/account'
now = int(time.time() * 1000)
data = ''
data_json = json.dumps(data)
str_to_sign = str(now) + prefix + path + data_json
signature = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
        }
response = requests.request(prefix, url+path, headers=headers, data=data_json)
response_json = json.loads(response.text)
prefix = 'GET'
path = '/api/v1/symbols'
now = int(time.time() * 1000)
data = ''
data_json = json.dumps(data)
str_to_sign = str(now) + prefix + path + data_json
signature = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
        }
increment_response = requests.request(prefix, url+path, headers=headers, data=data_json)
increment_json = json.loads(increment_response.text)
for i in range(0,len(response_json['data']['accounts'])):
    if float(response_json['data']['accounts'][i]['availableBalance']) > 0 and response_json['data']['accounts'][i]['currency'] != 'USDT' or float(response_json['data']['accounts'][i]['liability']) > 0 and response_json['data']['accounts'][i]['currency'] != 'USDT': 
        print('\n'+str(response_json['data']['accounts'][i])+'\n')
        for j in range(0,len(increment_json['data'])):
            if increment_json['data'][j]['symbol'] == response_json['data']['accounts'][i]['currency']+'-USDT':
                digits = increment_json['data'][j]['baseIncrement']
                min_size = float(increment_json['data'][j]['baseMinSize'])
                break
        if float(response_json['data']['accounts'][i]['availableBalance']) > float(response_json['data']['accounts'][i]['liability']):
            amount_to_trade = float(response_json['data']['accounts'][i]['availableBalance'])-float(response_json['data']['accounts'][i]['liability'])
            trade_type = 'sell'
        if float(response_json['data']['accounts'][i]['availableBalance']) < float(response_json['data']['accounts'][i]['liability']):
            amount_to_trade = float(response_json['data']['accounts'][i]['liability'])-float(response_json['data']['accounts'][i]['availableBalance'])
            amount_to_trade = amount_to_trade + min_size
            trade_type = 'buy'
        digits = len(str(digits)) - 2
        amount_to_trade = math.floor(amount_to_trade * 10 ** digits)/ 10 ** digits
        prefix = 'POST'
        path = '/api/v1/margin/order'
        now = int(time.time() * 1000)
        data = data = {"clientOid":str(uuid.uuid4()),"side":str(trade_type),"symbol":response_json['data']['accounts'][i]['currency']+'-USDT',"type":"market",'size':str(amount_to_trade)}
        data_json = json.dumps(data)
        str_to_sign = str(now) + prefix + path + data_json
        signature = base64.b64encode(
            hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
        passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": str(now),
            "KC-API-KEY": api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
            }
        order_response = requests.request(prefix, url+path, headers=headers, data=data_json)
        order_json = json.loads(order_response.text)
print(trade_group,'\n')




@app.route('/',methods=['POST'])
def get_webhook():
    global id_tracker, in_trade, flag_up, side_tracker, total_size, trade_group
    
    if request.method == 'POST':
        while flag_up == True:
            sleep(.5)
        flag_up = True
        print("#############################################################################################################################################################################################################################")
        output = str(request.data, 'UTF-8')
        output_json = json.loads(output)
        now = datetime.datetime.now()
        print(str(now))
        print(output_json)
        ticker = output_json["ticker"]
        position = int(float(output_json["position"]))
        order_type = output_json["order"]
        price = float(output_json['price'])
        digits = get_price_increment(ticker)
        digits = len(str(digits)) - 2
        price = math.floor(price * 10 ** digits)/ 10 ** digits
        if order_type == "Change-Order":
            old_order = output_json['old-order']
            new_order = output_json['new-order']
            for i in range(0,len(id_tracker)):
                for j in range(0,len(id_tracker[i])):
                    if id_tracker[i][j] == old_order:
                        id_tracker[i][j] = new_order
                        print("ID List Updated")
                        flag_up = False
                        return "ID List Updated"
            flag_up = False
            print("Order Not Found")
            return "Order Not Found"
        if order_type == "Remove-Current-Trade":
            pos = in_trade.index(ticker)
            in_trade.remove(ticker)
            side_tracker.pop(pos)
            id_tracker.pop(pos)
            total_size.pop(pos)
            print("Current Active Trades \n",in_trade,"\n",side_tracker,"\n",total_size, "\n",id_tracker)
            flag_up = False
            return 'Trade Removed'
        if order_type == "Remove-Trade-Group":
            file = open('trades.csv', 'r')
            print("File Open")
            rd = csv.reader(file)
            temp = []
            for line in rd:
                temp.append(line)
            file.close()
            file = open('trades.csv','w')
            wr = csv.writer(file)
            for i in range(0, len(temp)):
                if temp[i][0] != ticker:
                    wr.writerow(temp[i])
            file.close()
            populate_trade_group()
            flag_up = False
            return 'Trade Group Removed'
        for i in range(0,len(trade_group)):
            if trade_group[i][0] == ticker:
                break
            if trade_group[i][0] != ticker and i == len(trade_group)-1:
                print('Ticker Not In Trade Group')
                row = []
                volume = get_ticker_volume(ticker)
                for j in range(0, len(trade_group[i])):
                    if j == 0:
                        row.append(ticker)
                    if j == 1:
                        row.append(volume)
                    if j != 0 and j != 1:
                        row.append('1')
                trade_group.append(row)
                print(trade_group)
                file = open('trades.csv', 'w')
                rd = csv.writer(file)
                row = []
                for i in range(0,len(trade_group)):
                    for j in range(0,len(trade_group[i])):
                        if j == len(trade_group[i]) and i != len(trade_group):
                            row.append(trade_group[i][j]+'\n')
                            break
                        elif j == len(trade_group[i]) and i == len(trade_group):
                            row.append(trade_group[i][j])
                        row.append(trade_group[i][j])
                    rd.writerow(row)
                    row.clear()
                file.close()
             
        if ticker not in in_trade and position == 0:
            print("Closing position not opened")
            flag_up = False
            return "No Trade"
        if ticker in in_trade and position == 0:
            ticker_index = in_trade.index(ticker)
            order_id = []
            for i in range(0,len(id_tracker[ticker_index])):
                order_id.append(id_tracker[ticker_index][i])
            print(order_id)
            close_position(ticker,order_id,order_type, price, ticker_index)
            flag_up = False
            return "Closed or Maybe not"
        if ticker not in in_trade and position != 0:
            print("Placing Order")
            place_order(ticker, order_type, price)
            flag_up = False
            return "Made Order"
        print("No Activity Found")
        flag_up = False
        return 'Thanks!'  

def place_order(ticker, order_type, price):
    global in_trade, id_tracker, api_key, api_secret, loan_tracker, total_size, side_tracker
    
    order_amount = get_wallet(ticker, order_type, price)
    data = {"clientOid":str(uuid.uuid4()),"side":str(order_type),"symbol":str(ticker), "type":"limit",'size':str(order_amount),"autoBorrow":True,"price":str(price)}
    response = SendRequest('POST','/api/v1/margin/order', json.dumps(data))
    while response[1]['code'] == "429000":
        sleep(.5)
        response = SendRequest('POST','/api/v1/margin/order', json.dumps(data))
    if response[0] == 200 and response[1]['code'] == "200000":
        in_trade.append(ticker)
        position = in_trade.index(ticker)
        print(position)
        side_tracker.append(order_type)
        total_size.append(order_amount)
        create_loss_profit(ticker, order_type,price, order_amount, in_trade.index(ticker),response[1]['data']['orderId'])
    print("Current Active Trades \n",in_trade,"\n",side_tracker,"\n",total_size, "\n",id_tracker)
    
    
def close_position(ticker, orderID, side, price, ticker_index):
    global in_trade, id_tracker, api_key, api_secret, total_size, side_tracker
    
    size = get_trade_info(orderID, ticker, side)
    data = {"clientOid":str(uuid.uuid4()),"side":str(side),"symbol":str(ticker),"type":"limit","size":str(size),"price":str(price)}
    response = SendRequest('POST','/api/v1/margin/order',json.dumps(data))
    while response[1]['code'] == "429000":
        sleep(.5)
        response = SendRequest('POST','/api/v1/margin/order',json.dumps(data))
    repay_loan(ticker, side)
    in_trade.remove(ticker)
    id_tracker.pop(ticker_index)
    side_tracker.pop(ticker_index)
    total_size.pop(ticker_index)
    print("Current Active Trades \n",in_trade,"\n",side_tracker,"\n",total_size, "\n",id_tracker) 
    
    
    
def get_wallet(ticker, order_type, price):
    global api_key, api_secret, in_trade, growth, trade_group, wallet_timer, master_wallet
    
    if time.time() - wallet_timer > 30:
        response = SendRequest('GET','/api/v1/margin/account', '')
        total_assets = 0.00
        total_liability = 0.00
        for i in range (0,len(response[1]['data']['accounts'])):
            if "USDT" == response[1]["data"]['accounts'][i]['currency']:
                total_assets += float(response[1]['data']['accounts'][i]['availableBalance'])
                total_liability += float(response[1]['data']['accounts'][i]['liability'])
            if response[1]['data']['accounts'][i]['currency'] != "USDT" and float(response[1]['data']['accounts'][i]['availableBalance']) > 0 or response[1]['data']['accounts'][i]['currency'] != "USDT" and float(response[1]['data']['accounts'][i]['liability']) > 0:
                ticker_price = float(get_ticker_price(response[1]['data']['accounts'][i]['currency'] + '-USDT'))
                total_assets += float(response[1]['data']['accounts'][i]['availableBalance']) * ticker_price
                total_liability += float(response[1]['data']['accounts'][i]['liability']) * ticker_price
        master_wallet = int(((total_assets - total_liability)*5)*.9)
        if len(growth) == 0:
            growth.append(total_assets - total_liability)
        print(str((((total_assets-total_liability) - growth[0])/growth[0])*100) + "%")
    for i in range(0, len(trade_group)):
        if trade_group[i][0] == ticker:
            position = i
            break
    wallet_timer = time.time()
    print('wallet='+str(master_wallet))
    if float(trade_group[position][1]) >= 10000000:
        vol = 0
        for i in range(0, len(trade_group)):
            if float(trade_group[i][1]) >= 10000000:
                vol += 1
        sub_wallet = int((master_wallet * .75)/vol)
    if float(trade_group[position][1]) < 10000000:
        vol = 0
        for i in range(0, len(trade_group)):
            if float(trade_group[i][1]) < 10000000:
                vol += float(trade_group[i][1]) 
        sub_wallet = int((master_wallet * .25))*(float(trade_group[position][1])/vol)
    sub_wallet = sub_wallet/price
    digits = get_increment(ticker)
    digits = len(str(digits)) - 2
    sub_wallet = math.floor(sub_wallet * 10 ** digits)/ 10 ** digits
    print("wallet =",sub_wallet)
    return sub_wallet
    
    
    
def get_trade_info(orderID, ticker, side):
    global trade_group
    
    for i in range(0,len(trade_group)):
        if trade_group[i][0] == ticker:
            place = i
            break
    profits_left = 0
    response = SendRequest('GET', '/api/v1/stop-order', '')
    for i in range(0 ,len(response[1]['data']['items'])):
        if response[1]['data']['items'][i]['symbol'] == ticker:
            if response[1]['data']['items'][i]['type'] == 'limit':
                profits_left += 1
            delete_response = SendRequest('DELETE', '/api/v1/orders/'+str(response[1]['data']['items'][i]['id']),'')
    response = SendRequest('GET', '/api/v1/orders/'+orderID[0], '')
    if str(response[1]['data']['isActive']) == "True":
        response = SendRequest('DELETE', '/api/v1/orders/'+str(orderID[0]),'')
    for i in range(0,(len(trade_group[place])-3)-profits_left):
        trade_group[place][3+i] = str(int(trade_group[place][3+i]) + 1)
    response = SendRequest('DELETE','/api/v1/orders?symbol='+str(ticker)+'&tradeType=MARGIN_TRADE','')
    file = open('trades.csv', 'w')
    rd = csv.writer(file)
    row = []
    for i in range(0,len(trade_group)):
        for j in range(0,len(trade_group[i])):
            if j == len(trade_group[i]) and i != len(trade_group):
                row.append(trade_group[i][j]+'\n')
                break
            elif j == len(trade_group[i]) and i == len(trade_group):
                row.append(trade_group[i][j])
            row.append(trade_group[i][j])
        rd.writerow(row)
        row.clear()
    file.close()
    response = SendRequest('GET','/api/v1/margin/account', '')
    for i in range(0,len(response[1]['data']['accounts'])):
        if ticker  == str(response[1]["data"]['accounts'][i]['currency'])+"-USDT":
            if side == 'buy':
                amount_to_trade = float(response[1]['data']['accounts'][i]['liability'])
            if side == 'sell':
                amount_to_trade = float(response[1]['data']['accounts'][i]['availableBalance'])
    digits = get_increment(ticker)
    digits = len(str(digits)) - 2
    print("decimal places = ",digits)
    amount_to_trade = math.floor(amount_to_trade * 10 ** digits)/ 10 ** digits
    print(amount_to_trade)
    return amount_to_trade    
            
def get_increment(ticker):
    
    response = SendRequest('GET', '/api/v1/symbols', '')
    for i in range(0, len(response[1]['data'])):
        if ticker == response[1]['data'][i]['symbol']:
            increment = response[1]['data'][i]['baseIncrement']
            return increment

def get_ticker_price(ticker):

    response = (0,0)
    if ticker == "USDT-USDT":
        return 1
    while(response[0] != 200 or response[1]['code'] != '200000'):
        response = SendRequest('GET','/api/v1/market/orderbook/level1?symbol='+ticker,'')
    price = response[1]['data']['price']
    return price
        
def repay_loan(ticker, order_type):
    global in_trade
    
    if order_type == 'sell':
        currency = 'USDT'
    if order_type == 'buy':
        currency = ticker.replace('-USDT','')
    loan = grab_open_loans(currency)
    if loan[1] == 0:
        return
    
    data = {'currency':str(currency), 'tradeId':str(loan[0]),'size':str(loan[1])}
    response = SendRequest('POST', '/api/v1/margin/repay/single', json.dumps(data))
    for i in range(0, 2):
        if response[1]['code'] == "210001":
            data = {"clientOid":str(uuid.uuid4()),"side":'buy',"symbol":str(ticker), "type":"market",'funds':'2'}
            response = SendRequest('POST', '/api/v1/margin/order', json.dumps(data))
            sleep(5)
            data = {'currency':str(currency), 'tradeId':str(loan[0]),'size':str(loan[1])}
            response = SendRequest('POST', '/api/v1/margin/repay/single', json.dumps(data))
    if response[0] == 200 and response[1]['code'] == "200000":
        SendMessage(str(ticker)+" Loan Repaid")
    return 

def grab_open_loans(currency):
    
    response = SendRequest('GET','/api/v1/margin/borrow/outstanding','')
    for i in range(0, len(response[1]['data']['items'])):
        if response[1]['data']['items'][i]['currency'] == currency:
            loan_id = response[1]['data']['items'][i]['tradeId']
            size = response[1]['data']['items'][i]['liability']
            return loan_id, size
    return 0,0
        
def get_price_increment(ticker):
    
    response = SendRequest('GET', '/api/v1/symbols', '')
    for i in range(0, len(response[1]['data'])):
        if ticker == response[1]['data'][i]['symbol']:
            increment = response[1]['data'][i]['priceIncrement']
            print(increment)
            return increment
   
def SendRequest(prefix, path, data_json):
    
    now = int(time.time() * 1000)
    print(prefix + '  '+path+'   '+data_json)
    str_to_sign = str(now) + prefix + path + data_json
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
        }
    response = requests.request(prefix, url+path, headers=headers, data=data_json)
    response_json = json.loads(response.text)
    if '/api/v1/symbols' not in path and '/api/v1/market/orderbook' not in path and '/api/v1/margin/account' not in path:
        print(response.status_code)
        print(response.json())
    return(response.status_code,response_json)
        

def populate_trade_group():
    global trade_group

    print("In populate Trade Group")
    file = open('trades.csv', 'r')
    rd = csv.reader(file)
    rows = 0
    for row in rd:
        rows+=1
        cols = len(row)
    file.close()
    trade_group.clear()
    trade_group = [['0' for i in range(cols)] for j in range(rows)]
    file = open('trades.csv','r')
    rd = csv.reader(file)
    i = 0
    for row in rd:
        volume = get_ticker_volume(row[0])
        for j in range(0,len(row)):
            trade_group[i][j] = row[j]
        trade_group[i][1] = str(volume)
        i += 1
    file.close()
    print(trade_group,'\n')
    return

def get_ticker_volume(ticker):

    response = SendRequest('GET','/api/v1/market/stats?symbol='+ticker,'')
    volume = response[1]['data']['volValue']
    return volume

def create_loss_profit(ticker, order_type, price, order_amount, ticker_index, trade_id):
    global id_tracker, trade_group
    
    stop_loss_price = [0,0]
    take_profit_price = [0,0,0,0,0,0,0,0]
    id_array = []
    id_array.append(trade_id)
    stop_loss_amount = order_amount/2
    digits = get_increment(ticker)
    digits = len(str(digits)) - 2
    stop_loss_amount = math.floor(stop_loss_amount * 10 ** digits)/ 10 ** digits
    if order_type == 'buy':
        new_order_type = 'sell'
        stop_loss_type = 'loss'
        take_profit_type = 'entry'
        stop_loss_price[0] = price * (1-.015)
        stop_loss_price[1] = price * (1-.025)
        take_profit_price[0] = price * (1+.005)
        take_profit_price[1] = price * (1+.01)
        take_profit_price[2] = price * (1+.015)
        take_profit_price[3] = price * (1+.02)
        take_profit_price[4] = price * (1+.025)
        take_profit_price[5] = price * (1+.03)
        take_profit_price[6] = price * (1+.035)
        take_profit_price[7] = price * (1+.04)
    if order_type == 'sell':
        new_order_type = 'buy'
        stop_loss_type = 'entry'
        take_profit_type = 'loss'
        stop_loss_price[0] = price * (1+.015)
        stop_loss_price[1] = price * (1+.025)
        take_profit_price[0] = price * (1-.005)
        take_profit_price[1] = price * (1-.01)
        take_profit_price[2] = price * (1-.015)
        take_profit_price[3] = price * (1-.02)
        take_profit_price[4] = price * (1-.025)
        take_profit_price[5] = price * (1-.03)
        take_profit_price[6] = price * (1-.035)
        take_profit_price[7] = price * (1-.04)
    allocation = 0
    take_profit_amt = [0,0,0,0,0,0,0,0]
    for i in range(0, len(trade_group)):
        if trade_group[i][0] == ticker:
            for j in range(3, len(trade_group[i])):
                allocation += int(trade_group[i][j])
            for j in range(3,11):
                take_profit_amt[j-3] = (int(trade_group[i][j])/int(allocation)) * float(order_amount)
            break
    for i in range(0,len(take_profit_amt)):
        take_profit_amt[i] = math.floor(take_profit_amt[i] * 10 ** digits)/ 10 ** digits
    digits = get_price_increment(ticker)
    digits = len(str(digits)) - 2
    for i in range(0,len(stop_loss_price)):
        stop_loss_price[i] = math.floor(stop_loss_price[i] * 10 ** digits)/ 10 ** digits
    for i in range(0,len(take_profit_price)):
        take_profit_price[i] = math.floor(take_profit_price[i] * 10 ** digits)/ 10 ** digits
    print(take_profit_price, stop_loss_price)
    sleep(3)
    for i in range(0,len(stop_loss_price)):
        data = {"clientOid":str(uuid.uuid4()),"side":str(new_order_type),"symbol":str(ticker), "type":"market",'stop':str(stop_loss_type),'size':str(stop_loss_amount),"autoBorrow":True,"stopPrice":str(stop_loss_price[i]),"tradeType":"MARGIN_TRADE"}
        response = SendRequest('POST','/api/v1/stop-order', json.dumps(data))
        if response[1]['code'] == '200000':
            id_array.append(response[1]['data']['orderId'])
        else:
            id_array.append("XXXXXXXXXXXXX")
    for i in range(0,len(take_profit_price)):
        data = {"clientOid":str(uuid.uuid4()),"side":str(new_order_type),"symbol":str(ticker), "type":"limit",'size':str(take_profit_amt[i]),"autoBorrow":True,"price":str(take_profit_price[i]),"stopPrice":str(take_profit_price[i]),'stop':str(take_profit_type),'tradeType':'MARGIN_TRADE'}
        response = SendRequest('POST','/api/v1/stop-order', json.dumps(data))
        if response[1]['code'] == '200000':
            id_array.append(response[1]['data']['orderId'])
        else:
            id_array.append("XXXXXXXXXXXXX")
    file = open('trade_block.csv','a')
    id_tracker.append(id_array)
    return

    

        
def SendMessage(message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo
    server.starttls()
    server.ehlo()
    server.set_debuglevel(0)
    server.login('justforsms2000@gmail.com', 'Strikeout123')
    server.sendmail('justforsms2000@gmail.com','9727624417@vtext.com',message)
    server.close()
    return
app.run(host='0.0.0.0',port=6000)   

def get_ticker_volume(ticker):

    response = SendRequest('GET','/api/v1/market/stats?symbol='+ticker,'')
    volume = response[1]['data']['volValue']
    return volume
