#!/usr/bin/env python3

import mailbox
import re
import numpy as np
from collections import defaultdict
import fire
eighths_dict = {"⅛": ".125", "¼": ".25", "⅜": ".375", "½": ".5", "⅝": ".625", "¾": ".75", "⅞": ".875"}
security_price_db = defaultdict(lambda: [])


def get_security(line):
  line = line.split()
  ticker, coupon, maturity = line[:3]
  ticker = ticker.upper()

  if not all(map(lambda c: c.isalpha(), list(ticker))):
    return

  for k in eighths_dict.keys():
    coupon = coupon.replace(k, eighths_dict[k])

  if all(map(lambda c: c.isdigit() or c in ['.', '-'], list(coupon))):
    coupon = "{:.3f}".format(round(float(coupon), 3))

  if len(line) > 4:
    prices = line[3:5]
    prices = [_ for _ in prices if all(map(lambda c: c.isdigit() or c in ['.', '-'], list(_))) and float(_)<200.]
    if prices:
      security_price_db[" ".join([ticker, coupon, maturity])] += list(map(float, prices))


def cut_signature(body):
  """
    Removes Jefferies signature and other non essential information
  """

  # turn into list
  body = body.splitlines()

  # remove signature
  body = body[:-2]

  # move from binary to string
  body = [line if isinstance(line, str) else line.decode() for line in body]

  # cut empty lines
  body = [line.strip() for line in body if line.strip()]

  # cut lines with filter words
  filter_words = [
    "***", "uyer", "eller", "Securit", "---", "Jefferies", "http", "ASK", "SOVS", "ignore", "CORPS", "AXES", "BSz",
    "Amt", 'FROM:', 'AEFES', 'HOWEVER,', 'DOWNSTREAM', 'EXPECTED', 'IN', 'NEW', 'CLIENT', 'JOURNALISTS:', 'ADDITIONAL',
    'THAT', 'FROM', 'AGENTS,', '144A', 'SUBSIDIARY', 'IF', 'INVESTORS', 'THIS', 'GOVERNMENT', 'EMPLOYEES,', 'TCGLN',
    'PRICED:', 'BOOKS:', '(EXPECTED)', 'CAPITAL,', 'BOOK', '[NEW]', 'CLIENTS&#34;', 'LEADS', 'DATE:', 'LIMITED', 'IPT:',
    'BLOOMBERG)', 'ANALYTICS,', 'ONE', 'ALL', 'DEBT', 'SHARJAH', 'SHAJI', 'GENERALE', 'GUIDANCE', 'SETTLE', 'GIVEN',
    'AFFILIATES', 'POLICIES', 'MEET', 'ANNOUNCED', 'REGULATORY', 'NON-NRSRO', 'REMAINS', 'BETWEEN', 'WITH',
    'PROVIDER&#39;S', 'DO', 'LINKAGE', 'REGISTRATION', 'ANALYST', 'WHOLESALE', 'THE', 'NO', 'AS', 'ROYAL', 'FORM',
    'DISCLOSURES', 'DAILY', 'FACT.', 'DERIVED', 'OBLIGATION', 'APPLICABLE)', '2018.', 'UNDER', 'VERIFY', '...85BPS',
    'ANTICIPATES', 'INCLUDED', 'IPO', 'PRACTICES.', 'FUNDAMENTAL', 'NEGATIVE', 'HYDROCARBON', 'INVESTMENT', 'MEASURE',
    'WHILE', 'COMPARES', 'MARKET', 'COPY', '(SAUDI', 'HOLD', 'WHATSOEVER,', 'TERM', 'LONDON,', 'EXXON', 'WIDER',
    'HEADQUARTERED', 'DOUBT,', 'MANNER', 'SERVICES,', 'FACILITIES.', 'REFINING', '33.5%', 'SECURITIES', 'SUCH',
    'CONTRACTUAL', 'DIVIDENDS.', 'SUPPORT', 'SHEET', 'SUPPLIER', 'RANGING', 'CERTAIN', 'RATIONALE', 'IMPACT',
    'ORGANIZATION', 'BUSINESS', 'WEAK', 'THEREFORE', 'RELIABLE', 'RELATED', 'RESILIENCE', 'PIPELINE:', 'SYMBOLS',
    'WILLFUL', 'JUNE', 'RISK', 'DIRECTLY', 'RETAIL', 'SIGNIFICANT,', 'WHICH', 'OTHER', 'FOCUS', '6.9MN', 'SECURITIES.',
    'DRIVEN', 'CORPORATION', 'COMPANIES', 'TAXES', 'COMMERCIAL', 'PUBLICATIONS', 'WORLD&#39;S', 'STRUCTURE', 'ABOUT',
    'INFORMATION,', 'DISSEMINATED,', 'INCIDENTAL', 'FINANCIAL', 'MCO.', 'INFORMATION', 'MECHANICAL', 'HAVE,',
    'ANNOUNCEMENT', 'INTEREST', '24S', 'IPT', 'STRONG', 'CASH', 'CLOSELY', 'REPORTED', 'HEREIN', 'LOSS', 'COMMENT',
    'SOME', '6MN', 'COMMITMENTS', 'FUTURE', 'OTHERWISE', 'BORFIN', 'CEILING)', 'STRATEGY', 'WHOLLY-OWNED', 'FINAL',
    'SPA:', 'USED', 'TERMS', 'PURCHASE,', 'RATINGS', 'MAY', 'INTERLINKAGES', 'BEYOND', 'ASSIGNED', 'INDUSTRY',
    'EXPECTATION', 'OWN', 'SUBJECT:', 'PROVIDE', 'HIGHLY', '(C)', 'GENERATION', 'CATEGORY', 'JPY125,000', 'FIRM',
    'POSSIBILITY', 'AFFILIATE,', 'PROFILE', 'BILLION,', 'CONTINUING', 'PROVIDES', 'BLENDED', 'INC.', 'GROUP', 'CAPITAL',
    'STATE-OWNED', 'BEEN', 'LEVERAGE', 'APPLICABLE).', 'DOCUMENT', 'COUNTERCYCLICAL', 'BY', 'WHAT', 'MERCHANTABILITY',
    'NECESSARY', 'ACTION', 'THESE', 'EXIST', 'CAPACITY', 'PREFCHEM', 'ENTITY', 'BOOKS', 'ISSUER', "OBLIGOR",
    'STRUCTURE', 'FORMAT', 'JOINT', 'LAW', 'DENOMS', 'CONTACT', 'COORD', 'IRISH', 'SECURIT', 'EXPECT', 'DEAL', 'GMT',
    'Security', 'REOFFER', 'YTD', 'SWITCH', "OFFICER", 'STATUS', 'SIZE'
  ]

  # clean_line
  cut_this_pattern = re.compile(r"{[A-z]*}")
  clean_line = lambda line: cut_this_pattern.sub("",line) \
                            .replace("USD","")  \
                            .replace("/", " ")  \
                            .replace("EUR","")  \
                            .replace("  ", " ") \
                            .replace(" - "," ") \
                            .replace(" at "," ")

  body = [
    clean_line(line).strip() for line in body \
      if not any(_.upper() in line.upper() for _ in filter_words) \
        and len(line.split()) > 3 \
        and not line.strip().startswith("Security")
  ]

  return body


