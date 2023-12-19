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
            main.eventReply("ni bu zai you xi zhong", plugin_event)
            return True
        if uid == group_data.next_player:  # check next player
            pass
        else:
            main.eventReply("现在是" + group_data.next_player + "的回合喔", plugin_event)
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
            main.eventReply("这里已经满人了", plugin_event)
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                main.eventReply("你已经在玩家列表中了喔", plugin_event)
                return True
    elif case == 1:
        if not group_data.switch:
            return True
        for player in group_data.player_list:
            if uid == player[0]:
                break
        else:
            main.eventReply("ni bu zai you xi zhong", plugin_event)
            return True
        if len(group_data.player_list) < 3:
            player_list = ""
            for player in group_data.player_list:
                player_list = "," + player[1]
                player_list = player_list[1:]
            main.eventReply(f"人还不够呢，快去摇人\n当前玩家列表:{player_list}", plugin_event)
            return True
    return False


def cmp_cards(cards: list, last_cards: list):
    pass


def game_end(
    group_data,
    plugin_event: OlivOS.API.Event,
):
    pass
