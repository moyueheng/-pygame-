# _*_ coding: utf-8 _*_

# @File    :   main.py
# @Version :   1.0
# @Author  :   grit
# @Email   :   2285839445@qq.com
# @Time    :   2020/05/26 21:05:19
# Description:


import os
import sys
import pygame
from Sprites import *
from config import Config
from itertools import chain  # 链接列表
import time

"""退出游戏"""


def quitGame():
    '''退出游戏'''
    pygame.quit()
    sys.exit(0)


"""游戏地图元素类"""

class GameMap():
    '''游戏地图'''

    def __init__(self, num_cols, num_rows):
        self.walls = []  # 存放墙对象
        self.boxes = []  # 存放盒子对象
        self.targets = []  # 存放目的地对象
        self.trees = []
        self.num_cols = num_cols  # 行数
        self.num_rows = num_rows  # 列数

    '''增加游戏元素'''

    def addElement(self, elem_type, col, row):
        if elem_type == 'wall':
            self.walls.append(elementSprite(
                'wall.png', col, row))  # 图片+位置 # TODO
        elif elem_type == 'box':
            self.boxes.append(elementSprite('box.jpg', col, row))
        elif elem_type == 'target':
            self.targets.append(elementSprite('target.png', col, row))
        elif elem_type == 'tree':
            self.trees.append(elementSprite('tree.png', col, row))

    '''画游戏地图元素'''

    def draw(self, screen):
        for elem in self.elemsIter():
            elem.draw(screen)

    '''游戏元素迭代器'''  # 迭代器是特殊的生成器
    def elemsIter(self):
        for elem in chain(self.targets, self.walls, self.boxes, self.trees):
            yield elem  # yield到一个迭代器器里面去

    '''该关卡中所有的箱子是否都在指定位置, 在的话就是通关了'''

    def levelCompleted(self) -> bool:
        for box in self.boxes:  # 对于每个盒子来说看看是否到达目标
            is_match = False
            for target in self.targets:
                # 如果宽高重合就是就是重合了
                if box.col == target.col and box.row == target.row:
                    is_match = True
                    break

            if not is_match:  # 只要有一个没匹配到都是没通关
                return False
        return True

    '''某位置是否可到达'''

    def isValidPos(self, col, row) -> bool:
        # 在地图范围内
        if col >= 0 and row >= 0 and col < self.num_cols and row < self.num_rows:

            block_size = Config.get('block_size')

            temp1 = self.walls + self.boxes + self.trees  # 存放所以的墙和盒子,因为这些玩家都不可到达
            temp2 = pygame.Rect(col * block_size, row *
                                block_size, block_size, block_size)
            return temp2.collidelist(temp1) == -1  # 如
        else:
            return False

    '''获得某位置的box'''

    def getBox(self, col, row):
        for box in self.boxes:
            if box.col == col and box.row == row:
                return box
        return None


"""游戏界面"""


