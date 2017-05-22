from helper.setup import *

#2 lines below are equivalent
baserunners = it.chain.from_iterable(it.combinations(range(1,4), r) for r in range(4))
#baserunners = (x for r in range(4) for x in it.combinations(range(1,4), r))

states = it.product(range(3),baserunners)
states = pd.DataFrame.from_records(states,columns=["outs","baserunners"])
states['num_baserunners'] = states['baserunners'].apply(len)

#Handle runs scored during inning ending play
end = states.iloc[:4].copy()
for runs in range(4):
    end.ix[runs] = [3,runs,runs]
states = states.append(end,ignore_index=True)

header = states.iloc[:,:2]
states['o+b'] = states['outs'] + states['num_baserunners']

#rbis on play = (o+b)_before - (o+b)_after + 1
rbi = np.subtract.outer(states['o+b'],states['o+b'])+1
rbi = pd.DataFrame(rbi,index=header,columns=header)

#Play invalid if negative rbi's
rbi_valid = rbi >= 0
#Play invalid if num outs decreases.  Two lines below are equivalent.
outs_valid = np.less_equal.outer(states['outs'],states['outs'])
#outs_valid = np.subtract.outer(states['outs'],states['outs']) <= 0

valid = rbi_valid & outs_valid
#If play invalid, set entry in rbi matrix to -1
rbi[~valid] = -1
#Drop ROWS for inning ending plays because play can not BEGIN in such a state.
#Keep COLUMNS because play can END in such a state.
rbi = rbi.iloc[:-4]
#display(rbi)

def margins(df):
    #Appends row and column totals
    df = pd.DataFrame(df)
    col_sums = df.sum(axis=0)
    df.loc['TOTAL'] = col_sums
    row_sums = df.sum(axis=1)
    df['TOTAL'] = row_sums
    return df
valid = rbi>=0
#display(margins(valid))


#Define player types and their transition matrices.
player_types = pd.DataFrame(index = ['power','contact','speed','mendoza'])

#Fill with random numbers
#def make_rand_T():
#    T = rbi.copy() #So that row and column size and headers are copied
#    T[:] = np.random.rand(*T.shape) #fill with random
#    T[~valid]=0 #Set prob of invalid plays to 0
#    return T.div(T.sum(axis=1), axis=0) #normalize rows to sum to 1
#player_types['T'] = [make_rand_T() for d in player_types.index]
#display(margins(player_type.ix['power','T']))


#Make crude "typical" matrix - roughly 30% chance of hit, 70% of out.
#d_outs is number of outs on the play
d_outs = np.subtract.outer(states['outs'],states['outs']).T
d_outs = pd.DataFrame(d_outs,index=header,columns=header)
d_outs = d_outs.ix[:-4,:]
d_outs[~valid] = -1

#f makes 30% chance of hit, 70% chance of out.  It divides these probs equally among all 
#possible ways to make hit or out.
def f(r):
    #c counts all ways to make 0, 1, 2, or 3 outs during this AB.
    c = r.value_counts()
    #d is total prob of making 0, 1, 2, or 3 outs during this AB.
    #Note d[-1]=0 (impossible) and d[3]=0 (triple plays are extremely rare)
    d = c*0
    d[0] = 3
    d[1] = 7
    #d[2] = 1/11 if a double play is possble.
    try:
        if c.ix[2] > 0:
            d[2] = 1
    except:
        pass    
    d /= d.sum()
    #d is either [0/10, 3/10, 7/10, 0/10, 0/10] or [0/11, 3/11, 7/11, 1/11,0/11]
    #is distributes these probs equally among the ways to get there.
    e = (d/c).fillna(0)
    return r.replace(e)
T = d_outs.apply(f,axis=1)
player_types['T'] = [T.copy() for d in player_types.index]



#Make our team's roster
players = pd.DataFrame(index = ['Adam','David','Joseph','Mary','Mikaela','Parker','Archie',
                               'Taylor','Bobby','Wesley','Chad','Jeanne','Gerardo','Richard'])
def make_rand_coefs():
    #Each player is a linear combination of the player types above.  For now, random.
    c = np.random.rand(player_types.shape[0])
    return c/c.sum() #normalize so coefs sum to 1
players['coefs'] = [make_rand_coefs() for p in players.index]

#Each player has a unique T which is a linear combination of the player type T's
#using that player's coefs as weights.
players['T'] = [players.ix[p,'coefs'].dot(player_types['T']).values for p in players.index]
#display(margins(player.ix['David','T']))

os.makedirs('./data', exist_ok=True) 
states.to_csv('./data/states.csv',index=True,header=True)
rbi.to_csv('./data/rbi.csv',index=True,header=True)
players.to_json('./data/players.json',orient='index')

print("Matrix creation complete")