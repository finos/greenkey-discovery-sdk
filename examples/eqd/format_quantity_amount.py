#!/usr/bin/env python3

quantity_dict = {
    "k": "M",
    "thousand": "M",
    "million": "MM",
    "mill": "MM",
    "mills": "MM",
    "millions": "MM",
    "yard": "MMM",
    "billion": "MMM",
    "yards": "MMM",
}


def formatting(entity):
    return "".join(quantity_dict[_] if _ in quantity_dict else _ for _ in str(entity).split())