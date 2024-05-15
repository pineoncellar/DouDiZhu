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

import OlivOS
import DouDiZhu.dataFiles as df
import DouDiZhu.gameData as gd

import random
import requests
import json
from collections import Counter

ai_name_list = []
for ai_data in gd.ai_data_list:
    ai_name_list.append(ai_data[1])


def exclude(
    group_data: gd.gameData,
    uid,
    plugin_event: OlivOS.API.Event,
):
    if not group_data.switch:  # group switch
        return True
    if group_data.process != None:
        pass
    else:
        return True
    for player in group_data.player_list:  # check player list
        if uid == player[0]:
            break
    else:
        plugin_event.reply("你不在游戏中")
        return True
    if uid == group_data.next_player[0]:  # check next player
        pass
    else:
        plugin_event.reply("现在是" + group_data.next_player[1] + "的回合喔")
        return True

    return False


def exclude_before_game(
    case: int,  # 0-add 1-start 2-add_ai
    group_data: gd.gameData,
    uid,
    plugin_event: OlivOS.API.Event,
):
    if case == 0:
        if len(group_data.player_list) == 3:
            plugin_event.reply("这里已经满人了")
            return True
        if not group_data.switch:
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                plugin_event.reply("你已经在玩家列表中了喔")
                return True
    elif case == 1:
        if not group_data.switch:
            return True
        if group_data.process != None:
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                break
        else:
            plugin_event.reply("你不在游戏中")
            return True
        if len(group_data.player_list) < 3:
            player_list = ""
            for player in group_data.player_list:
                player_list = player_list + "," + player[1]
            player_list = player_list[1:]
            plugin_event.reply(f"人还不够呢，快去摇人\n当前玩家列表:{player_list}")
            return True
    elif case == 2:
        if not group_data.switch:
            return True
        if len(group_data.player_list) == 3:
            plugin_event.reply("这里已经满人了")
            return True

        ai_num = 0
        for player in group_data.player_list:
            if player[1] in ai_name_list:
                ai_num += 1

        if ai_num == 2:
            plugin_event.reply("列表中已经有两位人机了")
            return True

    return False


def sendCards(player_data: gd.playerData, plugin_event):
    cards = player_data.cards
    message = "你的手牌是: " + " ".join(cards)
    uid = player_data.uid
    name = player_data.name
    if uid not in ai_name_list:  # 排除AI
        plugin_event.send("private", uid, message)


def gameInit(group_data, gid, plugin_event):
    card_pile = gd.CardPile()
    card_pile.shuffle()

    # mix the player list
    random.shuffle(group_data.player_list)

    player_list_message = (
        "本轮游戏顺序为 "
        + group_data.player_list[0][1]
        + ", "
        + group_data.player_list[1][1]
        + ", "
        + group_data.player_list[2][1]
        + " 请抢地主"
    )
    plugin_event.reply(player_list_message)

    # draw player cards
    player1 = gd.playerData(
        group_data.player_list[0][0],
        group_data.player_list[0][1],
        card_pile.draw_player_card(),
    )
    player1.sort()
    df.setUserData(player1, player1.uid, gid)
    player2 = gd.playerData(
        group_data.player_list[1][0],
        group_data.player_list[1][1],
        card_pile.draw_player_card(),
    )
    player2.sort()
    df.setUserData(player2, player2.uid, gid)
    player3 = gd.playerData(
        group_data.player_list[2][0],
        group_data.player_list[2][1],
        card_pile.draw_player_card(),
    )
    player3.sort()
    df.setUserData(player3, player3.uid, gid)

    group_data.host_cards = card_pile.draw_host_card()
    group_data.last_player = [player3.uid, player3.name]
    group_data.next_player = [player1.uid, player1.name]
    group_data.process = 0

    # send cards message
    sendCards(player1, plugin_event)
    sendCards(player2, plugin_event)
    sendCards(player3, plugin_event)

    ai_host_check(group_data, gid, plugin_event)


