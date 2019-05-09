#!/usr/bin/env python3
# This is the CGI decode function as shown in the course
import sys

hex_values = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15,
    'A': 10,
    'B': 11,
    'C': 12,
    'D': 13,
    'E': 14,
    'F': 15,
}

def cgi_decode(s):
    t = ""
    i = 0
    state = 0
    val = iter(s)
    while True:
        if state == 1:
            c = next(val, '')
            if c == '' or c not in hex_values:
                raise Exception('0')
            digit_high = c
            i = i + 1
            state = 2
        elif state == 2:
            c = next(val, '')
            if c == '' or c not in hex_values:
                raise Exception('0')
            digit_low = c
            i = i + 1
            state = 3
        elif state == 3:
            v = hex_values[digit_high] * 16 + hex_values[digit_low]
            t = t + chr(v)
            state = 0
        elif state == 0:
            c = next(val, '')
            if c == '':
                return t
            if c == '+':
                t = t + ' '
            elif c == '%':
                state = 1
                i = i + 1
            else:
                t = t + c
            i = i + 1
    return t

def main(arg):
    cgi_decode(arg)
