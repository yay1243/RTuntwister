import random
import z3


def untemper(output):
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


def z3_untemper(output):
    solver = z3.Solver()
    y1 = z3.BitVec('y1', 32)
    y2 = z3.BitVec('y2', 32)
    y3 = z3.BitVec('y3', 32)
    y4 = z3.BitVec('y4', 32)
    y5 = z3.BitVec('y5', 32)
    y = z3.BitVecVal(output, 32)
    equations = [
        y2 == y1 ^ (z3.LShR(y1, 11)),
        y3 == y2 ^ ((y2 << 7) & 0x9d2c5680),
        y4 == y3 ^ ((y3 << 15) & 0xefc60000),
        y == y4 ^ (z3.LShR(y4, 18))
    ]
    solver.add(equations)
    solver.check()
    return solver.model()[y1].as_long()


def z3_solver(outputs1, outputs2, bit_length):
    offset = 32 - bit_length
    solver = z3.Solver()
    cur_index = 0
    upper_mask = 0x80000000
    lower_mask = 0x7fffffff
    matrix = [0, 0x9908b0df]
    y_base_state = z3.BitVec('y_base', 32)
    y1 = z3.BitVec('y1', 32)
    y2 = z3.BitVec('y2', 32)
    y3 = z3.BitVec('y3', 32)
    y_base_out = z3.BitVec('y_base_out', 32)
    y_base_offset = z3.BitVecVal(outputs1[cur_index], 32)
    y_baseplus1_state = z3.BitVec('y_baseplus1', 32)
    y4 = z3.BitVec('y4', 32)
    y5 = z3.BitVec('y5', 32)
    y6 = z3.BitVec('y6', 32)
    y_baseplus1_out = z3.BitVec('y_baseplus1_out', 32)
    y_baseplus1_offset = z3.BitVecVal(outputs1[(cur_index+1) % 624], 32)
    y_baseplus397_state = z3.BitVec('y_baseplus397', 32)
    y7 = z3.BitVec('y7', 32)
    y8 = z3.BitVec('y8', 32)
    y9 = z3.BitVec('y9', 32)
    y_baseplus397_out = z3.BitVec('y_baseplus397_out', 32)
    y_baseplus397_offset = z3.BitVecVal(outputs1[(cur_index+397) % 624], 32)
    y_refreshed_state = z3.BitVec('y_refreshed', 32)
    y10 = z3.BitVec('y10', 32)
    y11 = z3.BitVec('y11', 32)
    y12 = z3.BitVec('y12', 32)
    y_refreshed_out = z3.BitVec('y_refreshed_out', 32)
    y_refreshed_offset = z3.BitVecVal(outputs2[cur_index], 32)
    equations = [
        y1 == y_base_state ^ (z3.LShR(y_base_state, 11)),
        y2 == y1 ^ ((y1 << 7) & 0x9d2c5680),
        y3 == y2 ^ ((y2 << 15) & 0xefc60000),
        y_base_out == y3 ^ (z3.LShR(y3, 18)),
        y_base_offset == z3.LShR(y_base_out, offset),
        y4 == y_baseplus1_state ^ (z3.LShR(y_baseplus1_state, 11)),
        y5 == y4 ^ ((y4 << 7) & 0x9d2c5680),
        y6 == y5 ^ ((y5 << 15) & 0xefc60000),
        y_baseplus1_out == y6 ^ (z3.LShR(y6, 18)),
        y_baseplus1_offset == z3.LShR(y_baseplus1_out, offset),
        y7 == y_baseplus397_state ^ (z3.LShR(y_baseplus397_state, 11)),
        y8 == y7 ^ ((y7 << 7) & 0x9d2c5680),
        y9 == y8 ^ ((y8 << 15) & 0xefc60000),
        y_baseplus397_out == y9 ^ (z3.LShR(y9, 18)),
        y_baseplus397_offset == z3.LShR(y_baseplus397_out, offset),
        y10 == y_refreshed_state ^ (z3.LShR(y_refreshed_state, 11)),
        y11 == y10 ^ ((y10 << 7) & 0x9d2c5680),
        y12 == y11 ^ ((y11 << 15) & 0xefc60000),
        y_refreshed_out == y12 ^ (z3.LShR(y12, 18)),
        y_refreshed_offset == z3.LShR(y_refreshed_out, offset),
        y_refreshed_state == z3.If(((y_base_state & upper_mask) | (y_baseplus1_state & lower_mask)) << 31 == 0,
                                   # If Thingy last bit == 0, states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[0]
                                   y_baseplus397_state ^
                                   z3.LShR(((y_base_state & upper_mask) | (y_baseplus1_state & lower_mask)), 1),
                                   # If Thingy last bit != 1, states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[1]
                                   y_baseplus397_state
                                   ^ z3.LShR(((y_base_state & upper_mask) | (y_baseplus1_state & lower_mask)), 1)
                                   ^ 0x9908b0df
                                   )
        # y = (states[idx] & upper_mask) | (states[(idx + 1) % 624] & lower_mask)
        # temp = states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[y & 1]
    ]
    solver.add(equations)
    print(solver.check())
    temp = solver.model()[y_base_state].as_long() & upper_mask | solver.model()[y_baseplus1_state].as_long() & lower_mask
    temp = solver.model()[y_baseplus397_state].as_long() ^ (temp >> 1) ^ matrix[temp & 1]
    print(f"I hate my life {temp}")
    # counter = 0
    # while counter < 2 ** offset:
    #     if solver.check() == z3.sat:
    #         # Register state values at [0], [1], and [397] that the solver has obtained
    #         print(f"Tried values are: {solver.model()[y_base_state].as_long()} "
    #               f"{solver.model()[y_baseplus1_state].as_long()} and {solver.model()[y_baseplus397_state].as_long()}")
    #         # The output that they should produce
    #         temp = single_twist(solver.model()[y_base_state].as_long(), solver.model()[y_baseplus1_state].as_long(),
    #                             solver.model()[y_baseplus397_state].as_long())
    #         print(f"Guessed state value of 2nd output set  = {temp}")
    #         # On 1st titer, y_refreshed_state depends on output2[0]
    #         # In this case, there are only 2 possible outputs for this.
    #         # Now, I need to check if this output can be matched to a valid set of output1 state inputs.
    #         print(f"Check = {solver.model()[y_refreshed_state].as_long()}")
    #         if temp == solver.model()[y_refreshed_state].as_long():
    #             break
    #         else:
    #             print(f"Tempered output = {temper(solver.model()[y_refreshed_state].as_long())}")
    #             solver.add(y_refreshed_state != solver.model()[y_refreshed_state].as_long())
    #     counter += 1
    return solver.model()[y_refreshed_state].as_long()


