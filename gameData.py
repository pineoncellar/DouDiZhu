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

import OlivOS
import DouDiZhu.dataFiles as df
import DouDiZhu.gamePlay as gp

import random

ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # cards
cards_pile = []


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
    ):
        self.switch = switch
        self.player_list = player_list
        self.host_player = host_player
        self.process = process
        self.next_player = next_player
        self.last_cards = last_cards
        self.last_player = last_player
        self.host_cards = host_cards

    def gameInit(self, gid, plugin_event):
        card_pile = CardPile()
        card_pile.shuffle()

        # mix the player list
        random.shuffle(self.player_list)

        # draw player cards
        player1 = playerData(
            self.player_list[0][0], self.player_list[0][1], card_pile.draw_player_card()
        )
        player1.sort()
        df.setUserData(player1, player1.uid, gid)
        player2 = playerData(
            self.player_list[1][0], self.player_list[1][1], card_pile.draw_player_card()
        )
        player2.sort()
        df.setUserData(player2, player2.uid, gid)
        player3 = playerData(
            self.player_list[2][0], self.player_list[2][1], card_pile.draw_player_card()
        )
        player3.sort()
        df.setUserData(player3, player3.uid, gid)

        self.host_cards = card_pile.draw_host_card()
        self.last_player = player3.uid
        self.next_player = player1.uid
        self.process = 0

        # send cards message
        gp.sendCards(player1, plugin_event)
        gp.sendCards(player2, plugin_event)
        gp.sendCards(player3, plugin_event)

    def setHost(self, uid, gid):
        player_data = df.getUserData(uid, gid)
        player_data.incCards(self.host_cards)
        self.host_player = uid
        self.next_player = uid
        self.process = 1

    def _pass(self):
        for player in self.player_list:
            if self.next_player == player[0]:
                i = self.player_list.index(player)  # get index
                if i == 2:
                    self.next_player = self.player_list[0][0]
                else:
                    self.next_player = self.player_list[i + 1][0]
                break


class playerData:
    def __init__(self, uid, name, cards: list):
        self.uid = uid
        self.name = name
        self.cards = cards

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
        tmp_card_list = self.cards

        for card in cards:
            if card in tmp_card_list:
                tmp_card_list.remove(card)
            else:
                return False
        return True


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
        value = 13
    elif card == "D":
        value = 13

    return value
