from trader_bot import Bot

def main():
	bot = Bot()
	bot.watchlist_info()
	bot.run(12)
	bot.paper_gains()


if __name__ == '__main__':
	main()