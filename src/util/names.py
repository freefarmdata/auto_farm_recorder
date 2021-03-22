import random

names = [
    'phil',
    'james',
    'jack',
    'frank',
    'chris',
    'becca',
    'dyson',
    'clint',
    'randy',
    'cate',
    'kole',
    'janette',
    'perry',
    'rod',
    'juliet',
    'fox'
]

numbers = [
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
    'ten'
]

def random_name():
    global names, numbers
    n1 = random.randint(0, len(names)-1)
    n2 = random.randint(0, len(numbers)-1)
    return f'{names[n1]}_{numbers[n2]}'
