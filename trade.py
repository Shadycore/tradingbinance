from library import trading
import time
successed = False
#trade = trading.trading_binance(tld='com', symbol='MAVUSDT', asset='MAV', quantity_usd=10.30, profit_margin=0, percentage_asset_sell=0)

trade = trading.trading_binance(tld='com', symbol='ALTUSDT', asset='ALT', 
                                quantity_usd=10.50, profit_margin=5, percentage_asset_sell=0,
                                buy_price=0.306)
buy_order, successed = trade.buy_order()
print ("****************************************************************")
print("buy_order info:","\n",buy_order, "\n", "successed: ", successed)
trade.finalizar()
time.sleep(1)
print ("================================================================")
if successed:
    sell_order, successed = trade.sell_order()
    print("sell_order info:","\n",sell_order, "\n", "successed: ", successed)
else:
    print("No se pudo realizar la orden de compra")
print ("****************************************************************")
trade.finalizar()
