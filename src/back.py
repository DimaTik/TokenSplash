# from pprint import pprint
import pprint
import random as rd
import time
from pybit.unified_trading import HTTP
from pybit import exceptions
from collections import namedtuple


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
		# self.order_volume =
		self.total_volume = 0
		self.total_waste = 0
		self.PERCENT_OF_PROFIT = 0.003
		self.PERCENT_OF_LOSS = 0.002
		self.PRICE_DEVIATION = 0.001
		self.LIMIT_OF_LOSS = 3
		self.DELAY_CLOSE = 2

	def __make_order(self):
		while True:
			try:
				price = self.__get_price_of_token()
				price_precision = len(str(price).split('.')[-1])
				base_precision = self.__get_base_precision()
				# price = round(price * (1 - self.PRICE_DEVIATION), price_precision)
				take_profit = str(round(price * (1 + self.PERCENT_OF_PROFIT), price_precision))
				stop_loss = str(round(price * (1 - self.PERCENT_OF_LOSS), price_precision))
				# tpLimitPrice = str(round(float(take_profit) * (1 - self.PRICE_DEVIATION), price_precision))
				# slLimitPrice = str(round(float(stop_loss) * (1 + self.PRICE_DEVIATION), price_precision))
				# print(take_profit, tpLimitPrice, stop_loss, slLimitPrice)
				# print(take_profit, stop_loss)
				volume = rd.randint(int(self.order_volume * (1 - 0.1)), int(self.order_volume * (1 + 0.1)))
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

					takeProfit=take_profit,
					stopLoss=stop_loss,
					tpLimitPrice=take_profit,
					slLimitPrice=stop_loss,
					tpslMode="Full",
					tpOrderType="Limit",
					slOrderType="Limit",
				)
			# print(req)
			except exceptions.InvalidRequestError as e:
				if e.message == 'Not supported symbols':
					print('Указан несуществующий токен')
					self.token = input('Введите новый тикер ').upper() + 'USDT'
				elif e.message == 'Insufficient balance.':
					print('У вас недостаточно средств')
					self.order_volume = Checker.check_int_input('Введите новый объем одного ордера ')
			else:
				# print('make_order')
				# print(req)
				Order = namedtuple('Order', ['price', 'volume', 'qty', 'order_id'])
				return Order(price, volume, qty, req['result']['orderId'])

	def __sell(self, order_qty):
		self.session.place_order(
			category="spot",
			symbol=self.token,
			side="Sell",
			orderType="Market",
			orderFilter="Order",
			marketUnit="baseCoin",
			qty=order_qty
		)

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
			if not order:
				break
			else:
				order_status = order[0]['orderStatus']
				# pprint.pprint(order)
				if order_status == 'New':
					start_time = time.time_ns()
					# print(start_time)
					while True:
						if (time.time_ns() - start_time) // 1000 >= self.DELAY_CLOSE:
							# order = self.session.get_open_orders(category='spot', symbol=self.token)
							self.__cancel_pending_order(order[0]['orderId'])
							try:
								self.__sell(order[0]['qty'])
							except exceptions.InvalidRequestError:
								break
							else:
								print('AUTO-CLOSE')
								break
				elif order_status == 'Untriggered':
					# print('Wait')
					time.sleep(0.5)

	def __check_status_order(self):
		order = self.session.get_open_orders(category='spot', symbol=self.token)
		if order['result']['list']:
			return order['result']['list'][0]['orderStatus']
		else:
			return None

	def __cancel_pending_order(self, order_id):
		try:
			self.session.cancel_order(category='spot', orderId=order_id)
		except exceptions.InvalidRequestError:
			pass

	def info_of_last_order(self, side):
		while True:
			data = self.session.get_order_history(
				category='spot',
				symbol=self.token,
				limit=1,
			)['result']['list'][0]
			if data['side'] == side:
				break
			else:
				time.sleep(0.5)
		# pprint.pprint(data)
		order = namedtuple('order', ['volume_in_base', 'volume_in_token', 'price', 'fee'])
		return order(float(data['cumExecValue']), float(data['cumExecQty']),
		             float(data['avgPrice']), float(data['cumExecFee']))

	def work(self):
		cnt_loss = 0
		while True:
			order = self.__make_order()
			time.sleep(1)
			status = self.__check_status_order()
			if status == 'New':
				self.__cancel_pending_order(order.order_id)
			else:
				buy_order = self.info_of_last_order('Buy')
				# print(buy_order)
				self.__wait_close_position()
				sell_order = self.info_of_last_order('Sell')
				# print(sell_order)
				self.total_volume += buy_order.volume_in_base + sell_order.volume_in_base
				self.total_waste += buy_order.fee*order.price + sell_order.fee - \
				                    (sell_order.price - buy_order.price) * sell_order.volume_in_token

				print(f'Цена покупки: {buy_order.price} Цена продажи: {sell_order.price} Количество монет: {order.qty} '
				      f'Убыток: {self.total_waste:.2f} Общий наработанный объем за сессию: {self.total_volume:.2f} ',
				      end='')
				if buy_order.price > sell_order.price:
					print('Сделка: убыточная')
					cnt_loss += 1
				else:
					print('Сделка: прибыльная')
					cnt_loss = 0

				print('OK')

				time.sleep(rd.randint(0, 20))

			if cnt_loss == self.LIMIT_OF_LOSS:
				print('AUTO-STOP')
				break


class Checker:
	@staticmethod
	def check_int_input(message):
		while True:
			arg = input(message)
			if not arg.isnumeric():
				print('Значок, что ты дурачок, введи цифру')
			else:
				return int(arg)

	@staticmethod
	def enter_keys():
		public_key = input('Вы не ввели api ключ или ввели неверный. Введите другой public key: ')
		secret_key = input('Secret key: ')
		return public_key, secret_key
