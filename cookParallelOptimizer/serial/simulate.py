for sim in range(num_sims):
    s = simulate_game_serial(lineup, sim, print_level=0)    
    scores[sim] = s

scores = scores.ravel()
scores = scores[:sample_size*reps]
scores = scores.reshape(sample_size,reps)