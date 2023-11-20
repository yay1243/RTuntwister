import random


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


def randint_emulator(states, range):
    size = range.bit_length()
    index = states[-1]
    while (scramble(states[index]) >> (32-size)) >= range:
        index += 1
    number = scramble(states[index]) >> (32-size)
    return number, index


if __name__ == '__main__':
    random.seed()
    output_numbers = []
    state_values = []
    further_output = []
    new_gen_further_output = []
    for a in range(1000000):
        random.random()
    for a in range(624):
        output = random.getrandbits(32)
        output_numbers.append(output)
        state_values.append(unscramble(output))
    for a in range(100):
        further_output.append(random.getrandbits(32))
    print(output_numbers)
    state_values.append(0)
    random.setstate((3, tuple(state_values), None))
    new_gen_output = []
    for a in range(624):
        new_gen_output.append(random.getrandbits(32))
    print(new_gen_output)
    for a in range(100):
        new_gen_further_output.append(random.getrandbits(32))
    assert(new_gen_output == output_numbers)
    assert(new_gen_further_output == further_output)


# if __name__ == '__ain__':
#     random.seed(1)
#     a = random.getstate()
#     print(a)
#     random_number = random.getrandbits(32)
#     print(random_number)
#     before = random.getstate()
#     print(before)
#     test = before[1][0]
#     print(scramble(test))
#     print(unscramble(random_number))
#     for b in range(100):
#         random.getrandbits(32)
#     after = random.getstate()
#     print(after)
#     count = 0
#     for idx, c in enumerate(before[1]):
#         if c != before[1][idx]:
#             count += 1
#     print(count)



