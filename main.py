import random


def untwist(output):
    xor_last = output >> 18
    output_third = output ^ xor_last
    xor_third = (output_third << 15 & 0xefc60000)
    output_second = output_third ^ xor_third
    a = output_second
    b = 0x9d2c5680 >> 7
    c = (a & b) << 7
    d = output_second ^ c
    e = d
    f = 0x9d2c5680 >> 7
    g = (e & f) << 7
    h = output_second ^ g
    i = h
    j = 0x9d2c5680 >> 7
    k = (i & j) << 7
    l = output_second ^ k
    xor_second = ((l << 7) & 0x9d2c5680)
    output_first = output_second ^ xor_second
    m = output_first >> 11
    n = output_first ^ m
    o = n >> 11
    initial = output_first ^ o
    # print("Untwisted value: " + format(initial, 'b') + ", " + str(initial))
    return initial


def twist(input):
    # all funcs work as expected
    twisted = input ^ (input >> 11)
    twisted = twisted ^ ((twisted << 7) & 0x9d2c5680)
    twisted = twisted ^ ((twisted << 15) & 0xefc60000)
    twisted = twisted ^ (twisted >> 18)
    return twisted


if __name__ == '__main__':
    random.seed(1)
    #1100/0011/1000/0110/1011/1011/1100/0100
    # 3280387012
    #print(format(random.randint(0, (2**32)-1), 'b'))
    a = random.randint(0, (2**32)-2)
    print(a)
    print(twist(a))
    untwist(twist(a))
    for b in range(2**22):
        c = random.randint(0, 40)
        assert c == untwist(twist(c))
        if b % 100000 == 0:
            print(b)
    #a = random.randbytes(4)
    #print(format(random.getrandbits(8), "b"))


