from helper.pycuda_setup import *

scores_gpu = togpu(scores,'uint16')
outs_gpu = togpu(states['outs'],'uint8')
rbi_gpu = togpu(rbi,'uint8')
T_gpu = togpu(T,'float32')

num_rands = 2**24
rand = np.random.rand(num_rands).astype('float32')
rand_gpu = togpu(rand,'float32')
rand_start = np.random.randint(num_rands,size=threadDims).astype('uint32')
rand_start_gpu = togpu(rand_start,'uint32')

mod = SourceModule("""
    #include <stdio.h>
    __global__ void simulate_game_parallel_gpu(ushort *scores, char *lineup, char *rbi, float *T, char *outs, float *rand, uint *rand_start, uint num_rands, char print_level)
    {
        const uint blockId      = blockIdx.z * (gridDim.y * gridDim.x) 
                                + blockIdx.y * (gridDim.x)
                                + blockIdx.x;
                           
        const uint threadIdLoc  = threadIdx.z * (blockDim.y * blockDim.x)
                                + threadIdx.y * (blockDim.x)
                                + threadIdx.x;
                           
        const uint threadIdGlob = blockId * (blockDim.z * blockDim.y * blockDim.x)
                                + threadIdLoc;

        const char *div1 = "***********************************************************************************************\\n";
        const char *div2 = "###############################################################################################\\n";

        char inning = 0;
        ushort total_ABs = 0;
        char AB_idx = 0;
        char state_in = 0;
        char state_out = 0;
        ushort score = 0;
        uint T_idx = 0;
        ushort batter_idx = lineup[AB_idx];
        const uint n_rows = 24;
        const uint n_cols = 28;
        const uint r_idx_max = num_rands;
        uint r_idx = rand_start[threadIdGlob];
        float r = rand[r_idx];
        float prob = 0;

        for(inning = 1; inning <= 9; inning++){
            state_in = 0;
            
            if(print_level >= 2){
                printf("%sSim %d, thr %d.%d, BEGIN INNING %d, runs %d, outs %d, AB %d, bat %d, s_in %d\\n", div1, threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_in], AB_idx, batter_idx, state_in);
                if(print_level >= 3){printf("\\n");}
            }
            
            while(outs[state_in] < 3){
                state_out = 0;
                T_idx = batter_idx*n_rows*n_cols + state_in*n_cols;
                r = rand[r_idx];

                if(print_level >= 3){
                    printf("Sim %d, thr %d.%d, inn %d, runs %d, outs %d, BEGIN AB %d, bat %d, s_in %d, r=%f\\n", threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_in], AB_idx, batter_idx, state_in, r);
                }

                while(r > 0){
                    prob = T[T_idx];
                    r -= prob;
                    
                    if(print_level >= 4){
                        printf("Sim %d, thr %d.%d, inn %d, runs %d, outs %d, AB %d, bat %d, s_out %d, prob=%f, r_left=%f\\n", threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_in], AB_idx, batter_idx, state_out, prob, r);
                    }
                    T_idx++;
                    state_out++;
                }
                state_out--;
                score += rbi[state_in*n_cols + state_out];
                state_in = state_out;

                if(print_level >= 3){
                    printf("Sim %d, thr %d.%d, inn %d, runs %d, outs %d, END AB %d, bat %d, s_out %d, r_left=%f\\n\\n", threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_out], AB_idx, batter_idx, state_out, r);
                }
                total_ABs++;
                AB_idx++; AB_idx %= 9;
                r_idx += 17; r_idx %= r_idx_max;
                batter_idx = lineup[AB_idx];
            }
            
            if(print_level >= 2){
                printf("Sim %d, thr %d.%d, END INNING %d, runs %d, outs %d, AB %d, bat %d, s_in %d\\n%s", threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_out], AB_idx, batter_idx, state_out, div1);
            }
        }
        inning--;
        if(print_level >= 1){
            printf("%sSim %d, thr %d.%d, END GAME, inn %d, runs %d, outs %d, AB %d, bat %d, s_out %d, total ABs %d\\n%s", div2, threadIdGlob, blockId, threadIdLoc, inning, score, outs[state_out], AB_idx, batter_idx, state_out, total_ABs, div2);
        }
        scores[threadIdGlob] = score;
        rand_start[threadIdGlob] = (r_idx + 193) % r_idx_max;
    }
""")
simulate_game_parallel = mod.get_function("simulate_game_parallel_gpu")
print("Simulation setup complete")