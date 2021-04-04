from random import shuffle


num_to_repr = { 14: 'A', 11: 'J', 12: 'Q', 13: 'K' }
suit_to_repr = { 'S': '♠', 'H' : '♥', 'D' : '♦' , 'C' : '♣' }

class Card:

    def __init__(self, number, suit):

        # Number 1 - 13
        self.number = number

        # Suit = [H, D, C, S]
        self.suit = suit


    def __repr__(self):
        num = num_to_repr[self.number] if self.number in num_to_repr else self.number
        suit_repr = suit_to_repr[self.suit]
        return str(num) + suit_repr

    def __gt__(self, other_card):
        return self.number > other_card.number

    def __eq__(self, other_card):
        return self.number == other_card.number


class Deck:

    def __init__(self):
        self.cards = []

        for n in range(2, 15):
            for s in ['H', 'D', 'C', 'S']:
                card = Card(n,s)
                self.cards.append(card)

    def shuffle(self):
        shuffle(self.cards)

    def drawOne(self):
        return self.cards.pop(0)
    
    def draw(self, N):
        drawn_cards = self.cards[:N]
        self.cards = self.cards[N:]
        return drawn_cards


if __name__ == "__main__":

    deck = Deck()
    deck.shuffle()

    hand = [deck.drawOne(), deck.drawOne()]

    print(hand)



