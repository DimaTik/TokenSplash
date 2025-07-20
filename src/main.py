import back
from enum import Enum
import configparser


def main():
	Modes = Enum('Modes', [('SPOT', False), ('DEMO', True)])
	Lengths = Enum('Lengths', [('PUBLIC_LEN', 18), ('SECRET_LEN', 36)])

	input('''Привет, перед началом использования бота заполните пожалуйста файл config,
ключи api для demo-режима необязательны, если не хочешь использовать его.
Если всё готово, нажми Enter.''')

	config = configparser.ConfigParser()
	while True:
		config_arr = config.read('config.ini')
		if not config_arr:
			input('Файл config не найден')
		else:
			break

	mode = bool(back.Checker.check_int_input('Выберите режим торговли spot(0)/demo(1), напишите цифру. '))
	while True:
		if mode == Modes['SPOT'].value:
			if len(config['API']['api_public']) == Lengths['PUBLIC_LEN'].value\
					and len(config['API']['api_secret']) == Lengths['SECRET_LEN'].value:
				api_public, api_secret = config['API']['api_public'], config['API']['api_secret']
				break
			else:
				config['API']['api_public'], config['API']['api_secret'] = back.Checker.enter_keys()
		elif mode == Modes['DEMO'].value:
			if len(config['API']['demo_api_public']) == Lengths['PUBLIC_LEN'].value\
					and len(config['API']['demo_api_secret']) == Lengths['SECRET_LEN'].value:
				api_public, api_secret = config['API']['demo_api_public'], config['API']['demo_api_secret']
				break
			else:
				config['API']['demo_api_public'], config['API']['demo_api_secret'] = back.Checker.enter_keys()

	token = input('Введите тикер ').upper() + 'USDT'
	order_volume = back.Checker.check_int_input('Объем одного ордера в $ ')
	print(token, order_volume, mode)

	trader = back.Trade(api_public, api_secret, token, order_volume, mode)
	trader.work()


if __name__ == '__main__':
	main()