def setHost(group_data, uid, gid, plugin_event):
    tmp_num = 0
    landlord_up_player = 0
    landlord_down_player = 0
    for player in group_data.player_list:
        if player[0] == uid:
            landlord_up_player = group_data.player_list[(tmp_num - 1) % 3]
            landlord_down_player = group_data.player_list[(tmp_num + 1) % 3]
            break
        tmp_num += 1

    landlord_up_player_data = df.getUserData(landlord_up_player[0], gid)
    landlord_down_player_data = df.getUserData(landlord_down_player[0], gid)
    landlord_up_player_data.setRole(0)
    landlord_down_player_data.setRole(2)
    df.setUserData(landlord_up_player_data, landlord_up_player[0], gid)
    df.setUserData(landlord_down_player_data, landlord_down_player[0], gid)

    player_data = df.getUserData(uid, gid)
    player_data.incCards(group_data.host_cards)
    player_data.setRole(1)
    df.setUserData(player_data, uid, gid)

    sendCards(player_data, plugin_event)
    group_data.host_player = [uid, player_data.name]
    group_data.next_player = [uid, player_data.name]
    group_data.process = 1

    douzero_init(group_data, gid, plugin_event)


def cmp_cards(cards: list, last_cards: list) -> tuple:
    card_type, card_value, card_count = analyze_cards(cards)
    if card_type == 0:
        return False, "未知牌型"
    if last_cards:
        l_card_type, l_card_value, l_card_count = analyze_cards(last_cards)
        if card_type == 10:
            if l_card_count == 10:
                if not (card_value > l_card_value):
                    return False, "所出的牌并没有比上家的大"
        else:
            if not (card_type == l_card_type):
                return False, "牌型不匹配"
            if not (card_value > l_card_value):
                return False, "所出的牌并没有比上家的大"
            if card_count != 0:
                if not (card_count == l_card_count):
                    return False, "牌型不匹配"
    # 如果last_cards为None，则直接判断有效
    if card_type == 12:
        card_type = 11
    if card_type == 10 and card_value == 16:
        card_type = 12
    card_type_list = [
        "一张",
        "一对",
        "顺子",
        "连对",
        "三张",
        "三带一",
        "三带二",
        "三顺",
        "四带二",
        "炸弹",
        "飞机",
        "王炸",
    ]
    return True, card_type_list[card_type - 1]


