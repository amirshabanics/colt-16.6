import random


def random_item(list: list):
    return list[random.randint(0, len(list) - 1)]
