# -*- encoding: utf-8 -*- #
"""
██████╗  ██╗ ███╗   ██╗ ███████╗
██╔══██╗ ██║ ████╗  ██║ ██╔════╝
██████╔╝ ██║ ██╔██╗ ██║ █████╗  
██╔═══╝  ██║ ██║╚██╗██║ ██╔══╝  
██║      ██║ ██║ ╚████║ ███████╗
╚═╝      ╚═╝ ╚═╝  ╚═══╝ ╚══════╝
@Author    :   地窖上的松
@Contact   :   dijsds@163.com
@License   :   CC BY-NC-SA 4.0
@Desc      :   游戏数据类与操作
"""


import random

ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # cards
cards_pile = []

# [id, name, model]
ai_data_list = [
    [100, "困难人机", "WP"],
    [200, "中级人机", "252150400"],
    [300, "简单人机", "170048000"],
]


class CardPile:
    def __init__(self):
        self.cards = self._generate_deck()  # all cards

    def _generate_deck(self):
        cards = []
        for rank in ranks:
            for i in range(0, 4):
                cards.append(rank)
        cards.append("X")
        cards.append("D")
        return cards

    def shuffle(self):
        random.shuffle(self.cards)  # mix cards

    def draw_host_card(self):
        cards = []
        for i in range(0, 3):
            cards.append(self.cards.pop())
        return cards

    def draw_player_card(self):
        cards = []
        for i in range(0, 17):
            cards.append(self.cards.pop())
        return cards


class gameData:

    def __init__(
        self,
        switch: bool = True,
        player_list: list = [],  # [uid,name]
        host_player=None,
        process: "int|None" = None,
        next_player=None,
        last_cards: "list|None" = None,
        last_player=None,
        host_cards: "list|None" = None,
        ai_player_number: int = 0,
    ):
        self.switch = switch
        self.player_list = player_list
        self.host_player = host_player
        self.process = process
        self.next_player = next_player
        self.last_cards = last_cards
        self.last_player = last_player
        self.host_cards = host_cards
        self.ai_player_number = ai_player_number

    def gameDataInit(self, card_pile, player1, player3):
        self.host_cards = card_pile.draw_host_card()
        self.last_player = [player3.uid, player3.name]
        self.next_player = [player1.uid, player1.name]
        self.process = 0

    def setHostData(self, uid, name):
        self.host_player = [uid, name]
        self.next_player = [uid, name]
        self.process = 1

    def _pass(self):
        for i in range(0, 3):
            if self.next_player == self.player_list[i]:
                if i == 2:
                    self.next_player = self.player_list[0]
                else:
                    self.next_player = self.player_list[i + 1]
                break


class playerData:
    def __init__(self, uid, name, cards: list):
        self.uid = uid
        self.name = name
        self.cards = cards
        self.role = None

    # decrease cards
    def decCards(self, cards: list):
        for card in cards:
            self.cards.remove(card)
        self.sort()

    # increase cards
    def incCards(self, cards: list):
        for card in cards:
            self.cards.append(card)
        self.sort()

    # sort cards
    def sort(self):
        self.cards = sorted(self.cards, key=getCardValue)

    # check if player has these cards
    def check_cards(self, cards: list):
        tmp_card_list = []
        in_list = True

        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
                tmp_card_list.append(card)
            else:
                in_list = False
                break

        for card in tmp_card_list:
            self.cards.append(card)
        self.sort()
        return in_list

    def setRole(self, role: int):
        self.role = role


def getCardValue(card: str):
    value = 0
    if card in ["3", "4", "5", "6", "7", "8", "9", "10"]:
        value = int(card) - 2
    elif card == "J":
        value = 9
    elif card == "Q":
        value = 10
    elif card == "K":
        value = 11
    elif card == "A":
        value = 12
    elif card == "2":
        value = 13
    elif card == "X":
        value = 14
    elif card == "D":
        value = 15

    return value
