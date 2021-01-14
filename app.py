import json, config
from flask import Flask, request, jsonify, render_template
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def get_symbol_name(symbol):
    try:
        if symbol.endswith('PERP'):
            return symbol.rstrip('PERP')
        return symbol
    except:
        return ''

def order(side, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        # set the percentage or fraction you want to invest in each order

        if side == 'BUY':
            balance= client.get_asset_balance(asset='USDT')
            portion_balance = float(balance['free']) * 0.2
        
        elif side == 'SELL':
            balance = client.get_asset_balance(asset=symbol)
            portion_balance = float(balance['free'])

        print(f"sending order {order_type} - {side} {portion_balance} {symbol}")
        order = client.futures_create_order(symbol=symbol, side=side, type=order_type, quantity=portion_balance)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return order

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    #print(request.data)
    data = json.loads(request.data)
    
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    side = data['strategy']['order_action'].upper()
    symbol = get_symbol_name(data['ticker'])

    order_response = order(side, symbol ,order_type)

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")

        return {
            "code": "error",
            "message": "order failed"
        }