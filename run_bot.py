from trader_bot import Bot

def main():
	bot = Bot()
	bot.set_paper_account('PKUBAPHQC8ZNCG5DUCK6', '6tIf9JZFqbPQEJQlcHxxEY2AJPoEvLuPkOFV1A0A')
	bot.watchlist_info()
	bot.run(9)
	#bot.run_bot(paper = True)
	bot.paper_gains()


if __name__ == '__main__':
	main()