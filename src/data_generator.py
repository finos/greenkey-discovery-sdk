# nom = net operation margin? nuveen missouri remium fund (american stock exchange [AMEX]
import random
import string
from faker import Faker
fake = Faker()






PLEASE = ['please', 'pls']


DATE = ["1/22", "Jan 22", "Jan 22's" "January 2022", "02/01/22", "2Jan22", "2 Jan 22", "apr22, 17jul19"]
DATE_SIZE = ['17Jul19-6m']
DATE_PRICE = ['1.875arl 22 nom']


# PLEASE CAN_I get/have a quote/price ON TICKER DATE COUPON
# PLEASE quote/price TICKER DATE COUPON


# can I buy 40k (of the) AAPL 43s for (under) 42
# CAN_I BUY SIZE (of the)? TICKER DATE COUPON FOR (under)? PRICE

# contains all components: product (ticker coupon, maturity), size (40k), price (42)
# can you sell me 40k (of the) APPL 43s 3.5% for (under) 42

# ["can I buy", "40", "k"]


DATE_FORMATS = [
    "23s",
    "apr22",
    "March 23",
    "Jan 29s",
    "March 28, 2019",
    "10jun2019",
    "16-jul19"
    "15May24"
    "Jun"
    "1/21"]


DATE_COMBOS = [
    "19jun19-10y",
    "17-jul19-6m",
    "March 23 9.25%",
    "Jun IMM 2y @0.0%",
    "IMMU9-15May24"
]

buy1 = "can I buy"
buy2 = "can I get"
sell = "can you sell"

# year could have ' -> 23 vs 23's              # 02/03/23
# Mar mar | March march
# 03/23  3/23 ||  02/03/23  2/3/23  12/3/23  12/03/23
DATE = ["23s",
        "3/23",
        "Mar 23s",
        "March 23s",
        "2/3/23",
        "2Mar23", "2March23",
        "2Mar2023", "2March2023",
        "2 March 23s", "March 2, 2023 "
        ]


# this returns ALL tickers at once rather than 1 by 1
def gen_ticker():
    # ticker = random.choice(["AAPL", 'HD', 'MOZAM', 'EUR'])
    letters = " ".join(string.ascii_letters).split()
    num_letters = random.choice([1,2,2, 2,3,3,3,4,4,4,5])
    ticker = ''.join(random.sample(letters, num_letters))
    if len(ticker) < 3:
        return ticker.upper()
    return ticker.upper() if random.random() >= 0.5 else ticker.lower()

# gen_ticker()
# [gen_ticker() for _ in range(20)]



def gen_coupon():
    """ decimal with 1-4 decimal points +/- %"""
    coupon_num = random.random()
    precision = random.choice([1,2,3,4])
    include_percent = random.choice(["", "%"])
    include_at = random.choice(["", "@ "])
    coupon_value = round(coupon_num, precision)
    coupon = "{}{}{}".format(
        include_at, coupon_value, include_percent)
    return coupon

# [gen_coupon() for _ in range(20)]
# fake.add_provider(date_time)

def gen_maturity():
    pass


#TODO include par > 100
def gen_price(precision=2):
    par = random.choice([100,0])
    decimal = random.random()
    if par:
        price = round(par + decimal, precision)
    else:
        price = int("{}{}".format(random.randrange(1,9), random.randrange(1,9)))
        # price = int(decimal*100)
    return price

# [gen_price() for _ in range(20)]



def gen_size():
    # decide whether to include ['k', 'm', 'mm'] and whether it should be .upper() or .lower()
    # decide whether to include commas 1,900 1.9mm -> 1,900,000
    pass


def gen_quote():
    pass


def gen_price(precision=2):
    """include $ or USD"""
    par = random.choice([100, 0])
    decimal = random.choice()
    if par:  # 100.42
        price = round(par + decimal, precision)
    else:  # 42
        # incl_bps = 'bps' if random.random() >= 0.8 else ''
        price = int("{}{}".format(random.randrange(1, 9), random.randrange(1, 9)))
    currency = random.choice('', '$', 'USD')
    price = "{}{} {}".format(currency, price, currency)
    if currency != 'USD':
        price = price.split()[0].strip()
    return price




# TESTS

def test_gen_ticker_fixed_tickers():
    random.seed(99)
    expected = ['eur', 'hd', 'HD', 'MOZAM', 'AAPL']
    t1, t2, t3, t4, t5 = [gen_ticker() for _ in range(5)]
    assert t1.lower() and t2.lower() and t3.upper and t4.upper()
    observed = [t1,t2,t3,t4,t5]
    assert len({ticker.lower() for ticker in observed}) == 4
    assert len(observed) == 5
    assert expected == observed

def test_gen_coupon():
    print("Random seed is zero. coupon_generator() returns values in order present in list of expected outcomes")
    random.seed(0)
    expected = [
        '@ 0.8444',
        '@ 0.9655%',
        '0.968'
    ]
    assert all([gen_coupon() == coupon for coupon in expected]) is True

    print("Seed is one. coupon_generator will not return values ordered as in 'expected' list")
    random.seed(1)
    assert all([gen_coupon()==coupon for coupon in expected]) is False

