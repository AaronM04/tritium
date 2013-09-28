#!/usr/bin/python
# tritium.py
# balanced ternary module for Python
# written after being inspired by https://en.wikipedia.org/wiki/Balanced_ternary
# and http://www.computer-museum.ru/english/setun.htm

from collections import namedtuple


charset_base3 = 'T01'    # represented by 0b11, 0b00, and 0b01, respectively; 0b10 is invalid

trit_to_bit  = {'T': 0b11,
                '0': 0b00,
                '1': 0b01}

bit_to_trit = {0b11: 'T',
               0b00: '0',
               0b01: '1'}

bit_to_tritval = {0b11: -1,
                  0b00:  0,
                  0b01:  1}

magic_map ={0: (0b0000, 0b00),  #00
            1: (0b0000, 0b01),  #01
            2: (0b0100, 0b11),  #1T
            3: (0b0000, 0b11),  #10
            4: (0b0000, 0b00),  #00
            5: (0b0000, 0b01),  #01
            6: (0b1100, 0b01),  #T1
            7: (0b0000, 0b11),  #0T
            9: (0b1100, 0b00)}  #T0



charset_base27 = 'MNPQRSTUVWXYZ0123456789ABCD'  # I left out 'O' because it looks too much like '0'

def _convert_int(x):
    "given a regular binary number, convert to a bitmap of trits"
    n = 0b0
    shift = 0
    while x != 0:
        bitpair = (x%3) & 0b11
        if bitpair == 0b10:
            bitpair = 0b11
        n |= bitpair << shift
        shift += 2
        x = (x+1)/3
    return n



class TritNumber(namedtuple('TritNumber', 'n checked')):   # n is a non-zero integer (really a bitmap); checked is boolean
    __slots__ = ()

    def __new__(_cls, *args, **keys):
        if len(keys) != 0 or len(args) > 2:
            raise ValueError('expected either a string or (integer-bitmap, boolean) as arguments')
        if len(args) == 2:
            return tuple.__new__(_cls, args)    # this is the standard named tuple behavior
        # now, we are processing a string that matches /\*?(0g)?[T01]+/
        s = args[0]
        n = 0
        if type(s) is not str and type(s) is not unicode:
            self.__init__(self, *args, **keys)  # pass to the super-class (a named tuple)
            return
        if s.startswith('*'):
            s = s[1:]
        if s.startswith('0g'):
            s = s[2:]
        if len(s) == 0:
            raise ValueError('no digits in balanced trinary number %r' % s)
        for digit in s:
            if not trit_to_bit.has_key(digit):
                raise ValueError('invalid trinary digit %r' % digit)
            n = (n << 2) | trit_to_bit[digit]
        return tuple.__new__(_cls, (n, True))

    def __add__(self, x):
        if type(x) is int or type(x) is long:
            # convert to trit bitmap
            q = _convert_int(x)
        else:
            q = x.n

        carry = 0
        p = self.n
        shift = 0
        total = 0
        while p > 0 or q > 0 or carry > 0:
            pbits, qbits, carrybits = (p & 0b11, q & 0b11, carry & 0b11)
            # magic! :-)
            if (pbits, qbits, carrybits) == (1,1,1):
                high_pair, low_pair = (0b0100, 0b00)
            else:
                naive_sum = pbits + qbits + carrybits
                high_pair, low_pair = magic_map[naive_sum]
            carry |= high_pair
            total |= (low_pair << shift)
            p >>= 2
            q >>= 2
            carry >>= 2
            shift += 2
        return TritNumber(total, True)


    def __int__(self):
        "convert to a regular binary integer"
        x = 0
        n = self.n
        z = 1
        while n > 0:
            bitpair = n & 0b11
            if bitpair == 0b10:
                raise ValueError('invalid trinary digit')
            x += bit_to_tritval[ bitpair ]*z
            n >>= 2
            z *= 3
        return x

    def __str__(self):
        s = '0g'
        if not self.checked:   # if unchecked, prepend a '*'
            s = '*' + s
        # calculate the trits
        digits = []
        n = self.n
        while n > 0:
            d = n & 0b11
            digits.insert(0, '01!T'[d])     # '! is for an invalid trit
            n >>= 2
        if len(digits) == 0:
            digits = ['0']
        s += ''.join(digits)
        return s

    def __repr__(self):
        return 'TritNumber("%s")' % str(self)



def check(tn, force_check=False):
    """given a TritNumber, check it; if force_check is True, do the check even
    if tn.checked is True; returns the same TritNumber if it is valid, otherwise
    raises a ValueError exception"""
    if type(tn) is not TritNumber:
        raise ValueError('not a TritNumber: %r' % tn)

    if tn.checked and (not force_check):
        return tn

    if tn.n < 0:
        raise ValueError('internal value of TritNumber is negative: -0x%x' % -tn.n)

    n = tn.n
    all01 = 0x55555555
    while n > 0:
        if ((n>>1) & ~n) & all01  != 0:
            raise ValueError('invalid trit in internal value of TritNumber: 0x%x' % tn.n)
        n >>= 32

    return TritNumber(tn.n, True)     # True because checked


def to_bin(tn):
    "given a TritNumber, return a regular binary number"
    tn = check(tn)
    #XXX
