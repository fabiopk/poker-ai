from Deck import Card, Deck
from collections import Counter

HAND_STRENGHT = {
    'STRAIGHT_FLUSH' : 10,
    'FOUR_OF_A_KIND' : 9,
    'FULL_HOUSE' : 8,
    'FLUSH' : 7,
    'STRAIGHT' : 6,
    'TREE_OF_A_KIND' : 5,
    'TWO_PAIR' : 4,
    'PAIR' : 3,
    'HIGH_CARD' : 2,
}

class Hand:

    def __init__(self, hand):
        self.hand = hand
        self.suits = Counter([c.suit for c in hand])
        self.numbers = Counter([c.number for c in hand])
        self.best_hand = []
        self.kickers = []
        self.type = None
        self.criterion = None
        self.resolve()

    def __repr__(self):
        return f"{self.type} crit: {self.criterion} kickers: {self.kickers} -- {self.best_hand}"

    def resolve(self):
        
        detected = self.detectFourOfAKind()
        if not detected:
            detected = self.detectFullHouse()
        if not detected:
            detected = self.detectFlush()
        if not detected:
            detected = self.detectTreeOfAKind()
        if not detected:
            detected = self.detectStraight()
        if not detected:
            detected = self.detectTwoPair()
        if not detected:
            detected = self.detectPair()
        if not detected:
            detected = self.HighCard()

    def detectStraightFlush(self):
        
        suit, amount = self.suits.most_common(1)[0]

        if amount < 5:
            return False

        ordered = sorted([c for c in self.hand if c.suit == suit], reverse=True)
        combo = 1
        highest = ordered[0].number
        previous = ordered[0].number
        best_hand = [ordered[0]]

        for card in ordered[1:]:
            if card.number == previous - 1 or (previous == 2 and combo == 4 and card.number == 14):
                combo += 1
                best_hand.append(card)
                if combo == 5:
                    break
            elif card.number == previous:
                continue
            else:
                highest = card.number
                combo = 1
                best_hand = [card]
            previous = card.number

        if combo < 5:
            return False

        self.best_hand = best_hand
        self.kickers = []
        self.type = 'STRAIGHT_FLUSH'
        self.criterion= highest

        return True
            
    def detectFlush(self):

        suit, amount = self.suits.most_common(1)[0]

        if amount < 5:
            return False

        best_hand = sorted([c for c in self.hand if c.suit == suit], reverse=True)[:5]

        self.best_hand = best_hand
        self.kickers = best_hand
        self.type = 'FLUSH'
        self.criterion = 0 

        return True

    def detectFullHouse(self):

        triple, double = self.numbers.most_common(2)
        number_3, amount_3 = triple
        number_2, amount_2 = double

        if amount_3 < 3 or amount_2 < 2:
            return False
        
        triple = max([num for num in self.numbers if self.numbers[num] >= 3])
        double = max([num for num in self.numbers if (self.numbers[num] >= 2 and num != triple)])
        best_hand = [c for c in self.hand if c.number == triple][:3] + [c for c in hand if c.number == double][:2]
        
        self.best_hand = best_hand,
        self.kickers = [],
        self.type = 'FULL_HOUSE',
        self.criterion = triple * 100 + double 

        return True

    def detectTwoPair(self):

        pair_1, pair_2 = self.numbers.most_common(2)
        number_p1, amount_p1 = pair_1
        number_p2, amount_p2 = pair_2

        if amount_p1 < 2 or amount_p2 < 2:
            return False
        
        num_pair_1 = max([num for num in self.numbers if self.numbers[num] >= 2])
        num_pair_2 = max([num for num in self.numbers if (self.numbers[num] >= 2 and num != num_pair_1)])

        kicker =[max([c for c in self.hand if c.number not in [pair_1, pair_2]])]
        best_hand = [c for c in self.hand if c.number == num_pair_1][:2] + [c for c in self.hand if c.number == num_pair_2][:2] + kicker

        self.best_hand = best_hand
        self.kickers = kicker
        self.type = 'TWO_PAIR'
        self.criterion = num_pair_1 * 100 + num_pair_2 

        return True

    def detectFourOfAKind(self):

        number, amount = self.numbers.most_common(1)[0]

        if amount < 4:
            return False

        kickers = sorted([c for c in self.hand if c.number != number], reverse=True)[:1]
        best_hand =  [c for c in hand if c.number == number] + kickers

        self.best_hand = best_hand
        self.kickers = kickers
        self.type = 'FOUR_OF_A_KIND'
        self.criterion = number 

        return True

    def detectTreeOfAKind(self):

        number, amount = self.numbers.most_common(1)[0]

        if amount < 3:
            return False

        kickers = sorted([c for c in self.hand if c.number != number], reverse=True)[:2]

        best_hand =  [c for c in self.hand if c.number == number][:3] + kickers

        self.best_hand = best_hand
        self.kickers = kickers
        self.type = 'TREE_OF_A_KIND'
        self.criterion = number 

        return True
    
    def detectPair(self):

        number, amount = self.numbers.most_common(1)[0]

        if amount < 2:
            return False

        kickers = sorted([c for c in self.hand if c.number != number], reverse=True)[:3] 
        best_hand = [c for c in self.hand if c.number == number][:2] + kickers

        self.best_hand = best_hand
        self.kickers = kickers
        self.type = 'PAIR'
        self.criterion = number 

        return True

    def detectStraight(self):

        ordered = sorted(self.hand, reverse=True)
        combo = 1
        highest = ordered[0].number
        previous = ordered[0].number
        best_hand = [ordered[0]]

        for card in ordered[1:]:
            if card.number == previous - 1 or (previous == 2 and combo == 4 and card.number == 14):
                combo += 1
                best_hand.append(card)
                if combo == 5:
                    break
            elif card.number == previous:
                continue
            else:
                highest = card.number
                combo = 1
                best_hand = [card]
            previous = card.number

        if combo < 5:
            return False

        self.best_hand = best_hand
        self.kickers = []
        self.type = 'STRAIGHT'
        self.criterion = highest 

        return True

    def HighCard(self):

        kickers = sorted(self.hand, reverse=True)[:5]

        self.best_hand = kickers
        self.kickers = kickers
        self.type = 'HIGH_CARD'
        self.criterion = 0 

        return True

    def __gt__(self, other_hand):

        if HAND_STRENGHT[self.type] > HAND_STRENGHT[other_hand.type]:
            return True
        elif HAND_STRENGHT[self.type] == HAND_STRENGHT[other_hand.type]:
            if self.criterion > other_hand.criterion:
                return True
            elif self.criterion == other_hand.criterion:
                for i in range(len(self.kickers)):
                    if self.kickers[i] != other_hand.kickers[i]:
                        return self.kickers[i] > other_hand.kickers[i]
                return False
            else:
                return False
        else:
            return False

        return sel

    def __eq__(self, other_hand):
        sameType = HAND_STRENGHT[self.type] == HAND_STRENGHT[other_hand.type]
        sameCriteria = self.criterion == other_hand.criterion
        sameKickers = all([self.kickers[i] == other_hand.kickers[i] for i in range(len(self.kickers))])
        return sameType and sameCriteria and sameKickers


if __name__ == '__main__':
    deck = Deck()
    deck.shuffle()

    table = deck.draw(5)
    h1 = deck.draw(2)
    h2 = deck.draw(2)

    h1 = [Card(4, 'C'), Card(7, 'S')]
    h2 = [Card(7, 'H'), Card(12, 'C')]
    table = [Card(10, 'C'), Card(5, 'H'), Card(7, 'C'), Card(14, 'S'), Card(11, 'S') ]    
    print('Player 1', h1)
    print('Player 2', h2)
    print('Table: ', table)
    
    hand1 = Hand(table + h1)
    hand2 = Hand(table + h2)

    print('Hand1', hand1)
    print('Hand2', hand2)

    if hand1 > hand2:
        print('Hand 1 is better')
    elif hand2 > hand1:
        print('Hand 2 is better')
    else:
        print('same hand')