def auto_z3_solver(outputs1, outputs2, bit_length):
    offset = 32 - bit_length
    solver = z3.Solver()
    solver.set("timeout", 500000000)
    upper_mask = 0x80000000
    lower_mask = 0x7fffffff
    matrix = [0, 0x9908b0df]
    # The stuff used for the 1st iteration of the RNG (0 - 623)
    # The stuff used for the 2nd iteration of the RNG (624 - 1247)
    y_initial_states = []
    y1_set = []
    y2_set = []
    y3_set = []
    y_initial_outputs = []
    y_initial_offset_outputs = []
    # The stuff used in the 2nd iteration of the RNG
    y_refreshed_states = []
    y4_set = []
    y5_set = []
    y6_set = []
    y_refreshed_outputs = []
    y_refreshed_offset_outputs = []
    for a in range(624):
        y_initial_states.append(z3.BitVec('y_baseplus' + str(a), 32))
        y1_set.append(z3.BitVec('y1plus' + str(a), 32))
        y2_set.append(z3.BitVec('y2plus' + str(a), 32))
        y3_set.append(z3.BitVec('y3plus' + str(a), 32))
        y_initial_outputs.append(z3.BitVec('y_baseplus' + str(a) + '_out', 32))
        y_initial_offset_outputs.append(z3.BitVecVal(outputs1[a], 32))
        # y_refreshed_states.append(z3.BitVec('y_refreshedplus' + str(a), 32))
        # y4_set.append(z3.BitVec('y4plus' + str(a), 32))
        # y5_set.append(z3.BitVec('y5plus' + str(a), 32))
        # y6_set.append(z3.BitVec('y6plus' + str(a), 32))
        # y_refreshed_outputs.append(z3.BitVec('y_refreshedplus' + str(a) + '_out', 32))
        # y_refreshed_offset_outputs.append(z3.BitVecVal(outputs2[a], 32))
    for a in range(624):
        y_initial_states.append(z3.BitVec('y_refreshedplus' + str(a), 32))
        y1_set.append(z3.BitVec('y4plus' + str(a), 32))
        y2_set.append(z3.BitVec('y5plus' + str(a), 32))
        y3_set.append(z3.BitVec('y6plus' + str(a), 32))
        y_initial_outputs.append(z3.BitVec('y_refreshedplus' + str(a) + '_out', 32))
        y_initial_offset_outputs.append(z3.BitVecVal(outputs2[a], 32))
    for a in range(1248):
        equations = [
            y1_set[a] == y_initial_states[a] ^ (z3.LShR(y_initial_states[a], 11)),
            y2_set[a] == y1_set[a] ^ ((y1_set[a] << 7) & 0x9d2c5680),
            y3_set[a] == y2_set[a] ^ ((y2_set[a] << 15) & 0xefc60000),
            y_initial_outputs[a] == y3_set[a] ^ (z3.LShR(y3_set[a], 18)),
            y_initial_offset_outputs[a] == z3.LShR(y_initial_outputs[a], offset),
        ]
        solver.add(equations)
    for a in range(624):
        equation = [
            y_initial_states[a + 624] == z3.If(((y_initial_states[a] & upper_mask) | (y_initial_states[(a+1)]
                                                                                           & lower_mask)) << 31 == 0,
                                   # If Thingy last bit == 0, states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[0]
                                   y_initial_states[(a + 397)] ^
                                   z3.LShR(((y_initial_states[a] & upper_mask) |
                                            (y_initial_states[(a+1)] & lower_mask)), 1),
                                   # If Thingy last bit != 1, states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[1]
                                   y_initial_states[(a + 397)]
                                   ^ z3.LShR(((y_initial_states[a] & upper_mask) |
                                              (y_initial_states[(a+1)] & lower_mask)), 1)
                                   ^ 0x9908b0df
                                   )
        ]
        solver.add(equation)
    print(solver.check())
    out = []
    for a in range(624):
        out.append(solver.model()[y_initial_states[a]].as_long())
    return out


