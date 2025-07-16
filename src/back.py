import time
from pybit.unified_trading import HTTP


class Trade:
	def __init__(self, api_public, api_secret, token, order_volume):
		self.api_public = api_public
		self.api_secret = api_secret
		self.token = token
		self.order_volume = order_volume
		self.session = HTTP(
			api_key=self.api_public,
			api_secret=self.api_secret,
			demo=True
		)

	def make_order(self):
		orderID = self.session.place_order(
			category="linear",
			symbol=self.token,
			side="Buy",
			orderType="Market",
			qty="0.1",
			timeInForce="PostOnly",
			isLeverage=0,
			orderFilter="Order",
			positionIdx=0
		)['result']['orderId']
		return orderID

	def close_order(self, orderId):
		self.session.place_order(
			category="linear",
			symbol=self.token,
			side="Sell",
			orderType="Market",
			qty="0.1",
			timeInForce="PostOnly",
			isLeverage=0,
			orderFilter="Order",
			positionIdx=0
		)

