import random as rd
import time
from pybit.unified_trading import HTTP
from pybit import exceptions


class Trade:
	def __init__(self, api_public, api_secret, token, order_volume, mode):
		self.api_public = api_public
		self.api_secret = api_secret
		self.token = token
		self.order_volume = order_volume
		self.session = HTTP(
			api_key=self.api_public,
			api_secret=self.api_secret,
			demo=mode)
		self.total_volume = 0
		self.PERCENT_OF_PROFIT = 0.005
		self.PERCENT_OF_LOSS = 0.002
		self.PRICE_DEVIATION = 0.0001

	def __make_order(self):
		while True:
			try:
				price = self.__get_price_of_token()
				price_precision = len(str(price).split('.')[-1])
				base_precision = self.__get_base_precision()
				price = round(price * (1 - self.PRICE_DEVIATION), price_precision)
				take_profit = str(round(price * (1+self.PERCENT_OF_PROFIT), price_precision))
				stop_loss = str(round(price * (1-self.PERCENT_OF_LOSS), price_precision))
				volume = rd.randint(int(self.order_volume*(1-0.1)), int(self.order_volume*(1+0.1)))
				qty = round(volume / price, base_precision)
				req = self.session.place_order(
					category="spot",
					symbol=self.token,
					side="Buy",
					orderType="Limit",
					price=price,
					marketUnit="baseCoin",
					qty=qty,
					isLeverage=0,
					orderFilter="Order",
					positionIdx=0,
					tpslMode='Partial',
					tpOrderType='Limit',
					slOrderType='Limit',
					tpLimitPrice=take_profit,
					slLimitPrice=stop_loss)
				print('make_order')
				print(req)
				return volume, req['result']['orderId']
			except exceptions.InvalidRequestError:
				print('Вы ввели несуществующий тикер')
				self.token = input('Введите новый ').upper() + 'USDT'

	def __get_base_precision(self):
		return len(str(self.session.get_instruments_info(
			category='spot',
			symbol=self.token
		)['result']['list'][0]['lotSizeFilter']['basePrecision']).split('.')[-1])

	def __get_price_of_token(self):
		return float(self.session.get_tickers(
			category="spot",
			symbol=self.token,
		)['result']['list'][0]['lastPrice'])

	def __wait_close_position(self):
		while True:
			order = self.session.get_open_orders(category='spot', symbol=self.token)['result']['list']
			print(order)
			if not order:
				break
			else:
				print('Жду')
				time.sleep(3)

	def __check_status_order(self):
		print('check_status_order')
		print(self.session.get_open_orders(category='spot', symbol=self.token))
		order = self.session.get_open_orders(category='spot', symbol=self.token)
		if order['result']['list']:
			return order['result']['list'][0]['orderStatus']
		else:
			return None

	def __cancel_pending_order(self, order_id):
		print('cancel_pending_order')
		print(self.session.cancel_order(category='spot', orderId=order_id))

	def work(self):
		while True:
			volume, order_id = self.__make_order()
			print(order_id)
			time.sleep(10)
			status = self.__check_status_order()
			if status == 'New':
				self.__cancel_pending_order(order_id)
				print('DELETE')
			elif status is None:
				continue
			else:
				self.__wait_close_position()
				print('OK')
			time.sleep(rd.randint(10, 30))
