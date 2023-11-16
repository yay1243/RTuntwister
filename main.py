import random
import MT19937
import logging


def unscramble(output):
    xor_last = output >> 18
    output_third = output ^ xor_last
    xor_third = (output_third << 15 & 0xefc60000)
    output_second = output_third ^ xor_third
    aligned_const = 0x9d2c5680 >> 7
    intermediate = 0
    for count in range(3):
        a = output_second ^ intermediate
        intermediate = (a & aligned_const) << 7
    l = output_second ^ intermediate
    xor_second = ((l << 7) & 0x9d2c5680)
    output_first = output_second ^ xor_second
    m = output_first >> 11
    n = output_first ^ m
    o = n >> 11
    initial = output_first ^ o
    return initial


def scramble(input):
    # all funcs work as expected
    twisted = input ^ (input >> 11)
    twisted = twisted ^ ((twisted << 7) & 0x9d2c5680)
    twisted = twisted ^ ((twisted << 15) & 0xefc60000)
    twisted = twisted ^ (twisted >> 18)
    return twisted


if __name__ == '__main__':
    MT19937.mt_seed(1)
    state_values = []
    output_values = []
    used_state_value = []
    for a in range(1100):
        MT19937.extract_number()
    for a in range(1000):
        used_state_value.append(MT19937.MT[MT19937.index % MT19937.n])
        value_out = MT19937.extract_number()
        output_values.append(value_out)
        unscrambled_out = unscramble(value_out)
        state_values.append(unscrambled_out)
    #print(MT19937.cur_state)
    print(output_values)
    #print(used_state_value)
    #print(state_values)
    MT19937.MT = state_values[:624]
    MT19937.index = 0
    output_values_recreated = []
    for a in range(1000):
        output_values_recreated.append(MT19937.extract_number())
    print(output_values_recreated)
    for a in range (1000000):
        b = MT19937.extract_number()
        assert(b == unscramble(scramble(b)))


