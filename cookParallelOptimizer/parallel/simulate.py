simulate_game_parallel(cuda.InOut(scores), cuda.In(lineup), rbi_gpu, T_gpu, outs_gpu, rand_gpu, rand_start_gpu, np.uint32(num_rands), np.uint8(print_level), block=blockDims, grid=gridDims, shared=0)

#simulate_game_parallel(scores_gpu, rbi_gpu, T_gpu, outs_gpu, lineup_gpu, rand_gpu, rand_start_gpu, np.uint32(num_rands), np.uint8(print_level), block=blockDims, grid=gridDims, shared=0)
#scores = scores_gpu.get()


scores = scores.ravel()
scores = scores[:sample_size*reps]
scores = scores.reshape(sample_size,reps)