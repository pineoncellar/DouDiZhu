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
@Desc      :   游戏数据类的定义, 与游戏初始化函数
"""

import random
import OlivOS
import dataFiles as df

ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "J", "Q", "K"]  # cards
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
        player_list: list = [],  # 存放列表的列表
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

    def gameInit(self, gid):
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
        self.host_player = player1.uid
        self.process = 0
        self.next_player = player1.uid

        # send cards message
        sendCards(player1)
        sendCards(player2)
        sendCards(player3)

    def setHost(name: str):
        pass


class playerData:
    def __init__(self, uid, name, cards: list):
        self.uid = uid
        self.name = name
        self.cards = cards

    def play(self, cards: list):
        pass

    def getCards(self, cards: list):
        pass

    # sort cards
    def sort(self):
        pass


def sendCards(player_data: playerData, plugin_event=OlivOS.API.Event):
    cards = player_data.cards
    message = "你的手牌是: " + " ".join(cards)
    uid = player_data.uid
    plugin_event.send("private", uid, message)
