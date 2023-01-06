from bot.order_bot import OrderBot

#!!
o_bot = OrderBot(demo=False)

o_bot.limit_order("JUN3.DE", quantity=4, limit_price=25.637)
#o_bot.limit_order("TMV.DE", 12.42, 12.069)
#o_bot.sell_limit("TMV.DE", 12.42, 12.438)