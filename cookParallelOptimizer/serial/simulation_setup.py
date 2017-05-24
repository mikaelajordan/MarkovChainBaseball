def simulate_game_serial(lineup, sim, print_level=0):
    div_len = 95
    inning = 0
    total_ABs = 0
    AB_idx = 0
    state_in = 0
    state_out = 0
    score = 0
    batter_idx = lineup[AB_idx];

    for inning in range(1,10):
        state_in = 0;

        if(print_level >= 2):
            print("*"*div_len)
            print("Sim %d, START OF INNING %d, runs %d, outs %d, AB %d, bat %d, s_in %d"
                  %(sim, inning, score, outs[state_in], AB_idx, batter_idx, state_in))
            if(print_level >= 3):
                print()

        while(outs[state_in] < 3):
            state_out = 0            
            r = np.random.rand()

            if(print_level >= 3):
                print("Sim %d, inn %d, runs %d, outs %d, AB %d, bat %d, s_in %d, r = %f"
                      %(sim, inning, score, outs[state_in], AB_idx, batter_idx, state_in, r))

            while(r > 0):
                prob = T[batter_idx, state_in, state_out]
                r -= prob
                if(print_level >= 4):
                    print("Sim %d, inn %d, runs %d, outs %d, AB %d, bat %d, s_out %d, prob=%f, r_left=%f"
                          %(sim, inning, score, outs[state_in], AB_idx, batter_idx, state_out, prob, r))
                state_out += 1
            state_out -= 1
            score += rbi[state_in, state_out]
            state_in = state_out
            
            if(print_level >= 3):
                print("Sim %d, inn %d, runs %d, outs %d, AB %d, bat %d, s_out %d, r_left = %f\n"
                      %(sim, inning, score, outs[state_out], AB_idx, batter_idx, state_out, r))

            total_ABs += 1
            AB_idx += 1
            AB_idx %= 9
            batter_idx = lineup[AB_idx]
            
        
        if(print_level >= 2):
            print("Sim %d, END OF INNING %d, runs %d, outs %d, AB %d, bat %d, s_out %d"
                  %(sim, inning, score, outs[state_out], AB_idx, batter_idx, state_out))
            print('*'*div_len)

    if(print_level >= 1):
            print('#'*div_len)
            print("Sim %d, END OF GAME, inning %d, FINAL SCORE %d, outs %d, AB %d, bat %d, state_out %d, total ABs %d"
                  %(sim, inning, score, outs[state_out], AB_idx, batter_idx, state_out, total_ABs))            
            print('#'*div_len)        

    return score
print("Simulation setup complete")