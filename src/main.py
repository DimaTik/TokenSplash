import back
import config
from enum import Enum


def check_int_input(message):
	while True:
		arg = input(message)
		if not arg.isnumeric():
			print('Значок, что ты дурачок, введи цифру')
		else:
			return int(arg)


def enter_keys():
	public_key = input('Вы не ввели api ключ или ввели неверный. Введите другой public key: ')
	secret_key = input('Secret key: ')
	return public_key, secret_key


def main():
	Modes = Enum('Modes', [('SPOT', 1), ('DEMO', 2)])
	Lenghts = Enum('Lenghts', [('PUBLIC_LEN', 18), ('SECRET_LEN', 36)])

	input('''Привет, перед началом использования бота заполни пожалуйста файл config,
ключи api для demo-режима необязательны, если не хочешь использовать его.
Если всё готово, нажми Enter.''')

	mode = check_int_input('Выберите режим торговли spot(1)/demo(2), напишите цифру. ')
	while True:
		if mode == Modes['SPOT'].value:
			if len(config.api_public) == Lenghts['PUBLIC_LEN'].value\
					and len(config.api_secret) == Lenghts['SECRET_LEN'].value:
				break
			else:
				config.API_public, config.API_secret = enter_keys()
		elif mode == Modes['DEMO'].value:
			if len(config.demo_api_public) == Lenghts['PUBLIC_LEN'].value\
					and len(config.demo_api_secret) == Lenghts['SECRET_LEN'].value:
				break
			else:
				config.demo_API_public, config.demo_API_secret = enter_keys()

	token = input('Введите тикер ').upper() + 'USDT'
	order_volume = check_int_input('Объем одного ордера в $ ')

	trader = back.Trade(config.api_public, config.api_secret, token, order_volume)


if __name__ == '__main__':
	main()