def game_end(
    group_data,
    player_data,
    plugin_event: OlivOS.API.Event,
):
    end_speech = ""
    if player_data.uid == group_data.host_player[0]:
        end_speech = "游戏结束，地主胜利"
    else:
        end_speech = "游戏结束，农民胜利"
    plugin_event.reply(end_speech)


ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "X", "D"]
det_ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
"""
分析卡牌需要分析出三个数据：牌型、主值、次数
9种牌型: 
1     2     3     4     5     6       7     8      9     10     11     12
单张  对子  顺子  连对  三张  三带一  三带二  三顺  四带二  炸弹  小飞机  大飞机
炸弹包含王炸，三顺即不带翅膀的飞机，小飞机即每三张带一张单牌的。

主值：
单张，对子，三张，炸弹的主值即为卡牌数值, 3 - 13 代表 3 - K, 14 - 15 代表 A - 2, 炸弹主值16代表王炸, 单张主值16, 17代表小王和大王
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
            straight_list.append(det_ranks.index(c) + 1)
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
                    straight_list.append(det_ranks.index(c) + 1)
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
                        straight_list.append(det_ranks.index(c) + 1)
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
                straight_list.append(det_ranks.index(c) + 1)
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
                straight_list.append(det_ranks.index(k) + 1)
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
                straight_list.append(det_ranks.index(c) + 1)
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
                straight_list.append(det_ranks.index(k) + 1)
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
        card_value = ranks.index(card_value) + 3

    return card_type, card_value, card_count


# determine whether the number in list are consecutive
def determine_cse(list: list) -> bool:
    n = len(list)
    for i in range(1, n):
        if list[i] - list[i - 1] != 1:
            return False
    return True


def ai_host_check(group_data, gid, plugin_event):
    if group_data.ai_player_number == 0:
        return

    # plugin_event.reply(f"ai_host_check, next_player:{group_data.next_player}")

    next_player_name = group_data.next_player[1]
    if next_player_name in ai_name_list:  # 下一位是ai
        ai_player_data = df.getUserData(group_data.next_player[0], gid)
        if check_if_get_host(ai_player_data.cards):
            setHost(group_data, ai_player_data.uid, gid, plugin_event)
            plugin_event.reply(f"{next_player_name}成为了地主! ")
            host_card_message = "地主牌为" + " ".join(group_data.host_cards)
            plugin_event.reply(host_card_message)
        else:
            plugin_event.reply(f"{next_player_name}不要地主")
            if group_data.next_player == group_data.last_player:  # all refused
                plugin_event.reply(
                    "大家都放弃了地主，地主牌为"
                    + " ".join(group_data.host_cards)
                    + ", 请重新开始游戏"
                )
                group_data.process = None
                return
            group_data._pass()
            ai_host_check(group_data, gid, plugin_event)
    else:
        return


def douzero_init(group_data, gid, plugin_event):
    if group_data.ai_player_number == 0:
        return

    elif group_data.ai_player_number == 1:  # 单人机
        game_data = {}
        # 取人机在列表中的位置
        ai_player_index = 0
        num_tmp = 0
        for player in group_data.player_list:
            if player[1] in ai_name_list:
                ai_player_index = num_tmp
                break
            num_tmp += 1
        # 取人机位号
        if group_data.host_player[1] in ai_name_list:
            ai_role = 1
        elif (
            group_data.host_player == group_data.player_list[(ai_player_index + 1) % 3]
        ):  # 地主上家
            ai_role = 0
        else:
            ai_role = 2

        ai_player_data = df.getUserData(group_data.player_list[ai_player_index][0], gid)
        ai_cards = "".join(["T" if i == "10" else i for i in ai_player_data.cards])
        host_cards = "".join(["T" if i == "10" else i for i in group_data.host_cards])
        ai_model = gd.ai_data_list[ai_name_list.index(ai_player_data.name)][2]

        init_ai_player_data = [
            {
                "model": ai_model,
                "hand_cards": ai_cards,
                "position_code": ai_role,
            },
        ]
        game_data = {
            "ai_amount": 1,
            "three_landlord_cards": host_cards,
            "pid": gid,
            "player_data": init_ai_player_data,
        }
        data = {"action": "init", "data": game_data}

        res = douzero_send(data)
        # plugin_event.reply(f"res: {json.dumps(res)}")
        # plugin_event.send("group", 1006250371, f"from gid:{gid}  res:{res}")

        if ai_role == 1:  # ai是地主，马上出牌
            ai_play(0, res, group_data, gid, plugin_event)

    else:  # 两位人机
        # 取人机在玩家列表中的索引
        ai0_player_index = -1
        ai1_player_index = -1
        num_tmp = 0
        for player in group_data.player_list:
            if player[1] in ai_name_list:
                if ai0_player_index == -1:
                    ai0_player_index = num_tmp
                else:
                    ai1_player_index = num_tmp
            num_tmp += 1
        # 取人机位号
        ai0_position_code = 0
        ai1_position_code = 0
        if (
            group_data.host_player == group_data.player_list[ai0_player_index]
        ):  # AI0是地主
            ai0_position_code = 1
            ai1_position_code = (1 + ai1_player_index - ai0_player_index) % 3
        elif (
            group_data.host_player == group_data.player_list[ai1_player_index]
        ):  # AI1是地主
            ai1_position_code = 1
            ai0_position_code = (1 + ai0_player_index - ai1_player_index) % 3
        else:  # 玩家是地主
            if ai1_player_index - ai0_player_index == 1:
                ai0_position_code = 2
                ai1_position_code = 0
            else:
                ai0_position_code = 0
                ai1_position_code = 2

        ai0_player_data = df.getUserData(
            group_data.player_list[ai0_player_index][0], gid
        )
        ai0_cards = "".join(["T" if i == "10" else i for i in ai0_player_data.cards])
        host_cards = "".join(["T" if i == "10" else i for i in group_data.host_cards])
        ai0_model = gd.ai_data_list[ai_name_list.index(ai0_player_data.name)][2]

        ai1_player_data = df.getUserData(
            group_data.player_list[ai1_player_index][0], gid
        )
        ai1_cards = "".join(["T" if i == "10" else i for i in ai1_player_data.cards])
        host_cards = "".join(["T" if i == "10" else i for i in group_data.host_cards])
        ai1_model = gd.ai_data_list[ai_name_list.index(ai1_player_data.name)][2]

        ai_init_player_data = [
            {
                "model": ai0_model,
                "hand_cards": ai0_cards,
                "position_code": ai0_position_code,
            },
            {
                "model": ai1_model,
                "hand_cards": ai1_cards,
                "position_code": ai1_position_code,
            },
        ]

        game_data = {
            "three_landlord_cards": host_cards,
            "pid": gid,
            "ai_amount": 2,
            "player_data": ai_init_player_data,
        }

        data = {"action": "init", "data": game_data}

        res = douzero_send(data)
        # plugin_event.reply(f"res: {json.dumps(res)}")
        # plugin_event.send("group", 1006250371, f"from gid:{gid}  res:{res}")
        res_data = res["data"]
        if (
            1 in [ai0_position_code, ai1_position_code] and res["status"] == "ok"
        ):  # AI是地主，马上出牌
            # 由此往下，ai0与ai1定义更新
            ai_play(0, res, group_data, gid, plugin_event)

            if res_data["play"][1]["cards"] != None:  # ai1为地主下家，马上出牌
                ai_play(1, res, group_data, gid, plugin_event)


def douzero_step(group_data, gid, player_cards, plugin_event):
    if group_data.ai_player_number == 0:
        return

    post_cards = "".join(["T" if i == "10" else i for i in player_cards])
    if player_cards == []:
        post_cards = ""

    game_data = {
        "pid": gid,
        "player": (
            group_data.player_list.index(group_data.next_player)
            - group_data.player_list.index(group_data.host_player)
        )
        % 3,  # 取玩家位号：0-地主上家，1-地主，2-地主下家
        "cards": post_cards,
    }
    data = {"action": "play", "data": game_data}

    res = douzero_send(data)
    res_data = res["data"]

    # plugin_event.reply(f"测试信息：\n res: {json.dumps(res)}")
    # plugin_event.send("group", 1006250371, f"from gid:{gid}  res:{res}")

    if res["action"] == "play":  # AI出牌了
        if ai_play(0, res, group_data, gid, plugin_event):
            return True
        if res_data["play"][1]["cards"] != None:
            if ai_play(1, res, group_data, gid, plugin_event):
                return True
        return False


def douzero_send(data: dict, port="24813"):
    url = "http://127.0.0.1:" + str(port)
    res = requests.post(url=url, data=json.dumps(data))
    res = json.loads(res.text)
    if res["status"] == "ok":
        return res
    else:
        err = res["msg"]
        return err


check_card_list = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


# ai抢地主的简单逻辑：大王4分，小王3分，每张2两分，每张A 1分，三张相同2分，炸弹3分，分数总和大于9就抢 ———— 好懒，不想写太复杂的
def check_if_get_host(cards):
    point = 0
    counter = Counter(cards)
    if "D" in cards:
        point += 4
    if "X" in cards:
        point += 3
    if counter.get("2") != None:
        point += counter.get("2") * 2
    if counter.get("A") != None:
        point += counter.get("A")

    for card in check_card_list:
        card_num = counter.get(card)
        if card_num != None and card_num > 2:
            point += card_num - 1
    print(f"point: {point}")
    if point > 8:
        return True
    else:
        return False


def ai_play(ai_index, res, group_data, gid, plugin_event) -> bool:
    res_data = res["data"]
    ai_player = group_data.next_player
    ai_player_data = df.getUserData(ai_player[0], gid)

    player_cards = [
        "10" if i == "T" else i for i in res_data["play"][ai_index]["cards"]
    ]  # 将T转为10

    if player_cards != []:
        if group_data.last_player == group_data.next_player:
            group_data.last_cards = None

        stat, card_type = cmp_cards(player_cards, group_data.last_cards)
        if stat:  # 其实AI出的牌不会有错，不过还是保留此判断
            group_data.last_cards = player_cards
            group_data.last_player = group_data.next_player
            ai_player_data.decCards(player_cards)
            ai_player_data.sort()
            play_cards = " ".join(player_cards)
            plugin_event.reply(
                f"{ai_player_data.name}出牌: {card_type} {play_cards} 剩余牌数{len(ai_player_data.cards)}"
            )

            if len(ai_player_data.cards) == 0:
                game_end(group_data, ai_player_data, plugin_event)
                df.resetGroupData(gid)
                return True
            else:
                group_data._pass()
                df.setGroupData(group_data, gid)
                df.setUserData(
                    ai_player_data,
                    ai_player_data.uid,
                    gid,
                )
        else:
            plugin_event.reply(
                f"{ai_player_data.name}出牌错误: \n{card_type}\n抱歉未能将游戏进行下去，请将此bug反馈给骰主"
            )
    else:  # AI不要
        group_data._pass()
        plugin_event.reply(f"{ai_player_data.name}不要")

    return False


def from_role_get_player_data(group_data, gid, role) -> gd.playerData:
    for player in group_data.player_list:
        player_data = df.getUserData(player[0], gid)
        if role == player_data.role:
            return player_data
