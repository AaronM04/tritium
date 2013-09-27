#!/usr/bin/python
# tritium.py
# balanced ternary module for Python
# written after being inspired by https://en.wikipedia.org/wiki/Balanced_ternary

from collections import namedtuple


charset_base3 = 'T01'    # represented by 0b11, 0b00, and 0b01, respectively; 0b10 is invalid

charset_base27 = 'MN' + ''.join([chr(ord('A')+x) for x in xrange(13+2, 26)]) + '0123456789ABCD'

TritNumber = namedtuple('TritNumber', 'n checked')     # n is a non-zero integer (really a bitmap); checked is boolean

class BadTritNumberException(Exception): pass



def trit(n):
    "given a regular binary number, return a TritNumber"
    pass #XXX



def check(tn, force_check=False):
    """given a TritNumber, check it; if force_check is True, do the check even
    if tn.checked is True; returns the same TritNumber if it is valid, otherwise
    raises a BadTritNumberException"""
    if type(tn) is not TritNumber:
        raise BadTritNumberException('not a TritNumber: %r' % tn)

    if tn.checked and (not force_check):
        return tn

    if tn.n < 0:
        raise BadTritNumberException('internal value of TritNumber is negative: 0x%x' % tn.n)

    n = tn.n
    all01 = 0x55555555
    while n > 0:
        if ((n>>1) & ~n) & all01  != 0:
            raise BadTritNumberException('invalid trit in internal value of TritNumber: 0x%x' % tn.n)
        n >>= 32

    return TritNumber(tn.n, True)     # True because checked


def to_bin(tn):
    "given a TritNumber, return a regular binary number"
    tn = check(tn)
    #XXX
