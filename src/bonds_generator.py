import os, sys
import random
import string

from faker import Faker
from faker.providers import BaseProvider

fake = Faker()


month_mapper = month_to_abbr = dict(january="jan", february="feb", march="mar", april="apr", may="may", june="jun",
     july="jul", august="aug", september="sept", october="oct", november="nov", december="dec")
abbr_to_month = {v:k for k,v in month_to_abbr.items()}
month_mapper.update(abbr_to_month)
MONTH_MAPPER = month_mapper



class BondsProvider(BaseProvider):
	def ticker(self):
		# this returns ALL tickers at once rather than 1 by 1
		# ticker = random.choice(["AAPL", 'HD', 'MOZAM', 'EUR'])
		letters = " ".join(string.ascii_letters).split()
		num_letters = random.choice([1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5])
		ticker = ''.join(random.sample(letters, num_letters))
		if len(ticker) < 3:
			return ticker.upper()
		return ticker.upper() if random.random() >= 0.5 else ticker.lower()


	def coupon(self, precision=None):
		"""
		:return: randomly selected decimal with precision 1-4
		  possibly succeeded by % symbol or preceded by '@' symbol
		"""
		coupon_num = random.random()
		if not precision:
			precision = random.choice([1, 2, 3, 4])
		include_percent = random.choice(["", "%"])
		include_at = random.choice(["", "@ "])
		coupon_value = round(coupon_num, precision)
		coupon = "{}{}{}".format(
			include_at, coupon_value, include_percent
		)
		return coupon

	#TODO currency other than $ and USD   --> fake.currency --> tuple: ('EUR', Euro') ('TRY', 'Turkish Lira')
	def price(self, precision=2):
		"""include $ or USD"""
		digits = int("{}{}".format(random.randrange(1,9), random.randrange(1,9)))
		price = random.choice([round(random.random() + 100, precision), digits])
		return random.choice(['{}'.format(price), '${}'.format(price), '{} USD'.format(price)])


	def size_unit(self):
		return random.choice(['k', 'm', 'mm', 'M', ''])

	def size(self):
		"""
		include ["k", "m", "mm"] and whether it should be .upper() or .lower()
		include commas? 1,900 1.9mm --> 1,900,000
		:return: numeric string consisting of an integer or float, with or without commas
			and with or without size unit
			## 4M of APPL 29s # 1,900 right? yes 1.9mm.
		"""
		unit = self.size_unit()
		if unit == 'k':
			value = random.randrange(100, 5000, 100)
			# comma
		else:
			value = random.randrange(0, 10)     # include higher numbers for mill
			if random.random() >= 0.5:
				decimal = random.choice([0.5, 0.5, 0.5, 0.5, 0.25, 0.75])
				value += decimal
		return value


	def maturity(self):
		date = fake.date_time_between('now', 2030).date()
		month = date.month if random.random() >= 0.75 else ''
		# day = date.day if random.random() >= 0.75 and month else ''
		year = str(date.year)
		year = year[-2:] if random.random() >= 0.75 else year
		if not month:
			return year

		# IF INCLUDING MONTH (NO DAY)
		month = self.month_fmt()
		if month.isdigit():
				date = month_digit_year = "{}{}{}".format(month, random.choice(["/",""]), year)   # 03/22
		else:
			date = ["{}{}{}".format(month, random.choice([" ", ""]), year)]
			#TODO add day -- note this includes possibility of including a comma if there is a space btw day and year
		return date


	def month_fmt(self):
			month = random.choice([fake.month(), fake.month_name()])
			month = month.lower() if random.random() >= 0.5 else month
			if not month.isdigit():
				mapped_month = MONTH_MAPPER[month.lower()]
				month = random.choice([month, mapped_month])
			if month.isdigit() and month[0]=='0':
				month = random.choice([month, month[-1]])
			return month


# add BondsProvider
fake.add_provider(BondsProvider)




# frames = [
#     "where can I buy",
#     "can I buy",
#     "looking to buy",
#     "looking to pick up"
#     "want to buy",
#     "where can I get",
#     "can I get",       # can i pls get _ OR can i get _ pls
#     "can you sell"     # pls can you sell _ OR can you sell __ ppls
#     "can you sell me" # please/pls
# ]
#
# content = [   # looking to buy 50k of the March 23 9.25%
#     ("40k of the AAPL March 2.13% for (under) 45", SIZE  "of the" TICKER DATE COUPON "for under" PRICE),
#     ("40k of the AAPL 2.13% 23s for (under) 45", SIZE  "of the" TICKER COUPON DATE "for under" PRICE),
#     ("40k of the AAPL 9.25% 23s", SIZE  "of the" TICKER COUPON DATE),     # coupon and date can swap places
#     ("40k of the AAPL 23s @ 9.25%", SIZE  "of the" TICKER DATE "@" COUPON),
#     ("40k of the AAPL 23s", SIZE  "of the" TICKER DATE),
#     ("40k for (under) 45", SIZE, DATE, "for under", PRICE),
#     ("40k", SIZE),
#
#     # ("AAPL 23s 3.5% for (under) 45", TICKER DATE COUPON "for under" PRICE),
#     # vary ticker coupon date price; drop price;
#     ("AAPL 3.5% 23s for (under) 45", TICKER COUPON DATE "for under" PRICE),
#     ("AAPL 3.5% 23s", TICKER COUPON DATE),      #
#     ("AAPL 23s", TICKER, DATE),
#
#     # no coupon + price
#     ("AAPL 23s for (under) 45", TICKER DATE "for under" PRICE),
#     ("some for (under 45)", "some", "for under", PRICE),
#     # ("March 23s @ 9.25%")
#     ("50k of the March 23 9.25%", SIZE, "of the" DATE COUPON)
]