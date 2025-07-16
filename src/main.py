import back
import config


def check_int_input(message):
	while True:
		arg = input(message)
		if not arg.isnumeric():
			print('Значок, что ты дурачок, введи цифру')
		else:
			return int(arg)


def main():
	input('''Привет, перед началом использования бота заполни пожалуйста файл config,
ключи api для demo-режима необязательны, если не хочешь использовать его.
Если всё готово, нажми Enter.''')
	mode = check_int_input('Выберите режим торговли spot(1)/demo(2), напиши цифру. ')
	while True:
		if mode == 1:
			if len(config.API_public) == 18 and len(config.API_secret) == 36:
				api_public = config.API_public
				api_secret = config.API_secret
				break
			else:
				input('Вы не ввели api ключ или ввели неверный. Введите другой.')
		else:
			if len(config.demo_API_public) == 18 and len(config.demo_API_secret) == 36:
				api_public = config.demo_API_public
				api_secret = config.demo_API_secret
				break
			else:
				input('Вы не ввели api ключ или ввели неверный. Введите другой.')

	token = input('Введите тикер ').upper() + 'USDT'
	order_volume = check_int_input('Объем одного ордера в $ ')

	trader = back.Trade(api_public, api_secret, token, order_volume)


if __name__ == '__main__':
	main()
