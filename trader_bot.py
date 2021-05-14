from yahoo_fin import stock_info as sf
from webull import webull
import alpaca_trade_api as tradeapi
import random
import pandas as pd
import numpy as np
import math
import time


class Bot():

	watchlist = []
	paper_account = None
	wb = None
	#wb = webull()
	#wb.login('', 'pa$$w0rd')
	#sf.get_market_status()


	def __init__(self):
		self.watchlist = []
		self.paper_account = None
		self.wb = None
		self.load_watchlist()

	def paper_gains(self):
		acc = self.paper_account.get_account()
		e = 100000
		e1 = float(acc.equity)
		print('Current Equity: {}'.format(e1))
		print('Gains $: {}'.format(round(e1 - e, 2)))
		print('Gains %: {}'.format(round((e1 / e) * 100 - 100, 2)))
		print('\n')

	def set_paper_account(self, key_id, secret_key):
		self.paper_account = tradeapi.REST(key_id, secret_key, 'https://paper-api.alpaca.markets')

	def paper_trade(self, ticker, quantity, buysell, buytype, tif):
		self.paper_account.submit_order(
		    symbol = ticker,
		    qty = quantity,
		    side = buysell,
		    type = buytype,
		    time_in_force = tif
		)

	def paper_algo_trade(self, ticker, buysell, budget = 1000):
		price = sf.get_live_price(ticker)

		if buysell == 'buy':
			holdings = int(self.paper_account.get_position(ticker).qty)
			value = holdings * sf.get_live_price(ticker)
			if value <= 6000:
				bp = float(self.paper_account.get_account().buying_power)
				bp -= price * 10
				budget -= price * 10
				bought = 0 
				while bp >= price*10 and budget >= price*10:
					bp -= price * 10
					budget -= price * 10
					self.paper_trade(ticker, 10, 'buy', 'market', 'gtc')
					bought += 10
				print('Bought: {} * {}'.format(ticker, bought))
			else:
				print('Bought: {} * {}'.format(ticker, 0))


		elif buysell == 'sell':
			sold = 0
			for i in range(5):
				try:
					if int(self.paper_account.get_position(ticker).qty) >= 10:
						self.paper_trade(ticker, 10, 'sell', 'market', 'gtc')
						sold += 10
						print(1)
				except Exception as e:
					break
			print('Sold: {} * {}'.format(ticker, sold))


	def set_webull_account(self, usr, passwrd):
		self.wb = webull()

	def account_info(self):
		account = self.paper_account.get_account()
		print(account)

	def print_portfolio(self):
		portfolio = self.paper_account.list_positions()
		print(portfolio)

	def run(self, runtime):
		runtime5 = runtime * 12
		while runtime5 > 0:
			runtime5 -= 1
			if self.paper_account.get_clock().is_open:
				self.run_bot(paper = True)
			else:
				print('Market Closed')
			time.sleep(300)


	def run_bot(self, paper = False, webull = False):
		for s in self.watchlist:
			rsi = self.get_rsi(s)
			if rsi >= 70:
				if paper:
					self.paper_algo_trade(s, 'sell')
			elif rsi <= 30:
				if paper:
					self.paper_algo_trade(s, 'buy')
			else:
				pass
				# print('Held: {}'.format(s))
		print('\n')

	def add_stock(self, *stock_ticker):
		for s in stock_ticker:
			self.watchlist.append(s)
		self.save_watchlist()

	def save_watchlist(self):
		f = open('watchlist.txt', "w")
		for w in self.watchlist:
			f.write(w + "\n")

	def load_watchlist(self):
		with open('watchlist.txt') as f:
			lines = f.read().splitlines()
			self.watchlist = lines

	def watchlist_info(self):
		print('\n\nStock Watchlist Info')
		print('--------------------------')
		for i in self.watchlist:
			holdings = 0
			price = round(sf.get_live_price(i), 2)
			try:
				holdings = int(self.paper_account.get_position(i).qty)
			except Exception:
				holdings = 0
			print("{}:\tRSI: {}\tHoldings: {}\t\tPrice: ${}".format(i, self.get_rsi(i), holdings, price))
		print('\n')

	def get_rsi(self, ticker):
		data = sf.get_data(ticker)
		delta = data['adjclose'].diff()

		dUp, dDown = delta.copy(), delta.copy()
		dUp[dUp < 0] = 0
		dDown[dDown > 0] = 0
		RolUp = pd.Series(dUp).rolling(window=14).mean()
		RolDown = pd.Series(dDown).rolling(window=14).mean().abs()

		RS = RolUp / RolDown
		rsi = 100.0 - (100.0 / (1.0 + RS))
		return round(rsi.iloc[-1], 3)

	def get_rsi1(self, stock_ticker):

		df = sf.get_data(stock_ticker)
		df = df[::-1][:14]['close']
		df = df.reset_index()
		df = df.drop(columns = ['index'])
		pd.concat([pd.Series([sf.get_live_price(stock_ticker)]), df])
		df = df['close'].tolist()
		#print(df)

		total_gain = 0
		total_loss = 0

		for i in range(1, 14):
			change = df[i] - df[i - 1]
			if change >= 0:
				total_gain += change
			else:
				total_loss += abs(change)

		avg_gain = total_gain / 14
		avg_loss = total_loss / 14

		rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))

		return round(rsi, 3)


