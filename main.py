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

import time
import random
import os
import re
import json
import OlivOS
import argparse
import dataFiles as df
import gameData as gd
import gamePlay as gp


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


def unity_reply(plugin_event, Proc):
    raw_msg = plugin_event.data.message
    uid = plugin_event.data.user_id
    gid = plugin_event.data.group_id
    name = plugin_event.data.sender.name

    prefix = re.match("^\S+", raw_msg)
    if prefix == "斗地主帮助":
        eventReply(help_msg)

    elif prefix == "加入游戏":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            return
        if len(group_data.player_list) == 3:
            eventReply("这里已经满人了")
            return
        for player in group_data.player_list:
            if uid == player[0]:
                eventReply("你已经在玩家列表中了喔")
                return

        group_data.player_list.append([uid, name])
        player_list = ""
        for player in group_data.player_list:
            player_list = "," + player[1]
        player_list = player_list[1:]
        eventReply(f"{name}加入游戏，当前玩家列表:{player_list}")

    elif prefix == "退出游戏":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            return

        df.resetGroupData(gid)
        eventReply(f"{name}把桌子掀了, 游戏列表清空")

    elif prefix == "开始游戏":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            return
        if len(group_data.player_list) < 3:
            player_list = ""
            for player in group_data.player_list:
                player_list = "," + player[1]
                player_list = player_list[1:]
            eventReply(f"人还不够呢，快去摇人\n当前玩家列表:{player_list}")
            return

        group_data.gameInit(gid)
        hont_card_message = "地主牌为" + " ".join(group_data.host_cards)
        eventReply(hont_card_message)
        player_list_message = (
            "本轮游戏顺序为 "
            + group_data.player_list[0][1]
            + ","
            + group_data.player_list[1][1]
            + ","
            + group_data.player_list[2][1]
            + " 请抢地主"
        )
        eventReply(player_list_message)

    elif prefix == "抢地主":
        group_data = df.getGroupData(gid)
        player_data = df.getUserData(uid, gid)
        if not group_data.switch:
            return
        if group_data.process != 0:
            return

        for player in group_data.player_list:
            if uid == player[0]:
                if name == group_data.next_player:
                    group_data.setHost(name)
                    eventReply(f"{name}成为了地主! ")
                else:
                    eventReply("现在是%s的回合喔", group_data.next_player)

    elif prefix == "不抢":
        group_data = df.getGroupData(gid)
        if not group_data.switch:
            return
        if group_data.process != 0:
            return

        for player in group_data.player_list:
            if uid == player[0]:
                if name == group_data.next_player:
                    group_data.nextTurn(group_data, name)
                    eventReply(f"{name}不要地主啦")
                else:
                    eventReply("现在是%s的回合喔", group_data.next_player)

    elif prefix == "查看手牌":
        group_data = df.getGroupData(gid)
        player_data = df.getUserData(uid, gid)
        if not group_data.switch:
            return
        if group_data.process == None:
            eventReply("游戏都还没开始呢")
            return

        gd.sendCards(player_data)

    elif prefix == "出牌":
        return

    elif prefix == "要不起":
        return


def eventReply(
    message: str,
    plugin_event=OlivOS.API.Event,
    msgid: "str|None" = None,
):
    if "qq" == plugin_event.platform["platform"]:
        try:
            msgid = plugin_event.data.message_id  # type: ignore
        except:
            pass
    res = message
    if msgid != None:
        res = "[OP:reply,id=%s]%s" % (str(msgid), message)
    plugin_event.reply(res)


def getPlayerNumber(group_data: dict, name):
    for i in range(0, 3):
        if group_data.player_list[i] == name:
            return i
