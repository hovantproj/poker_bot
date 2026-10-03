Kento: evcalc.py
- use the function calc_ev(hand, board)
- hand, board must be in the form ['Ac', '1d'], ['Qh', 'Ts', '4c'] etc
- The calc_ev function will output a numpy array of the expected values (probability * hand strength) for each type of hand
- index 0 is for royal flush and last index is for high card 

Philo: making main.py 
- determines optimal action using ev and player behaviour stuff

Hovan: player behaviour
- logs players' action
- can figure out when a player has a strong/weak hand with enough trials
- predict other's moves and return optimal move

Lucas: Help philo (the docs are very confusing)