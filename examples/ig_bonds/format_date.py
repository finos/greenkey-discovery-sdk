#!/usr/bin/env python3

import re
from discovery.nlp.constants import constants

def monthToNum(month):
    """ Converts month code to number (e.g. AUG -> 8) """
    ordered_month_list = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    return ordered_month_list.index(month[:3].upper()) + 1


def formatting(entity):
    " get maturity from input possible terms "

    entity = entity.lower().split()
    found_months = list(set(_ for _ in entity).intersection(set(constants['months'])))
    found_month = str(monthToNum(found_months[0].upper()[:3]))

    numbers = [_ for _ in entity if _ not in found_months]
    date = re.sub('[^0-9]','', "".join(numbers))

    return '/'.join([date, found_month])
