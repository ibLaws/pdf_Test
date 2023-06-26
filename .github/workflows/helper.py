#!/usr/bin/env python3
import os
import re
import sys


def image_output(images_index):
    if ":" in images_index:
        st, end = images_index.split(':')
        return [i for i in range(int(st), int(end) + 1)]

    else:
        return re.findall('[\.,-]?(\d+)', images_index)


def domain_detector(ad_link):
    if re.search('.*?(mobile\.de)/', ad_link):
        return 'SuchenMobileDe'

    elif re.search('.*?(autoscout24\.de)/', ad_link):
        return 'AutoScout24De'


def price_format(price):
    price = str(price)
    decimal = ''
    if '.' in price:
        decimal = f'.{price.split(".")[-1]}'
        price = price.split('.')[0]

    if 2 < len(price) <= 6:
        return f'{price[:-3]},{price[-3:]}' + decimal
    elif len(price) > 6:
        return f'{price[:-6]},{price[-6:-3]},{price[-3:]}' + decimal
    else:
        return price


def remove_white_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()


def remove_unicode_char(input_string):
    """
    This function takes string as an input, and return strings after removing unicode character
    """
    return (''.join([i if ord(i) < 128 else ' ' for i in input_string])).strip()


def extract_number_only(input_string):
    numbers = re.findall(r'\d+(?:\.\d+)?', input_string)
    if numbers:
        return numbers
    else:
        return 0
    # return (''.join(filter(lambda i: i.isdigit(), remove_white_spaces(input_string)))).strip()


def summation(numbers):
    summ = 0
    for num in numbers:
        summ += float(num)

    return summ


def calculate_percentage(percent, num):
    return round(float(percent) / 100 * float(num), 5)


def list2table(list_data):
    out_put = []
    if len(list_data) % 2 == 0:
        for i in range(0, len(list_data), 2):
            out_put.append([list_data[i], list_data[i + 1]])
    else:
        for i in range(0, len(list_data) - 1, 2):
            out_put.append([list_data[i], list_data[i + 1]])
        out_put.append([list_data[-1], ''])

    return out_put


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
