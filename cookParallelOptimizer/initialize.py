from helper.setup import *

states = pd.read_csv('./data/states.csv',index_col=0)
players = pd.read_json('./data/players.json',orient='index')
rbi = pd.read_csv('./data/rbi.csv',index_col=0)

valid = rbi >= 0
rbi[~valid] = 0
rbi = rbi.values
outs = states['outs'].values.astype('uint8')
T = np.stack(players['T']).astype('float32')

threadDims = np.concatenate([gridDims,blockDims]).astype('uint')
num_sims = threadDims.prod()
scores = np.zeros(num_sims,dtype='uint16')
reps = np.floor(num_sims/sample_size).astype('uint')
if(reps == 0):
    print("Total number of simulations is less than desired sample size.  Reducing sample size.")
    reps = 1
    sample_size = num_sims
sample_size = np.uint(sample_size)
reps = np.uint(reps)