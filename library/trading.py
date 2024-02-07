import json
from binance.client import Client
import time
import os

class trading_binance:
    def __init__(self, 
                tld='com',
                symbol='BTCUSDT',
                asset='BTC',
                quantity_usd=0, 
                profit_margin=0,
                percentage_asset_sell=0,
                buy_price=0):
        # tomar datos de api_config.json
        #Leer archivo api_config.json
        file = os.path.join(os.path.dirname(__file__), 'api_config.json')
        with open(file,'r') as api_config:
            data = json.load(api_config)

        self.api_key = data['api_key']
        self.api_secret = data['api_secret']
        self.base_url = data['base_url']

        self.client = Client(self.api_key, self.api_secret, tld=tld)
        self.symbol = symbol
        self.asset = asset        
        self.percentage_asset_sell = percentage_asset_sell # porcentaje de venta de la cripto
        self.profit_margin = profit_margin #% de ganancia en venta

        self.buy_price = buy_price # precio de compra, inicialmente en 0
        self.sell_price = 0 #precio de venta, inicialmente en 0
        self.sell_limit = 0 #límite precio de venta
        self.quantity_usd = quantity_usd
        self.quantity_asset = 0
        self.current_price = 0
        self.quantity_asset_sell = 0
        


    #obtiene precio actual del asset
    def get_price(self):
        # Realizar una petición de ejemplo a la API
        ticker = self.client.get_ticker(symbol=self.symbol)
        self.current_price = float(ticker['lastPrice'])
        return self.current_price
    
    #obtiene la cantidad de cripto que tengo
    def get_quantity_cripto(self):
        balance = self.client.get_asset_balance(asset=self.asset)
        self.quantity_asset = float(balance['free'])
        return self.quantity_asset
    
    def get_values(self):
        quantity_asset_sell =0
        sell_limit = 0

        if self.percentage_asset_sell > 0:
            quantity_asset_sell = self.quantity_asset * (self.percentage_asset_sell/100)
        else: 
            quantity_asset_sell = self.quantity_asset
        
        if self.profit_margin > 0:
            sell_limit = self.buy_price * (1 + self.profit_margin/100)
        else:   
            sell_limit = self.buy_price
        
        return quantity_asset_sell, sell_limit 

    #orden compra
    def buy_order(self):
        successed = True
        if self.buy_price > 0:
            ticker = self.client.get_ticker(symbol=self.symbol)
            self.current_price = float(ticker['lastPrice'])
            while self.current_price > self.buy_price:
                time.sleep(1)
                ticker = self.client.get_ticker(symbol=self.symbol)
                self.current_price = round(float(ticker['lastPrice']),3)
        try:
            order = self.client.order_market_buy(
                symbol=self.symbol,
                quoteOrderQty=self.quantity_usd
                )
            
            self.quantity_asset = float(order['fills'][0]['qty'])
            self.buy_price = float(order['fills'][0]['price']
                                )
            if self.percentage_asset_sell > 0:
                self.quantity_asset_sell = self.quantity_asset * (self.percentage_asset_sell/100)
            else: 
                self.quantity_asset_sell = self.quantity_asset
            
            if self.profit_margin > 0:
                self.sell_limit = self.buy_price * (1 + self.profit_margin/100)
            else:   
                self.sell_limit = self.buy_price

        except Exception as e:
            self.quantity_asset = 0
            self.buy_price = 0
            self.quantity_asset_sell = 0 
            self.sell_limit = 0

            successed = False
        return order, successed
    
    #orden de venta
    def sell_order(self):
        #Calcula el porcentaje de venta
        if self.sell_limit > 0:
            ticker = self.client.get_ticker(symbol=self.symbol)
            self.current_price = float(ticker['lastPrice'])
            while self.sell_limit > self.current_price:
                time.sleep(1)
                ticker = self.client.get_ticker(symbol=self.symbol)
                self.current_price = float(ticker['lastPrice'])
        
        if self.quantity_asset == 0 and self.buy_price == 0 and self.quantity_asset_sell == 0:
            self.quantity_asset = self.get_quantity_cripto()
            self.buy_price = self.get_price()
        
        successed = True
        try:
            if self.quantity_asset > 0:
                order = self.client.order_market_sell(
                    symbol=self.symbol,
                    quantity=self.quantity_asset
                    )
                self.sell_price = float(order['fills'][0]['price'])

        except Exception as e:
            successed = False
            self.sell_price = 0
        return order, successed
    
    def finalizar(self):
        print ("*****  Pair: ",self.symbol, "*****")
        print ("Asset: ", self.asset)        
        print("percentage_asset_sell",self.percentage_asset_sell)
        print("profit_margin", self.profit_margin) 
        print("quantity_usd",self.quantity_usd) 
        print("quantity_asset", self.quantity_asset)
        print("current_price",self.current_price) 
        print("quantity_asset_sell",self.quantity_asset_sell)
        print("La compra se realizó a un precio de: ", self.buy_price)
        print("Limite establecido para la venta",self.sell_limit)
        print("La venta se realizó a un precio de: ", self.sell_price)
        print("La ganancia obtenida fue de: ", self.sell_limit - self.buy_price)
