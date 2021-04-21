hands = ['32o', '52o', '53o', '62o', '42o', '73o', '52s', '72o', '63o', '43o', '64o', '32s', '54o', '72s', '42s', '82o', '85o', '74o', '92o', '74s', '83o', '65o', 'T3o', 'T2o', '53s', '75o', '75s', '64s', '93s', '95s', '63s', 'T3s', '62s', '93o', '94o', 'T2s', '95o', 'J2s', '76o', '22o', '84o', 'J4o', '86s', 'Q2o', '82s', '83s', 'T5o', 'J2o', '92s', '65s', '87o', '94s', '43s', 'T6o', '85s', '96o', '54s', '73s', 'T6s', 'Q3o', '86o', 'J3o', '96s', 'Q2s', '76s', 'T7s', '87s', 'J3s', '97o', 'T4o', 'J8o', 'J6o', 'J5o', '98o', '84s', 'J7o', 'K2s', 'T4s', 'K2o', 'Q5o', 'T7o', 'T8o', 'T5s', 'J4s', '33o', 'Q6o', 'J5s', 'T9s', 'Q4s', 'K3o', 'Q3s', 'K4o', 'J8s', 'J9s', 'K5o', 'K6s', 'K4s', 'Q5s', 'Q4o', 'A5o', 'T9o', '97s', 'Q7o', 'A3o', 'T8s', 'A6s', 'Q7s', 'J6s', 'K8o', 'A2o', 'K7o', 'Q9o', 'J9o', '55o', 'K6o', 'QJo', '98s', 'K3s', 'A4s', 'JTo', 'K8s', 'A2s', 'A5s', 'KJs', 'J7s', '44o', 'A4o', 'Q8o', 'Q9s', 'QTo', 'A8o', 'Q8s', 'K9o', 'A6o', 'A9o', 'K9s', 'A9s', 'K7s', 'A7o', 'KTo', 'KJo', 'Q6s', 'A3s', 'JTs', 'AJo', 'QTs', 'ATo', 'AQs', 'A7s', 'K5s', 'KQs', 'KTs', 'KQo', 'AQo', '88o', 'ATs', '77o', '66o', 'A8s', 'AJs', 'QJs', 'AKo', 'AKs', '99o', 'TTo', 'JJo', 'QQo', 'KKo', 'AAo', ]

def rank_hand(hand):
    return (hands.index(hand) + 1) / 169
    
if __name__ == "__main__":

    print('Lenght: ', len(hands))
    print(hands.index('T9s') / len(hands))