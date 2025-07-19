import back
from src import config
from enum import Enum


def enter_keys():
	public_key = input('Вы не ввели api ключ или ввели неверный. Введите другой public key: ')
	secret_key = input('Secret key: ')
	return public_key, secret_key


def main():
	Modes = Enum('Modes', [('SPOT', False), ('DEMO', True)])
	Lengths = Enum('Lengths', [('PUBLIC_LEN', 18), ('SECRET_LEN', 36)])

	input('''Привет, перед началом использования бота заполни пожалуйста файл config,
ключи api для demo-режима необязательны, если не хочешь использовать его.
Если всё готово, нажми Enter.''')

	mode = bool(back.Checker.check_int_input('Выберите режим торговли spot(0)/demo(1), напишите цифру. '))
	while True:
		if mode == Modes['SPOT'].value:
			if len(config.api_public) == Lengths['PUBLIC_LEN'].value\
					and len(config.api_secret) == Lengths['SECRET_LEN'].value:
				api_public, api_secret = config.api_public, config.api_secret
				break
			else:
				config.api_public, config.api_secret = enter_keys()
		elif mode == Modes['DEMO'].value:
			if len(config.demo_api_public) == Lengths['PUBLIC_LEN'].value\
					and len(config.demo_api_secret) == Lengths['SECRET_LEN'].value:
				api_public, api_secret = config.demo_api_public, config.demo_api_secret
				break
			else:
				config.demo_api_public, config.demo_api_secret = enter_keys()

	token = input('Введите тикер ').upper() + 'USDT'
	order_volume = back.Checker.check_int_input('Объем одного ордера в $ ')
	print(token, order_volume, mode)

	trader = back.Trade(api_public, api_secret, token, order_volume, mode)
	trader.work()


if __name__ == '__main__':
	main()
