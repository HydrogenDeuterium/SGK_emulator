import enum
from collections import deque, namedtuple
from random import shuffle
from copy import deepcopy
from typing import Sequence


class Suit(enum.Enum):
    Hearts = "红桃♥"
    Spades = "黑桃♠"
    Clubs = "草花♣"
    Diamonds = "方片♦"


class Card(namedtuple('Card', ['name', 'suit', 'number', 'type'])):
    name: str
    suit: Suit
    
    def __contains__(self, name):
        return name in self.name
    
    def __repr__(self):
        num = '_ A 2 3 4 5 6 7 8 9 10 J Q K'.split()
        return f'<{self.suit.value}{num[self.number]} 的 “{self.name}”>'
    
    def effect(self, table, target):
        match self.name:
            case '杀':
                target.need_miss()
            case '决斗':
                target.need_kill()
            case '火攻':
                return target.show_one()
            case '兵粮寸断':
                judge = table.deal()
                if judge.suit != Suit.Clubs:
                    target.status = 2
        table.drop(self)


# 牌堆
class Table:
    def __init__(self, cards: list[Card]):
        # 字段定义
        self.touch = None
        self._count = 0
        self.drops = []
        
        # 初始牌堆
        self.cards = tuple(cards)
        
        self.add_deck()
    
    def add_deck(self):
        assert not self.touch
        if self._count:
            print(f'[WARNING]牌堆已用尽，重新增加第{self._count}组新牌')
        self.touch = deque(self.drops)
        self._count += 1
    
    def shuffle(self):
        shuffle(self.touch)
    
    def deal(self) -> Card:
        if not self.touch:
            if self.drops:
                self.touch = deque(self.drops)
                self.drops.clear()
            else:
                self.touch = deque(self.cards)
            self.shuffle()
        return self.touch.pop()
    
    def deal_many(self, num):
        return [self.deal() for _ in range(num)]
    
    def drop(self, card: Card):
        self.drops.append(card)
    
    def drop_many(self, cards: Sequence[Card]):
        self.drops.extend(cards)


if __name__ == "__main__":
    import toml
    
    card_info = toml.load('deck.toml')
    cards = []
    for ctype, cnames in card_info.items():
        for cname, suits in cnames.items():
            for suit, numbers in suits.items():
                for number in numbers:
                    cards.append(Card(cname, getattr(Suit, suit), number, ctype))
    pass
