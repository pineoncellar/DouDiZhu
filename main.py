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

    def private_mseeage(plugin_event, Proc):
        pass


group_data = gd.gameData()

"""
class gameData:
    switch: bool # 游戏开关
    player_list: list = [ [uid,name],  [uid,name] ]
    host_player: name
    process: int|None # None = 游戏未开始  0 = 抢地主阶段 1 = 出牌阶段
    next_player: name
    last_cards: list|None
    last_player: uid|None
    host_cards: list|None
"""

help_msg = """斗地主"""


def unity_reply(plugin_event, Proc):
    raw_msg = plugin_event.data.message
    uid = plugin_event.data.user_id
    gid = plugin_event.data.group_id
    name = plugin_event.data.sender["name"]

    prefix = re.match("^\S+", raw_msg).group(0)
    if prefix == "斗地主帮助":
        plugin_event.reply(help_msg)

    elif prefix == "加入游戏":
        group_data = df.getGroupData(gid)
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

        group_data.gameInit(gid)
        player_list_message = (
            "本轮游戏顺序为 "
            + group_data.player_list[0][1]
            + ","
            + group_data.player_list[1][1]
            + ","
            + group_data.player_list[2][1]
            + " 请抢地主"
        )
        plugin_event.reply(player_list_message)

    elif prefix == "抢地主":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        group_data.setHost(uid, gid)
        plugin_event.reply(f"{name}成为了地主! ")
        host_card_message = "地主牌为" + " ".join(group_data.host_cards) + "\n请地主出牌"
        plugin_event.reply(host_card_message)

    elif prefix == "不抢":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        if group_data.next_player == group_data.last_player:  # all refused
            plugin_event.reply(
                "大家都放弃了地主，地主牌为" + " ".join(group_data.host_cards) + "\n正在重新洗牌"
            )

            group_data.gameInit(gid)
            player_list_message = (
                "本轮游戏顺序为 "
                + group_data.player_list[0][1]
                + ","
                + group_data.player_list[1][1]
                + ","
                + group_data.player_list[2][1]
                + " 请抢地主"
            )
            plugin_event.reply(player_list_message)

        else:
            group_data._pass()
            plugin_event.reply(f"{name}不要地主啦")

    elif prefix == "查看手牌":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        player_data = df.getUserData(uid, gid)
        gp.sendCards(player_data)

    elif prefix == "出牌":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return
        player_data = df.getUserData(uid, gid)

        player_cards = raw_msg[3:].split(" ")
        if not player_data.check_cards(player_cards):
            plugin_event.reply("ni mei you zhe xie pai")

        stat, card_type = gp.cmp_cards(player_cards, group_data.last_cards)
        if stat:
            group_data.last_cards = player_cards
            player_data.sort(player_cards)
            plugin_event.reply(f"{name}chu pai : {card_type} {raw_msg[3:]}")

            if len(player_data.cards) == 0:
                pass

            group_data.nextTurn()

        else:
            plugin_event.reply("play fail")  # play fail

    elif prefix == "要不起":
        group_data = df.getGroupData(gid)
        if gp.exclude(group_data, uid, plugin_event):
            return

        group_data.nextTurn(group_data, name)
        plugin_event.reply(f"{name}不要")

    elif prefix == "启用斗地主":
        group_data = df.getGroupData(gid)
        if group_data.switch:
            plugin_event.reply("wei jin yong")
            return

        df.resetGroupData(gid)
        plugin_event.reply("yi qi yong")

    elif prefix == "禁用斗地主":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            plugin_event.reply("wei qi yong")
            return

        group_data.switch = False
        df.setGroupData(group_data, gid)
        plugin_event.reply("yi jin yong")

    elif prefix == "dou di zhu tong ji":
        pass
