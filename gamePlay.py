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
@Desc      :   游戏进行阶段
"""

import dataFiles as df
import OlivOS
import gameData as gd
import main


def exclude(
    group_data: gd.gameData,
    uid,
    plugin_event: OlivOS.API.Event,
):
    if group_data.process == 0:
        if not group_data.switch:  # group switch
            return True
        for player in group_data.player_list:  # check player list
            if uid == player[0]:
                break
        else:
            main.replyMsg("ni bu zai you xi zhong", plugin_event)
            return True
        if uid == group_data.next_player:  # check next player
            pass
        else:
            main.replyMsg("现在是" + group_data.next_player + "的回合喔", plugin_event)
            return True

    elif group_data.process == 1:
        pass

    return False


def exclude_before_game(
    case: int,  # 0-add 1-start
    group_data: gd.gameData,
    uid,
    plugin_event: OlivOS.API.Event,
):
    if case == 0:
        if not group_data.switch:
            return True
        if len(group_data.player_list) == 3:
            main.replyMsg("这里已经满人了", plugin_event)
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                main.replyMsg("你已经在玩家列表中了喔", plugin_event)
                return True
    elif case == 1:
        if not group_data.switch:
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                break
        else:
            main.replyMsg("ni bu zai you xi zhong", plugin_event)
            return True
        if len(group_data.player_list) < 3:
            player_list = ""
            for player in group_data.player_list:
                player_list = "," + player[1]
                player_list = player_list[1:]
            main.replyMsg(f"人还不够呢，快去摇人\n当前玩家列表:{player_list}", plugin_event)
            return True
    return False


def cmp_cards(cards: list, last_cards: list):
    pass


def game_end(
    group_data,
    plugin_event: OlivOS.API.Event,
):
    pass


"""
分析卡牌需要分析出三个数据：牌型、主值、次数
9种牌型: 
1     2     3     4     5     6       7     8      9     10     11     12
单张  对子  顺子  连对  三张  三带一  三带二  三顺  四带二  炸弹  小飞机  大飞机
炸弹包含王炸，三顺即不带翅膀的飞机，小飞机即每三张带一张单牌的。

主值：
单张，对子，三张，炸弹的主值即为卡牌数值， 1 - 13 代表 A - K, **炸弹主值14代表王炸**
三带一，三带二，四带二的主值为 **三或四张相同牌的数值**
顺子，连对，飞机的主值为 **连续的牌中最大的数值**

次数：
顺子，连对，飞机才有的第三个数据，代表连续牌的种类数

尚存bug:
1.当将炸弹拆开作为小飞机，如4 4 4 3 3 3 4 6时，无法识别出小飞机
真的会有人这么打吗？。。
"""


# 分析卡牌并返回类型，主值，次数
def analyze_cards(cards: list) -> tuple:
    card_dict = {}  # dict : key = card type, value = number of card
    for card in cards:
        if card not in card_dict:
            card_dict[card] = 1
        else:
            card_dict[card] += 1

    total_number = len(cards)  # total number of cards
    type_number = len(card_dict)  # number of card type

    card_type = 0
    card_value = 0
    card_count = 0

    if total_number == 1:  # 单张
        card_type = 1
        card_value = list(card_dict.keys())[0]

    elif total_number == 2:
        if type_number == 1:  # 对子
            card_type = 2
            card_value = list(card_dict.keys())[0]
        if type_number == 2:  # 王炸
            if "X" in list(card_dict.keys()) and "D" in list(card_dict.keys()):
                card_type = 10
                card_value = 14

    elif total_number == 3:  # 三张
        if type_number == 1:
            card_type = 5
            card_value = list(card_dict.keys())[0]

    elif total_number == 4:
        if type_number == 1:  # 炸弹
            card_type = 10
            card_value = list(card_dict.keys())[0]
        elif type_number == 2:  # 三带一
            for k, v in card_dict.items():
                if v == 3:
                    card_type = 6
                    card_value = k

    # total_number >= 5
    elif total_number == type_number:  # 顺子
        straight_list = []
        for c in list(card_dict.keys()):
            straight_list.append(gd.ranks.index(c) + 1)
        straight_list.sort()
        if determine_cse(straight_list):
            card_type = 3
            card_value = straight_list[len(straight_list) - 1]
            card_count = total_number

    elif total_number == 5:  # 三带二
        if type_number == 2:
            for k, v in card_dict.items():
                if v == 3:
                    card_type = 7
                    card_value = k

    elif total_number == 6:
        if type_number == 3:  # 四带二张单或连对
            for v in list(card_dict.values()):
                if v != 2:
                    break
            else:  # 仅有6张的连对
                straight_list = []
                for c in list(card_dict.keys()):
                    straight_list.append(gd.ranks.index(c) + 1)
                straight_list.sort()
                if determine_cse(straight_list):
                    card_type = 4
                    card_value = straight_list[len(straight_list) - 1]
                    card_count = type_number

            for k, v in card_dict.items():
                if v == 4:  # 四带二张单
                    card_type = 9
                    card_value = k

        elif type_number == 2:  # 四带一对或三顺
            for k, v in card_dict.items():
                if v == 4:  # 四带一对
                    card_type = 9
                    card_value = k
                elif v == 3:  # 仅有6张的三顺
                    straight_list = []
                    for c in list(card_dict.keys()):
                        straight_list.append(gd.ranks.index(c) + 1)
                    straight_list.sort()
                    if determine_cse(straight_list):
                        card_type = 8
                        card_value = straight_list[1]
                        card_count = type_number

    # total_number > 6
    elif type_number == total_number / 2:  # 连对和小飞机
        for v in list(card_dict.values()):
            if v != 2:
                break
        else:  # 连对
            straight_list = []
            for c in list(card_dict.keys()):
                straight_list.append(gd.ranks.index(c) + 1)
            straight_list.sort()
            if determine_cse(straight_list):
                card_type = 4
                card_value = straight_list[len(straight_list) - 1]
                card_count = type_number

        # 小飞机
        straight_list = []
        for k, v in card_dict.items():
            if v == 1:
                continue
            elif v == 3:
                straight_list.append(gd.ranks.index(k) + 1)
            else:
                break
        else:
            if len(straight_list) == type_number / 2:
                straight_list.sort()
                if determine_cse(straight_list):
                    card_type = 11
                    card_value = straight_list[len(straight_list) - 1]
                    card_count = type_number / 2

    elif type_number == total_number / 3:  # 三顺
        for v in list(card_dict.values()):
            if v != 3:
                break
        else:
            straight_list = []
            for c in list(card_dict.keys()):
                straight_list.append(gd.ranks.index(c) + 1)
            straight_list.sort()
            if determine_cse(straight_list):
                card_type = 8
                card_value = straight_list[len(straight_list) - 1]
                card_count = type_number

    elif type_number == total_number / 2.5:  # 大飞机
        straight_list = []
        for k, v in card_dict.items():
            if v == 2:
                continue
            elif v == 3:
                straight_list.append(gd.ranks.index(k) + 1)
            else:
                break
        else:
            if len(straight_list) == type_number / 2:
                straight_list.sort()
                if determine_cse(straight_list):
                    card_type = 12
                    card_value = straight_list[len(straight_list) - 1]
                    card_count = len(straight_list)

    # convert str to int
    if isinstance(card_value, str):
        card_value = gd.ranks.index(card_value) + 1

    return card_type, card_value, card_count


# determine whether the number in list are consecutive
def determine_cse(list: list) -> bool:
    n = len(list)
    for i in range(1, n):
        if list[i] - list[i - 1] != 1:
            return False
    return True
