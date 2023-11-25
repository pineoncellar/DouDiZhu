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
@Desc      :   游戏数据存取与分析
"""

import os
import pickle
import gameData as gd


default_game_data = gd.gameData()


def getGroupData(group_id) -> gd.gameData:
    # 不存在则新建
    name = "Gdata" + str(group_id)
    if not os.access("plugin/data/douDiZhu/data/data_" + name + ".bin", os.R_OK):
        resetGroupData(group_id)
    game_data = loadClass(name)
    return game_data


def setGroupData(Class: gd.gameData, group_id):
    name = "g" + str(group_id)
    saveClass(Class, name)


def resetGroupData(group_id):
    name = "g" + str(group_id)
    saveClass(default_game_data, name)


def getUserData(uid, gid):
    name = "g" + gid + "_u" + str(uid)
    user_data = loadClass(name)
    return user_data


def setUserData(Class: gd.playerData, uid, gid):
    name = "g" + gid + "_u" + str(uid)
    saveClass(default_game_data, name)


def saveClass(Class: "gd.gameData | gd.playerData", name: str):
    fBin = open("plugin/data/douDiZhu/data/data_" + name + ".bin", "ab")
    pickle.dump(Class, fBin)
    fBin.close()


def loadClass(name: str):
    f = open("plugin/data/douDiZhu/data/data_" + name + ".bin", "rb")
    Class = None
    while True:
        try:
            Class = pickle.load(f)
        except Exception as err:
            print(err)
            break
    f.close()
    return Class