def temper(input):
    # all funcs work as expected
    twisted = input ^ (input >> 11)
    twisted = twisted ^ ((twisted << 7) & 0x9d2c5680)
    twisted = twisted ^ ((twisted << 15) & 0xefc60000)
    twisted = twisted ^ (twisted >> 18)
    return twisted


def randint_emulator(states, range):
    size = range.bit_length()
    index = states[-1]
    while (temper(states[index]) >> (32-size)) >= range:
        index += 1
    number = temper(states[index]) >> (32-size)
    return number, index


def twist(states):
    matrix = [0, 0x9908b0df]
    new_states = []
    upper_mask = 0x80000000
    lower_mask = 0x7fffffff
    for idx, state in enumerate(states):
        y = (states[idx] & upper_mask) | (states[(idx + 1) % 624] & lower_mask)
        temp = states[(idx + 397) % 624] ^ (y >> 1) ^ matrix[y & 1]
        new_states.append(temp)
    return new_states


def single_twist(in1, in2, in3):
    matrix = [0, 0x9908b0df]
    upper_mask = 0x80000000
    lower_mask = 0x7fffffff
    y = (in1 & upper_mask) | (in2 & lower_mask)
    temp = in3 ^ (y >> 1) ^ matrix[y & 1]
    return temp


if __name__ == '__min__':
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
        state_values.append(untemper(output))
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
    print(further_output[:5])
    print(new_gen_further_output[:5])


if __name__ == '__main__':
    random.seed()
    a = random.getstate()
    cur_states = list(a[1])
    cur_states[624] = 0
    random.setstate((3, tuple(cur_states), None))
    output_set1 = []
    output_set2 = []
    for a in range(624):
        output_set1.append(random.getrandbits(31))
    print(f"Relevant states for 1st iter: \n{random.getstate()[1][0], random.getstate()[1][1], random.getstate()[1][397]}")
    first_iter_state = random.getstate()[1]
    for a in range(624):
        output_set2.append(random.getrandbits(31))
    print(f"Relevant states for 2nd iter: \n{random.getstate()[1][0]}")
    print(f"1st output in 2nd set = {output_set2[0]}")
    check = auto_z3_solver(output_set1, output_set2, 31)
    print(check)
    print(first_iter_state)
    count = 0
    for a in range(624):
        if check[a] == first_iter_state[a]:
            count += 1
    print(count)
    assert count == 624








