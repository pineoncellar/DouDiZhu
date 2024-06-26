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
@Desc      :   斗地主插件主流程
"""
version = "1.1.1"

import OlivOS
import DouDiZhu.dataFiles as df
import DouDiZhu.gameData as gd
import DouDiZhu.gamePlay as gp

import time
import random
import os
import re
import json
import argparse


class Event(object):
    def init(plugin_event, Proc):
        # 创建文件夹
        if not os.path.exists("plugin/data"):
            os.mkdir("plugin/data")
        if not os.path.exists("plugin/data/douDiZhu"):
            os.mkdir("plugin/data/douDiZhu")
        if not os.path.exists("plugin/data/douDiZhu/data"):
            os.mkdir("plugin/data/douDiZhu/data")

        # 创建文件
        if not os.access("plugin/data/douDiZhu/user_data.json", os.R_OK):
            data = {"data": []}
            with open(
                "plugin/data/douDiZhu/user_data.json", "w", encoding="utf-8"
            ) as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def group_message(plugin_event, Proc):
        unity_reply(plugin_event, Proc)

    def private_message(plugin_event, Proc):
        unity_reply(plugin_event, Proc)


group_data = gd.gameData()

"""
class gameData:
    switch: bool # 游戏开关
    player_list: list = [ [uid,name],  [uid,name] ]
    host_player: [uid,name]
    process: int|None  # None = 游戏未开始  0 = 抢地主阶段 1 = 出牌阶段
    next_player: [uid,name]
    last_cards: list|None
    last_player: uid|None
    host_cards: list|None
    ai_player_number: bool = False # 是否有ai玩家