def get_body(message):
  """
  getting plain text 'email body'
  https://stackoverflow.com/a/31489271
  """
  body = None
  if message.is_multipart():
    for part in message.walk():
      if part.is_multipart():
        for subpart in part.walk():
          if subpart.get_content_type() == 'text/plain':
            body = subpart.get_payload(decode=True)
      elif part.get_content_type() == 'text/plain':
        body = part.get_payload(decode=True)
  elif message.get_content_type() == 'text/plain':
    body = message.get_payload(decode=True)
  return cut_signature(body.decode())


def is_run(message):
  """
  check for runs in message list-post and ensure it's not some news from Jefferies traders
  """
  ignored_subjects = ['BN', 'BFW', 'EOD', 'CLOSE', 'OPEN', "MIDDAY"]
  ignored_senders = ['mgoldey', 'sharklasers']
  return 'List-Post' in message \
    and 'runs' in message['List-Post'] \
    and 'subject' in message \
    and not any(_ in message['subject'].upper() for _ in ignored_subjects) \
    and 'reply-to' in message \
    and not any(_ in message['reply-to'] for _ in ignored_senders)


def print_most_active_tickers(message_bodies):
  tickers = defaultdict(lambda: 0)
  for body in message_bodies:
    for line in body:
      line = line.split()
      ticker = line[0] if '{' not in line[0] else line[1]
      tickers[ticker.upper()] += 1
  tickers = sorted([[k, v] for k, v in tickers.items()], key=lambda row: -row[1])

  column_1 = "Ticker"
  column_2 = "Frequency"
  width = 15
  print(column_1.ljust(width) + column_2.rjust(width))
  print("-" * (width) + "|" + "-" * (width))
  for row in tickers:
    print(row[0].ljust(width) + "|" + str(row[1]).rjust(width))


def get_runs(mailbox_location="/var/mail/matthew"):
  mb = mailbox.mbox(mailbox_location)
  messages = [_[1] for _ in mb.items()]

  runs = [message for message in messages if is_run(message)]
  bodies = [get_body(run) for run in runs]

  for body in bodies:
    for line in body:
      get_security(line)

  print_most_active_tickers(bodies)

  with open("imstrings.txt", 'w') as output:
    output.write("\n".join("\n".join(body) for body in bodies if body))

  with open("security_db.txt", 'w') as output:
    for k, v in security_price_db.items():
      try:
        output.write(" ".join([str(k), str(np.mean(v)), str(np.std(v)), str(len(v) // 2)]) + "\n")
      except:
        print(k, v)


if __name__ == "__main__":
  fire.Fire(get_runs)