class GameInterface():

    def __init__(self, screen):
        self.screen = screen
        self.levels_path = Config.get('levels_path')
        self.initGame()

    '''导入关卡地图'''

    def loadLevel(self, game_level):
        with open(os.path.join(self.levels_path, game_level), 'r') as f:
            lines = f.readlines()  # 读取地图文件
        # 游戏地图
        self.game_map = GameMap(
            max([len(line) for line in lines]) - 1, len(lines))  # 这么多行中最长的一个就是列数,根据我画的地图自动确定行数
        # 游戏surface 总的界面
        height = Config.get('block_size') * self.game_map.num_rows
        width = Config.get('block_size') * self.game_map.num_cols
        self.game_surface = pygame.Surface((width, height))  # 绘制游戏总界面
        self.game_surface.fill(Config.get('bg_color'))  # 填充游戏总界面
        self.game_surface_blank = self.game_surface.copy()  # 保存一个空白的surface对象,深拷贝

        for row, elems in enumerate(lines):  # 他会把行号读出来
            # [行号,字符串]
            for col, elem in enumerate(elems):
                # [列号,字符]
                # 对于每个字符串上的一个字符又是一个列号
                if elem == '*':
                    self.game_map.addElement('wall', col, row)
                elif elem == '#':
                    self.game_map.addElement('box', col, row)
                elif elem == 'o':
                    self.game_map.addElement('target', col, row)
                elif elem == 't':
                    self.game_map.addElement('tree', col, row)
                elif elem == 'p':
                    self.player = pusherSprite(col, row)

    '''游戏初始化'''

    def initGame(self):
        self.scroll_x = 0
        self.scroll_y = 0

    '''将游戏界面画出来'''

    def draw(self, *elems):
        self.scroll()  # 只是对scroll的数值就像修改
        self.game_surface.blit(self.game_surface_blank,
                               dest=(0, 0))  # 将空白的游戏页面画到屏幕上
        for elem in elems:
            elem.draw(self.game_surface)
        self.screen.blit(self.game_surface, dest=(
            self.scroll_x, self.scroll_y))

    '''因为游戏界面面积>游戏窗口界面, 所以需要根据人物位置滚动'''
    # 就算对scroll的数值进行了修改

    def scroll(self):
        x, y = self.player.rect.center  # 玩家中心位置
        width = self.game_surface.get_rect().w  # 游戏地图总面积的宽高
        height = self.game_surface.get_rect().h
        # 当人物朝右半边走的时候
        if (x + Config.get('WIDTH') // 2) > Config.get('WIDTH'):

            if -1 * self.scroll_x + Config.get('WIDTH') < width:
                self.scroll_x -= 2

        # 向下滚
        elif (x + Config.get('WIDTH') // 2) > 0:
            if self.scroll_x < 0:
                self.scroll_x += 2
        # 向上滚
        if (y + Config.get('HEIGHT') // 2) > Config.get('HEIGHT'):
            if -1 * self.scroll_y + Config.get('HEIGHT') < height:
                self.scroll_y -= 2
       # 向下滚
        elif (y + 250) > 0:
            if self.scroll_y < 0:
                self.scroll_y += 2


"""游戏运行"""  # TODO


def runGame(screen, game_level):
    clock = pygame.time.Clock()  # 帧数
    game_interface = GameInterface(screen)  # 实例化一个游戏界面类
    game_interface.loadLevel(game_level)  # 载入一个关卡

    font_path = os.path.join(Config.get(
        'resources_path'), Config.get('fontfolder'), 'simkai.ttf')  # 载入字体
    # 游戏提示信息
    text = '按R键重新开始本关'
    font = pygame.font.Font(font_path, 15)
    text_render = font.render(text, 1, (255, 255, 255))

    # 游戏进行的主要逻辑
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitGame()
            elif event.type == pygame.KEYDOWN:
                # 向左移动
                if event.key == pygame.K_LEFT:
                    # 先模拟向左移动得到向左移动的坐标
                    next_pos = game_interface.player.move('left', is_test=True)
                    # 判断是否可以真的移动过去
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('left')
                    else:
                        # 获得一个箱子对象
                        box = game_interface.game_map.getBox(*next_pos)
                        # 如果能获得箱子对象
                        if box:
                            # 模拟运动如果可以达到则运动
                            next_pos = box.move('left', is_test=True)
                            if game_interface.game_map.isValidPos(*next_pos):
                                game_interface.player.move('left')
                                box.move('left')
                    break
                if event.key == pygame.K_RIGHT:
                    next_pos = game_interface.player.move(
                        'right', is_test=True)
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('right')
                    else:
                        box = game_interface.game_map.getBox(*next_pos)
                        if box:
                            next_pos = box.move('right', is_test=True)
                            if game_interface.game_map.isValidPos(*next_pos):
                                game_interface.player.move('right')
                                box.move('right')
                    break
                if event.key == pygame.K_DOWN:
                    next_pos = game_interface.player.move('down', is_test=True)
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('down')
                    else:
                        box = game_interface.game_map.getBox(*next_pos)
                        if box:
                            next_pos = box.move('down', is_test=True)
                            if game_interface.game_map.isValidPos(*next_pos):
                                game_interface.player.move('down')
                                box.move('down')
                    break
                if event.key == pygame.K_UP:
                    next_pos = game_interface.player.move('up', is_test=True)
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('up')
                    else:
                        box = game_interface.game_map.getBox(*next_pos)
                        if box:
                            next_pos = box.move('up', is_test=True)
                            if game_interface.game_map.isValidPos(*next_pos):
                                game_interface.player.move('up')
                                box.move('up')
                    break
                if event.key == pygame.K_r:
                    game_interface.initGame()
                    game_interface.loadLevel(game_level)
        game_interface.draw(game_interface.player, game_interface.game_map)
        if game_interface.game_map.levelCompleted():
            return
        screen.blit(text_render, (5, 5))
        pygame.display.flip()
        clock.tick(60)


"""绘制按钮"""


def BUTTON(screen, position, text, bwidth=310, bheight=65,font_size = 50):
    """定义按钮
    Args:
            screen: 被画按钮的surface对象,
            position: 在screen对象上画的位置
            text: 画的文本内容
    return:
            按钮在screen上的react对象,记录位置,用于做碰撞检测
    """
    line_width = 5
    left_top_colour = (150, 150, 150)
    right_down_colour = (50, 50, 50)
    fill_colour = (100, 100, 100)
    font_colour = (255, 0, 0)
    left, top = position  # 拆包
    pygame.draw.line(screen, left_top_colour, (left, top),
                     (left+bwidth, top), line_width)  # 上方的线
    pygame.draw.line(screen, left_top_colour, (left, top-2),
                     (left, top+bheight), line_width)  # 左边的线
    pygame.draw.line(screen, right_down_colour, (left, top+bheight),
                     (left+bwidth, top+bheight), line_width)  # 右边的线
    pygame.draw.line(screen, right_down_colour, (left+bwidth,
                                                 top+bheight), [left+bwidth, top], line_width)  # 下班的线
    pygame.draw.rect(screen, fill_colour, (left, top, bwidth, bheight))
    font_path = os.path.join(Config.get(
        'resources_path'), Config.get('fontfolder'), 'simkai.ttf')
    font = pygame.font.Font(font_path, font_size)
    text_render = font.render(text, True, font_colour)
    return screen.blit(text_render, (left+50, top+10))  # 画一个按钮


"""开始页面"""  # 出来打的字不同逻辑十分类似


def startInterface(screen):
    '''开始界面'''
    screen.fill(Config.get('bg_color'))
    clock = pygame.time.Clock()
    while True:
        button_0 = BUTTON(screen, (20, 50), '19级自主性发展项目', font_size = 40, bwidth=450)  # 
        button_1 = BUTTON(screen, (95, 200), '开始游戏')  
        button_2 = BUTTON(screen, (95, 345), '退出游戏')
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1.collidepoint(pygame.mouse.get_pos()):  # 碰撞检测
                    return  # 如果点击了开始游戏则退出开始页面逻辑
                elif button_2.collidepoint(pygame.mouse.get_pos()):
                    quitGame()  # 如果点击了退出游戏则执行退出游戏逻辑
        clock.tick(60)
        pygame.display.update()



"""关卡切换界面"""  # 
def switchInterface(screen):
    screen.fill(Config.get('bg_color'))
    clock = pygame.time.Clock()
    while True:
        button_1 = BUTTON(screen, (95, 150), '进入下关')
        button_2 = BUTTON(screen, (95, 305), '退出游戏')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_1.collidepoint(pygame.mouse.get_pos()):
                    return
                elif button_2.collidepoint(pygame.mouse.get_pos()):
                    quitGame()
        clock.tick(60)
        pygame.display.update()



"""结束界面""" 

def endInterface(screen):
    screen.fill(Config.get('bg_color'))
    clock = pygame.time.Clock()
    font_path = os.path.join(Config.get(
        'resources_path'), Config.get('fontfolder'), 'simkai.ttf')
    text_1 = '不愧是你,你必定会成为'
    text_2 = '工商之光!!!'
    font = pygame.font.Font(font_path, 40)
    text1_render = font.render(text_1, 1, (255, 255, 255))
    text2_render = font.render(text_2, 1, (255, 255, 255))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.blit(text1_render, (50, 170))
        screen.blit(text2_render, (130, 270))
        clock.tick(60)
        pygame.display.update()


"""主函数"""
def main():
    pygame.init()  # pygame初始化
    pygame.mixer.init()  # 音效初始化
    pygame.display.set_caption('推箱子小游戏')  # 设置游戏标题
    screen = pygame.display.set_mode(
        [Config.get('WIDTH'), Config.get('HEIGHT')])  # 设置游戏大小
    # 音效
    pygame.mixer.init()  # 初始化音效
    audio_path = os.path.join(Config.get(
        'resources_path'), Config.get('audiofolder'), 'bg.mp3')
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)


    startInterface(screen)
    levels_path = Config.get('levels_path')
    for level_name in sorted(os.listdir(levels_path)):  # 将某路径下的的文件放到一个列表,并且进行排序
        runGame(screen, level_name)  # 某运行一游戏关卡 # level_name 1.level
        switchInterface(screen)  # 切换游戏关卡画面
    endInterface(screen)


"""run"""
if __name__ == '__main__':
    main()