"""

help_msg = f"""斗地主插件 ver{version} by 地窖上的松
开局之前请先添加骰娘好友，因为需要用到私聊发牌
游戏指令如下：
退出游戏  // 退出整个游戏，将重置游戏玩家列表与所有数据
游戏准备阶段：
加入游戏  // 加入准备玩家列表
开始游戏  // 当玩家人数为3时，可以开始游戏
抢地主阶段：
抢地主  // 依顺序抢地主
不抢  // 放弃抢地主
出牌阶段：
出牌  // 打出手牌，不分大小写，以"X"代替小王，"D"代替大王。
出牌后须有空格，每张牌以空格隔开，如“出牌 3 3 3 4”或“出牌 j j q q k k”
要不起  // 字面意思
查看手牌  // 查看自己最新的手牌
添加人机（Beta）：
添加困难人机/中级人机/简单人机  // 添加对应的人机至玩家列表
人机会自动抢地主与出牌，如果遇到bug，请反馈给骰主。
"""


def unity_reply(plugin_event, Proc):
    raw_msg = plugin_event.data.message
    uid = plugin_event.data.user_id
    try:
        gid = plugin_event.data.group_id
    except:
        gid = uid  # 在私聊中将QQ号作为窗口号
    name = plugin_event.data.sender["name"]

    prefix = ""
    if re.match("^\S+", raw_msg) != None:  # 排除掉神秘报错
        prefix = re.match("^\S+", raw_msg).group(0)
    if prefix == "斗地主帮助":
        plugin_event.reply(help_msg)

    elif prefix == "斗地主状态":  # 测试用
        if str(uid) != "602380092":
            return

        group_data = df.getGroupData(gid)
        plugin_event.reply("switch " + str(group_data.switch))
        plugin_event.reply("player_list " + str(group_data.player_list))
        plugin_event.reply("host_player " + str(group_data.host_player))
        plugin_event.reply("process " + str(group_data.process))
        plugin_event.reply("next_player " + str(group_data.next_player))
        plugin_event.reply("last_cards " + str(group_data.last_cards))
        plugin_event.reply("last_player " + str(group_data.last_player))
        plugin_event.reply("host_cards " + str(group_data.host_cards))

    elif prefix == "玩家状态":
        if str(gid) == "1006250371":
            pass
        elif str(uid) != "602380092" and str(uid) != "0":
            return

        player_data = df.getUserData(uid, gid)
        plugin_event.reply("uid: " + str(player_data.uid))
        plugin_event.reply("name: " + str(player_data.name))
        plugin_event.reply("cards: " + str(player_data.cards))

    elif prefix == "加入游戏":
        group_data = df.getGroupData(gid)

        try:
            __ = group_data.ai_player_number
        except:
            group_data.ai_player_number = 0

        if gp.exclude_before_game(0, group_data, uid, plugin_event):
            return

        group_data.player_list.append([uid, name])
        player_list = ""
        for player in group_data.player_list:
            player_list = player_list + "," + player[1]
        player_list = player_list[1:]
        plugin_event.reply(f"{name}加入游戏，当前玩家列表:{player_list}")
        df.setGroupData(group_data, gid)

    elif prefix == "退出游戏":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            return

        df.resetGroupData(gid)
        plugin_event.reply(f"{name}把桌子掀了, 游戏列表清空")

    elif prefix == "开始游戏":
        group_data = df.getGroupData(gid)
        if gp.exclude_before_game(1, group_data, uid, plugin_event):
            return

        gp.gameInit(group_data, gid, plugin_event)
        df.setGroupData(group_data, gid)

    elif prefix == "抢地主":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        gp.setHost(group_data, uid, gid, plugin_event)
        plugin_event.reply(f"{name}成为了地主! ")
        host_card_message = (
            "地主牌为" + " ".join(group_data.host_cards) + "\n请地主出牌"
        )
        plugin_event.reply(host_card_message)
        df.setGroupData(group_data, gid)

    elif prefix == "不抢":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        if group_data.next_player == group_data.last_player:  # all refused
            plugin_event.reply(
                "大家都放弃了地主，地主牌为"
                + " ".join(group_data.host_cards)
                + ", 请重新开始游戏"
            )
            group_data.process = None

            """gp.gameInit(group_data, gid, plugin_event)
            player_list_message = (
                "本轮游戏顺序为 "
                + group_data.player_list[0][1]
                + ","
                + group_data.player_list[1][1]
                + ","
                + group_data.player_list[2][1]
            )
            plugin_event.reply(player_list_message)"""
        else:
            group_data._pass()
            plugin_event.reply(f"{name}不要地主啦")
            gp.ai_host_check(group_data, gid, plugin_event)
        df.setGroupData(group_data, gid)

    elif prefix == "查看手牌":
        group_data = df.getGroupData(gid)
        if group_data.process != None:
            pass
        else:
            return True
        if not group_data.switch:  # group switch
            return
        for player in group_data.player_list:  # check player list
            if uid == player[0]:
                break
        else:
            plugin_event.reply("你不在游戏中")
            return

        player_data = df.getUserData(uid, gid)
        gp.sendCards(player_data, plugin_event)

    elif prefix == "出牌":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return
        player_data = df.getUserData(uid, gid)

        if group_data.last_player == group_data.next_player:
            group_data.last_cards = None

        player_cards = raw_msg[3:].split(" ")
        player_cards = list(map(str.upper, player_cards))  # uppercase
        while "" in player_cards:
            player_cards.remove("")  # remove excess elements
        if not player_data.check_cards(player_cards):
            plugin_event.reply(f"错误，请重新选择出牌:\n你没有这些牌")
            return

        stat, card_type = gp.cmp_cards(player_cards, group_data.last_cards)
        if stat:
            group_data.last_cards = player_cards
            group_data.last_player = group_data.next_player
            player_data.decCards(player_cards)
            player_data.sort()
            plugin_event.reply(
                f"{name}出牌: {card_type} {raw_msg[3:]} 剩余牌数{len(player_data.cards)}"
            )

            if len(player_data.cards) == 0:
                gp.game_end(group_data, player_data, plugin_event)
                df.resetGroupData(gid)
            else:
                group_data._pass()
                if gp.douzero_step(
                    group_data, gid, player_cards, plugin_event
                ):  # step一定要放在所有流程之后，保存数据之前
                    return  # 当游戏在AI出牌后结束，就直接退出，不然会将最后一轮出牌的游戏数据保存下来
                gp.sendCards(player_data, plugin_event)
                df.setGroupData(group_data, gid)
                df.setUserData(player_data, uid, gid)

        else:
            plugin_event.reply(
                f"错误，请重新选择出牌:\n{card_type}"
            )  # card_type = error msg

    elif prefix == "要不起":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        group_data._pass()
        plugin_event.reply(f"{name}不要")
        if gp.douzero_step(group_data, gid, [], plugin_event):
            return

        df.setGroupData(group_data, gid)

    elif prefix == "启用斗地主":
        group_data = df.getGroupData(gid)
        if group_data.switch:
            plugin_event.reply("本群斗地主未禁用")
            return

        df.resetGroupData(gid)
        plugin_event.reply("已启用本群斗地主")

    elif prefix == "禁用斗地主":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            plugin_event.reply("本群斗地主未启用")
            return

        group_data.switch = False
        df.setGroupData(group_data, gid)
        plugin_event.reply("已禁用本群斗地主")

    elif prefix == "斗地主统计":
        pass

    elif prefix == "添加困难人机":
        group_data = df.getGroupData(gid)
        if gp.exclude_before_game(2, group_data, uid, plugin_event):
            return

        try:
            __ = group_data.ai_player_number
        except:
            group_data.ai_player_number = 0

        ai_data = gd.ai_data_list[0]
        if (
            group_data.ai_player_number == 1
        ):  # 玩家列表中已经有个人机了，就将人机的id+1，以免重复
            group_data.player_list.append([ai_data[0] + 1, ai_data[1]])
            group_data.ai_player_number = 2
        else:
            group_data.player_list.append([ai_data[0], ai_data[1]])
            group_data.ai_player_number = 1

        player_list = ""
        for player in group_data.player_list:
            player_list = player_list + "," + player[1]
        player_list = player_list[1:]
        plugin_event.reply(f"{ai_data[1]}加入游戏，当前玩家列表:{player_list}")

        df.setGroupData(group_data, gid)

    elif prefix == "添加中级人机":
        group_data = df.getGroupData(gid)
        if gp.exclude_before_game(2, group_data, uid, plugin_event):
            return

        try:
            __ = group_data.ai_player_number
        except:
            group_data.ai_player_number = 0

        ai_data = gd.ai_data_list[1]
        if (
            group_data.ai_player_number == 1
        ):  # 玩家列表中已经有个人机了，就将人机的id+1，以免重复
            group_data.player_list.append([ai_data[0] + 1, ai_data[1]])
            group_data.ai_player_number = 2
        else:
            group_data.player_list.append([ai_data[0], ai_data[1]])
            group_data.ai_player_number = 1

        player_list = ""
        for player in group_data.player_list:
            player_list = player_list + "," + player[1]
        player_list = player_list[1:]
        plugin_event.reply(f"{ai_data[1]}加入游戏，当前玩家列表:{player_list}")

        df.setGroupData(group_data, gid)

    elif prefix == "添加简单人机":
        group_data = df.getGroupData(gid)
        if gp.exclude_before_game(2, group_data, uid, plugin_event):
            return

        try:
            __ = group_data.ai_player_number
        except:
            group_data.ai_player_number = 0

        ai_data = gd.ai_data_list[2]
        if (
            group_data.ai_player_number == 1
        ):  # 玩家列表中已经有个人机了，就将人机的id+1，以免重复
            group_data.player_list.append([ai_data[0] + 1, ai_data[1]])
            group_data.ai_player_number = 2
        else:
            group_data.player_list.append([ai_data[0], ai_data[1]])
            group_data.ai_player_number = 1

        player_list = ""
        for player in group_data.player_list:
            player_list = player_list + "," + player[1]
        player_list = player_list[1:]
        plugin_event.reply(f"{ai_data[1]}加入游戏，当前玩家列表:{player_list}")

        df.setGroupData(group_data, gid)
