from __future__ import annotations
import random
from enum import Enum
from functools import lru_cache

from card import Card, Table


class Hand(list[Card]):
    def __init__(self, game: Table):
        super().__init__()
        self.extend(game.deal_many(4))
        self.game = game
    
    def deal(self):
        self.append(self.game.deal())
    
    def touch(self, num=2):
        self.extend(self.game.deal_many(num))
    
    # def remove(self, card):
    #     self.remove(card)
    
    def drop(self):
        # TODO
        pass
    
    @lru_cache
    def search(self, keyword):
        return [i for i in self if keyword in i.name]
    
    def count(self, key):
        return len(self.search(key))


class S(Enum):
    NORMAL = 0
    FLIPPED = 1
    BAN_TOUCH = 2


class BaseSolder:
    def __init__(self, name, health, game: Table):
        self.weapon = None
        self.guard = None
        self.name = name
        self.max_health = health
        self.health = health
        self.game = game
        
        self.status = S.NORMAL
        # 判定区
        self.judge_areas: list[Card] = []
        
        self.hand = Hand(self.game)
    
    def set_weapon(self, weapon):
        if self.weapon:
            self.game.drop(self.weapon)
        self.weapon = weapon
    
    def set_guard(self, guard):
        if self.guard:
            self.game.drop(self.guard)
        self.guard = guard
    
    def touch(self):
        self.hand.touch()
    
    # False 代表跳过回合
    def start(self):
        if self.status == S.FLIPPED:
            self.status = S.NORMAL
            return False
        return True
    
    def judge(self):
        j = self.judge_areas
        for i in reversed(j):
            i.effect(self.game, target=self)
            
            j.remove(i)
            self.game.drop(i)


class Solder:
    def __init__(self, name, health, deck):
        self.name = name
        self.max_health = health
        self.health = health
        self.deck = deck
        self.judge_areas = []
        self.hand_cards = {
            '杀':  [],
            '南':  [],
            '万':  [],
            '闪':  [],
            '桃':  [],
            '酒':  [],
            '拆':  [],
            '防具': [],
            '武器': [],
            '其他': [],
        }
        
        self.weapon: Card = None
        self.guard: Card = None
    
    def touch(self):
        card = self.deck.get()
        for keys in self.hand_cards:
            # 有点问题好像
            if keys in card.name:
                self.hand_cards[keys].append(card)
    
    def loop(self, enemy: Solder):
        if self.health < 0:
            raise AssertionError(f'{self.name} 死了。')
        self.hand_cards += [self.deck.get()] * 2
        self.action(enemy)
        self.drop()
    
    def action(self, enemy):
        pass
    
    def drop(self):
        while sum(len(type) for type in self.hand_cards.values()) > self.max_health:
            card = random.choice(self.hand_cards)
            self.deck.drop(card)


class SimpleAI(Solder):
    def action(self, enemy):
        kills = tuple(card for card in self.hand_cards if '杀' in card.name)
        if kills < 2 * enemy.health:
            return
        
        others = (card for card in self.hand_cards if '杀' not in card.name)
        for card in others:
            if "连弩" in self.weapon.name:
                gun = card
                self.hand_cards.remove(gun)
                self.set_weapon(gun)
                break
        if "连弩" in self.weapon.name:
            pass
