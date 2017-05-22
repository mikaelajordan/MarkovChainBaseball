from helper.setup import *
from helper.pycuda_setup import *

#print_level = 1
#gridDims = (2**6,1,1)
#blockDims = (1024,1,1)
#gridDims = (1,1,1)
#blockDims = (1,1,1)


#from make_matrices import *
#from simulation_setup import *

threadDims = np.concatenate([gridDims,blockDims]).astype('uint32')
num_threads = threadDims.prod()

num_rands = 2**24
rand = np.random.rand(num_rands).astype('float32')
rand_gpu = togpu(rand,'float32')

rand_start = np.random.randint(num_rands,size=threadDims).astype('uint32')
rand_start_gpu = togpu(rand_start,'uint32')

scores = np.zeros(threadDims,dtype='uint16')

#Randomly selects 9 batters
num_players = players.shape[0]
lineup = np.random.permutation(np.arange(num_players))[:9]
lineup_gpu = togpu(lineup,'uint8')


func(cuda.InOut(scores), rbi_gpu, T_gpu, outs_gpu, lineup_gpu, rand_gpu, rand_start_gpu, np.uint32(num_rands), np.uint8(print_level), block=blockDims, grid=gridDims, shared=0)