#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 21:17:51 2022

@author: enigma
"""
import time
import json
import uuid
import base64
import hmac
import hashlib
import requests
import math
from time import sleep

api_key = ''
api_secret = ''
url = 'https://api.kucoin.com'
api_passphrase = ''
previous_ticker = []

def SendRequest(prefix, path, data_json):
    
    print(data_json)
    now = int(time.time() * 1000)
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
    if '/api/v1/symbols' not in path and '/api/v1/market/orderbook' not in path and '/api/v1/margin/account' not in path and '/api/v1/stop-order' not in path:
        print(response.status_code)
        print(response.json())
    return response.status_code, response_json

while True:
    sleep(150)
    print("Start")
    stop_id = []
    ticker_list = []
    
    response = SendRequest('GET','/api/v1/stop-order', '')
    for i in range(0, len(response[1]['data']['items'])):
        if response[1]['data']['items'][i]['symbol'] not in ticker_list:
            ticker_list.append(response[1]['data']['items'][i]['symbol'])
    print(ticker_list)
    stop_id = [[['0' for i in range(6)]for j in range(10)]for k in range(20)]
    print(len(response[1]['data']['items']))
    if len(ticker_list) >= 7:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!")
    for i in range(0, len(ticker_list)):
        number = 0
        for j in range(0, len(response[1]['data']['items'])):
            if response[1]['data']['items'][j]['symbol'] == ticker_list[i]:
                stop_id[i][number][0] = response[1]['data']['items'][j]['id']
                stop_id[i][number][1] = response[1]['data']['items'][j]['stop']
                stop_id[i][number][2] = response[1]['data']['items'][j]['stopPrice']
                stop_id[i][number][3] = response[1]['data']['items'][j]['type']
                stop_id[i][number][4] = response[1]['data']['items'][j]['side']
                stop_id[i][number][5] = response[1]['data']['items'][j]['size']
                number += 1
    for i in range(len(stop_id) -1,-1,-1):
        for j in range(len(stop_id[i])-1,-1,-1):
            if stop_id[i][j][0] == '0':
                stop_id[i].pop(j)
            else:
                break
                
    print(stop_id)
    for i in range(0,len(ticker_list)):
        loss_total = 0
        profit_total = 0
        market_counter = 0
        limit_counter = 0
        profit_positions = []
        loss_positions = []
        if ticker_list[i] not in previous_ticker:
            continue
        for j in range(0,len(stop_id[i])):
            if stop_id[i][j][3] == 'market':
                loss_total += float(stop_id[i][j][5])
                market_counter += 1
                loss_positions.append(j)
            if stop_id[i][j][3] == 'limit':
                profit_total += float(stop_id[i][j][5])
                limit_counter += 1
                profit_positions.append(j)
        disparity = (loss_total - profit_total) / ((loss_total + profit_total)/2)
        print(disparity)
        if market_counter == 0:
            for j in range(0,len(stop_id[i])):
                response = SendRequest('DELETE', '/api/v1/orders/'+stop_id[i][profit_positions[j]][0], '')
            continue
        if limit_counter == 0:
            for j in range(0, len(stop_id[i])):
                response = SendRequest('DELETE', '/api/v1/orders/'+stop_id[i][loss_positions[j]][0], '')
            continue
        if disparity < -.1:
            take_profits_left = limit_counter
            for k in range(0, take_profits_left):
                new_size = float(stop_id[i][profit_positions[k]][5]) / 2
                response = SendRequest('GET', '/api/v1/symbols', '')
                for l in range(0, len(response[1]['data'])):
                    if ticker_list[i] == response[1]['data'][l]['symbol']:
                        increment = response[1]['data'][l]['baseIncrement']
                        price_increment = response[1]['data'][l]['priceIncrement']
                        break
                digits = len(str(increment)) - 2
                price_digits = len(str(price_increment)) - 2 
                price = float(stop_id[i][profit_positions[k]][2])
                price = math.floor(price * 10 ** price_digits)/ 10 ** price_digits
                new_size = math.floor(new_size * 10 ** digits)/ 10 ** digits
                response = SendRequest('DELETE', '/api/v1/orders/'+stop_id[i][profit_positions[k]][0], '')
                data = {"clientOid":str(uuid.uuid4()),"side":str(stop_id[i][profit_positions[k]][4]),"symbol":str(ticker_list[i]), "type":"limit",'size':str(new_size),"autoBorrow":True,"price":str(price),"stopPrice":str(price),'stop':str(stop_id[i][profit_positions[k]][1]),'tradeType':'MARGIN_TRADE'}
                response = SendRequest('POST', '/api/v1/stop-order',json.dumps(data))
                if response[0] == 200:
                    data = {'order':'Change-Order','old-order':str(stop_id[i][profit_positions[k]][0]),'new-order':str(response[1]['data']['orderId']),'position':'0.00','ticker':str(ticker_list[i]),'price':str(price),'old-size':str(stop_id[i][profit_positions[k]][5]),'new-size':str(new_size),'action':'stop loss triggered'}
                    response = requests.post("http://10.100.1.10:6000", data=json.dumps(data))
                    print(json.dumps(data))
                    print(response.text)
            continue
        if disparity > .005:
            new_stop_loss = profit_total / market_counter 
            response = SendRequest('GET', '/api/v1/symbols', '')
            for j in range(0, len(response[1]['data'])):
                if ticker_list[i] == response[1]['data'][j]['symbol']:
                    increment = response[1]['data'][j]['baseIncrement']
                    price_increment = response[1]['data'][j]['priceIncrement']
                    break
            price_digits = len(str(increment)) - 2
            digits = len(str(increment)) - 2
            new_stop_loss = math.floor(new_stop_loss * 10 ** digits)/ 10 ** digits
            for j in range(0, market_counter):
                price = float(stop_id[i][loss_positions[j]][2])
                price = math.floor(price * 10 ** price_digits)/ 10 ** price_digits
                response = SendRequest('DELETE', '/api/v1/orders/'+stop_id[i][loss_positions[j]][0], '')
                data = {"clientOid":str(uuid.uuid4()),"side":str(stop_id[i][loss_positions[j]][4]),"symbol":str(ticker_list[i]), "type":"market",'size':str(new_stop_loss),"autoBorrow":True,'stopPrice':str(price),'stop':str(stop_id[i][loss_positions[j]][1]),'tradeType':'MARGIN_TRADE'}
                response = SendRequest('POST', '/api/v1/stop-order',json.dumps(data))
                if response[0] == 200:
                    data = {'order':'Change-Order','old-order':str(stop_id[i][loss_positions[j]][0]),'new-order':str(response[1]['data']['orderId']),'position':'0.00','ticker':str(ticker_list[i]),'price':str(price),'old-size':str(stop_id[i][loss_positions[j]][5]),'new-size':str(new_stop_loss),'action':'take profit triggered'}
                    response = requests.post('http://10.100.1.10:6000', data = json.dumps(data))
                    print(json.dumps(data))
                    print(response.text)
            continue
    previous_ticker = ticker_list 

       
    

            
                        
                      
                                