def test_gen_coupon2():
    random.seed(99)
    expected = ['0.4', '@ 0.2%', '0.5%', '@ 0.42%', '@ 0.86']
    first, second, third, fourth, fifth = [gen_coupon() for _ in range(5)]
    assert not '@' in first and not '%' in first
    assert second.startswith('@') and second.endswith("%")
    assert not '@' in third and third.endswith('%')

    assert fourth.startswith("@") and fourth.endswith("%")
    assert fifth.startswith("@") and not "%" in fifth
    observed = [first, second, third, fourth, fifth]
    assert all(["." in num for num in observed])
    assert [
        len(str(coupon).split())==2 if "@" in coupon else len(str(coupon).split())==1
        for coupon in observed
    ]
    assert expected == observed


def test_gen_ticker():
    ticker = gen_ticker()
    if len(ticker) < 3:
        assert ticker.lower()
    assert len(ticker) <= 5

def test_gen_price():
    precision = 2
    price = gen_price(precision)
    print(price)
    if price - 100 >= 0:
        assert isinstance(price, float)
        assert len(str(price)) == 3 + precision + 1 #for the decimal point
    else:
        assert isinstance(price, int)
        assert len(str(price)) == 2
    # print(gen_price)


# RUN TESTS
# test_gen_ticker_fixed_tickers()
test_gen_ticker()
test_gen_coupon()
test_gen_coupon2()

test_gen_price()







def gen_date():
    date = fake.date()

    # year
    year = date.year
    num_year_digits = random.choice([2,4])
    year = year[:num_year_digits]
    if num_year_digits == 2:
        incl_s = 's' if random.random() >= 0.5 else ''
        year = year + incl_s

    # month
    incl_month = date.month if random.random >= 0.5 else ''   # month can only appear if year is included

    # day
    incl_day = (date.day if random.random >= 0.5 and incl_month else '')  # but only include if month is included

    # TODO NEED TO INCORPORATE YEAR POSSIBLE FORMATS
    format = select_year_format()
    return format_date(year, incl_month, incl_day)

    # return date in that format including year & month if selected & year if selected


frames = [
    "where can I buy",
    "can I buy",
    "looking to buy",
    "looking to pick up"
    "want to buy",
    "where can I get",
    "can I get",       # can i pls get _ OR can i get _ pls
    "can you sell"     # pls can you sell _ OR can you sell __ ppls
    "can you sell me" # please/pls
]

content = [   # looking to buy 50k of the March 23 9.25%
    ("40k of the AAPL March 2.13% for (under) 45", SIZE  "of the" TICKER DATE COUPON "for under" PRICE),
    ("40k of the AAPL 2.13% 23s for (under) 45", SIZE  "of the" TICKER COUPON DATE "for under" PRICE),
    ("40k of the AAPL 9.25% 23s", SIZE  "of the" TICKER COUPON DATE),     # coupon and date can swap places
    ("40k of the AAPL 23s @ 9.25%", SIZE  "of the" TICKER DATE "@" COUPON),
    ("40k of the AAPL 23s", SIZE  "of the" TICKER DATE),
    ("40k for (under) 45", SIZE, DATE, "for under", PRICE),
    ("40k", SIZE),

    # ("AAPL 23s 3.5% for (under) 45", TICKER DATE COUPON "for under" PRICE),
    # vary ticker coupon date price; drop price;
    ("AAPL 3.5% 23s for (under) 45", TICKER COUPON DATE "for under" PRICE),
    ("AAPL 3.5% 23s", TICKER COUPON DATE),      #
    ("AAPL 23s", TICKER, DATE),

    # no coupon + price
    ("AAPL 23s for (under) 45", TICKER DATE "for under" PRICE),
    ("some for (under 45)", "some", "for under", PRICE),
    # ("March 23s @ 9.25%")
    ("50k of the March 23 9.25%", SIZE, "of the" DATE COUPON)
]



#
# #SIZE_UNIT (of the) PRODUCT for (under) PRICE
# SIZE, SIZE_UNIT = 1.9, 'M'
# SIZE_UNIT = "{}{}".format(SIZE, SIZE_UNIT)
#
#
# Price = ("40", "100.40", "USD 40", "40 USD")
#
#
# verbs = ["get", "have"]
#
# can_i_frames = [
#     "Can I {verb} a {quote/price} on {TICKER} {COUPON}% {MATURITY}"
# ]
#
#
#
#
#
#
# # verbs = ["buy", "sell"]
#
# please_words = ['please', 'pls']
#
# make me a market on AAPL 23s
# can I have a market in USD 75k/bp
# pls make 50mm 1y RPI, comp 2 others
#
#
# can i buy 40k AAPL 43s
# can I buy 40k of the AAPL 43s?
# can you sell me 40k APPL 43s
# can you sell me 40k of the APPL 43s
#
# pls price eur 1.266b 17Jul19-6m fra/enonia lch
#
# can I buy 5M AAPL 3Feb2010 for 66
# can you sell me 5M APPL 3Feb2010 for 66
#
#
# where can I buy/get 5M AAPL 3Feb2010 for under 66
#
#
# looking to buy 50k of the March 23 9.25%
#
# looking to pick up 50 of the March 23 9.25%
#
# looking at the APPL Jan 29's like to buy some under 101
#
#
# can i have a quote
# can i get a price