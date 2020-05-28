# 重庆工商大学19级2019~2020年资助性发展项目
# Introduction：
## 游戏简介:
经典的推箱子是一个来自日本的古老游戏，目的是在训练你的逻辑思考能力。在一个狭小的仓库中，要求把木箱放到指定的位置，稍不小心就会出现箱子无法移动或者通道被堵住的情况，所以需要巧妙的利用有限的空间和通道，合理安排移动的次序和位置，才能顺利的完成任务
## 控制方式：
↑↓←→键控制人物行动，r键重新开始本关。

# 环境

``` 
OS: Windows10
Python: Python3.5+(have installed necessary dependencies)
```

# 使用

``` 
Step1:
pip install -r requirements.txt
Step2:
run "python main.py"
```

# 游戏展示

[__点击查看b站视频内容展示__](https://www.bilibili.com/video/BV1ht4y1C7Js#reply2957183458)

# 细节

## 类之间的关系
[![tZBLFO.png](https://s1.ax1x.com/2020/05/28/tZBLFO.png)](https://imgchr.com/i/tZBLFO)


## Step1：定义精灵类
由于游戏涉及到碰撞检测，所以我们先来定义一些游戏精灵类，包括推箱子的人、箱子、墙和目标位置指示标记。
首先我们来定义一下推箱子的人这个精灵类：

``` Python
class pusherSprite(pygame.sprite.Sprite):
    """" 推箱子的精灵类
    需要完成移动和将自己画出来的功能
    Attributes:
    参数:   col: int 保存自己本身在屏幕的位置,及行号和列号
            row: int 
    """
    def __init__(self, col, row):
        pygame.sprite.Sprite.__init__(self)
        self.image_path = os.path.join(Config.get('resources_path'), Config.get('imgfolder'), 'player.png')
        self.image = pygame.image.load(self.image_path).convert() # 
        color = self.image.get_at((0, 0)) # 获取图片最开始那个点的像素值
        self.image.set_colorkey(color, pygame.RLEACCEL) # 设置透明的颜色
        self.rect = self.image.get_rect()
        self.col = col # 自己要被画在哪一行,哪一列
        self.row = row 
    '''移动'''
    def move(self, direction, is_test=False):
        # 测试模式代表模拟移动
        if is_test:
            if direction == 'up':
                return self.col, self.row - 1
            elif direction == 'down':
                return self.col, self.row + 1
            elif direction == 'left':
                return self.col - 1, self.row
            elif direction == 'right':
                return self.col + 1, self.row
        else:
            if direction == 'up':
                self.row -= 1
            elif direction == 'down':
                self.row += 1
            elif direction == 'left':
                self.col -= 1
            elif direction == 'right':
                self.col += 1
    '''将人物画到游戏界面上'''
    def draw(self, screen):
        self.rect.x = self.rect.width * self.col
        self.rect.y = self.rect.height * self.row
        screen.blit(self.image, self.rect)
```

他需要拥有可以移动的能力，这里设置了一个模拟移动的选项，是为了通过模拟移动判断他是否可以向上/下/左/右移动。
因为地图上的其他东西性质类似，所以我们把它们定义成同一个精灵类(T_T其实性质都类似，但是感觉还是有必要区分一下人和物的)：
``` Python
'''
Function:
    游戏元素精灵类
'''
class elementSprite(pygame.sprite.Sprite):
    """" 游戏元素精灵类
    在对应的位置将自己画出来,移动
    Attributes:
    参数: sprite_name: str 精灵种类
          col :int cow: int 精灵自身的位置
    """
    def __init__(self, sprite_name, col, row):
        pygame.sprite.Sprite.__init__(self)
        # 导入box.png/target.png/wall.png
        self.image_path = os.path.join(Config.get('resources_path'), Config.get('imgfolder'), sprite_name)
        self.image = pygame.image.load(self.image_path).convert()
        color = self.image.get_at((0, 0))
        self.image.set_colorkey(color, pygame.RLEACCEL)
        self.rect = self.image.get_rect()
        # 元素精灵类型
        self.sprite_type = sprite_name.split('.')[0]
        # 元素精灵的位置
        self.col = col
        self.row = row
    '''将游戏元素画到游戏界面上'''
    def draw(self, screen):
        self.rect.x = self.rect.width * self.col
        self.rect.y = self.rect.height * self.row
        screen.blit(self.image, self.rect)
    '''移动游戏元素'''
    def move(self, direction, is_test=False):
        if self.sprite_type == 'box':
            # 测试模式代表模拟移动
            if is_test:
                if direction == 'up':
                    return self.col, self.row - 1
                elif direction == 'down':
                    return self.col, self.row + 1
                elif direction == 'left':
                    return self.col - 1, self.row
                elif direction == 'right':
                    return self.col + 1, self.row
            else:
                if direction == 'up':
                    self.row -= 1
                elif direction == 'down':
                    self.row += 1
                elif direction == 'left':
                    self.col -= 1
                elif direction == 'right':
                    self.col += 1
```
其中箱子需要拥有可以移动的能力，其他则不能移动。模拟移动选项的功能与之前类似。

## Step2 : 定义游戏地图类

这里我们定义一个游戏地图类，目的是用该类来创建任意的游戏地图。因此，该类应当可以增加并保存游戏元素(人、墙、箱子等)，并在屏幕上把地图画出来。同时也应当自带一个方法来判断此地图上的箱子是否都已经送到了指定位置(这样子方便切换关卡)：

```python
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

```



## Sept3：**定义游戏界面类**

游戏界面类负责解析levels文件夹下的游戏各关卡的地图文件，并利用游戏地图类创建并显示游戏地图



```python
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
```



## Step4：定义某关的游戏主循环

主循环主要负责实例化游戏界面类，并根据按键检测的结果对游戏界面类进行一些操作：

```python
"""游戏运行"""  # 
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
                if event.key == pygame.K_LEFT:
                    next_pos = game_interface.player.move('left', is_test=True)
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('left')
                    else:
                        box = game_interface.game_map.getBox(*next_pos)
                        if box:
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
```

## Step4: **定义某关的游戏主循环**

主循环主要负责实例化游戏界面类，并根据按键检测的结果对游戏界面类进行一些操作：

```python
"""游戏运行"""  # 
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
                if event.key == pygame.K_LEFT:
                    next_pos = game_interface.player.move('left', is_test=True)
                    if game_interface.game_map.isValidPos(*next_pos):
                        game_interface.player.move('left')
                    else:
                        box = game_interface.game_map.getBox(*next_pos)
                        if box:
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
```

其中人物移动的逻辑为：

人移动的目标位置为空白格，则人移动；若撞到箱子，箱子可以和人方向一样移动一格，则人和箱子均移动；其他情况人和箱子均无法移动。

## Step5: **定义游戏开始、切换和结束界面**

__开始界面__

```python
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

```

__切换页面__

~~~py
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

~~~

__结束界面__

```py
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

```



## Step6: **实现游戏主函数**

把所有界面串起来就好啦

~~~python

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

~~~



![img](./img/开始页面.png)

1. 主要业务逻辑

``` Python
def startInterface(screen):
    '''开始界面'''
    screen.fill(Config.get('bg_color'))
    clock = pygame.time.Clock()
    while True:
        button_1 = BUTTON(screen, (95, 150), '开始游戏')  # TODO 观察button的实现
        button_2 = BUTTON(screen, (95, 305), '退出游戏')
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
```

2. 绘制按钮接口

``` Python
def BUTTON(screen, position, text, bwidth=310, bheight=65):
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
    font_size = 50
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

```

# 一些比较深入的知识点

### 1. 字典中的 dict[key]和dict.get(key)的区别

``` python
dict = {1:"haha",2:"zhazha"}
dict[1] -> haha
dict.get(2) -> zhazha
```

当遇到不存在的key的时候

``` Python
dict = {1:"haha",2:"zhazha"}
dict[0] -> 报错
dict.get(0) -> None
```

### 2. 颜色grb颜色数值越高, 颜色越亮, 在绘制按钮的时候, 通过颜色由浅入深形成立体感

  

### 3. 判断某位置是否可以到达

``` Python
Rect.collidelist()
检测该 Rect 对象是否与列表中的任何一个矩形有交集。
Rect.collidelist(list) -> index
返回值是第 1 个有相交的矩形所在列表中的索引号（如果有的话），否则返回 -1。
```

 

### 4. 迭代器与生产器

* __迭代器__ ：

    像列表，元组，字符串这样的是python内置的可迭代对象
    我们自己也可以定义自己的可迭代对象

    1. 可迭代对象本质：可以向我们提供一个中间“人”即迭代器帮助我们对其进行迭代遍历使用。

    可迭代对象通过__iter__方法向我们提供一个迭代器，我们在迭代一个可迭代对象的时候，实际上就是先获取该对象提供的一个迭代器，然后通过这个迭代器来依次获取对象中的每一个数据.
    2.iter()和next()函数：
        

![tV0AeK.png  ](https://s1.ax1x.com/2020/05/28/tV0AeK.png)

     > iter()函数可以触发可迭代对象的__iter__()获得一个可迭代对象的迭代器
        > exit()函数可以触发可迭代对象的__next__()方法


    3. 实现一个可迭代对象：
    
    > 1. 在iter方法中返回一个迭代器
    > 2. 在迭代器的next方法中实现迭代逻辑
    由于迭代器本身本身也是一个可迭代对象，所以我们一般返回本身


``` Python
    class FibIterator(object):
    """斐波那契数列迭代器"""
    def __init__(self, n):
        """
        :param n: int, 指明生成数列的前n个数
        """
        self.n = n
        # current用来保存当前生成到数列中的第几个数了
        self.current = 0
        # num1用来保存前前一个数，初始值为数列中的第一个数0
        self.num1 = 0
        # num2用来保存前一个数，初始值为数列中的第二个数1
        self.num2 = 1

    def __next__(self):
        """被next()函数调用来获取下一个数"""
        if self.current < self.n:
            num = self.num1
            self.num1, self.num2 = self.num2, self.num1+self.num2
            self.current += 1
            return num
        else:
            raise StopIteration

    def __iter__(self):
        """迭代器的__iter__返回自身即可"""
        return self

if __name__ == '__main__':
    fib = FibIterator(10)
    for num in fib:
        print(num, end=" ")
```

__生成器__: 生成器是一个特殊的迭代器
要创建一个生成器，有很多种方法。第一种方法很简单，只要把一个列表生成式的 [ ] 改成 ( )：
``` Python
In [1]: L = [ x*2 for x in range(5)]
In [2]: L
Out[3]: [0, 2, 4, 6, 8]

In [4]: G = ( x*2 for x in range(5))
In [18]: G
Out[18]: <generator object <genexpr> at 0x7f626c132db0>

```
创建 L 和 G 的区别仅在于最外层的 [ ] 和 ( ) ， L 是一个列表，而 G 是一个生成器。我们可以直接打印出列表L的每一个元素，而对于生成器G，我们可以按照迭代器的使用方法来使用，即可以通过next()函数、for循环、list()等方法使用。生成器就像一个方法,列表是把成品放到那里去了,所以生成器占用内存要小很多
``` Python
In [19]: next(G)
Out[19]: 0

In [20]: next(G)
Out[20]: 2

In [21]: next(G)
Out[21]: 4

In [22]: next(G)
Out[22]: 6

In [23]: next(G)
Out[23]: 8

In [24]: next(G)
---------------------------------------------------------------------------
StopIteration                             Traceback (most recent call last)
<ipython-input-24-380e167d6934> in <module>()
----> 1 next(G)

StopIteration:

In [25]:
```
``` Python
In [26]: G = ( x*2 for x in range(5))

In [27]: for x in G:
   ....:     print(x)
   ....:     
0
2
4
6
8

```
😘
__简单的生成器实现__
``` Python
 def fib(n):
   ....:     current = 0
   ....:     num1, num2 = 0, 1
   ....:     while current < n:
   ....:         num = num1
   ....:         num1, num2 = num2, num1+num2
   ....:         current += 1
   ....:         yield num
   ....:     return 'done'
   ....:

In [31]: F = fib(5)

In [32]: next(F)
Out[32]: 1

In [33]: next(F)
Out[33]: 1

In [34]: next(F)
Out[34]: 2

In [35]: next(F)
Out[35]: 3

In [36]: next(F)
Out[36]: 5

In [37]: next(F)
---------------------------------------------------------------------------
StopIteration                             Traceback (most recent call last)
<ipython-input-37-8c2b02b4361a> in <module>()
----> 1 next(F)

StopIteration: done
```
在使用生成器实现的方式中，我们将原本在迭代器__next__方法中实现的基本逻辑放到一个函数中来实现，但是将每次迭代返回数值的return换成了yield，此时新定义的函数便不再是函数，而是一个生成器了。简单来说：__只要在def中有yield关键字的 就称为 生成器__
__总结__:
- 使用了yield关键字的函数不再是函数，而是生成器。（使用了yield的函数就是生成器）
- yield关键字有两点作用：
    - 保存当前运行状态（断点），然后暂停执行，即将生成器（函数）挂起
    - 将yield关键字后面表达式的值作为返回值返回，此时可以理解为起到了return的作用
- 可以使用next()函数让生成器从断点处继续执行，即唤醒生成器（函数）
- Python3中的生成器可以使用return返回最终运行的返回值，而Python2中的生成器不允许使用return返回一个返回值（即可以使用return从生成器中退出，但return后不能有任何表达式）。

__在游戏中__:
    [![tVIuE4.png](https://s1.ax1x.com/2020/05/28/tVIuE4.png)](https://imgchr.com/i/tVIuE4)
    这样我们就能够遍历出所有的可迭代对象,并且占用内存还比较少
    如果直接遍历,需要把所有的精灵都加载到内存是非常不明智的做法

4. 透明度分析

Pygame支持三种类型的透明度分析：colorkeys，surface alphas 和 pixel alphas

* colorkeys 指定一种颜色, 让它变为透明
* surface alphas 给整体设置一个透明度
* pixel alphas 给每个像素点设置一个alphas通道, 让图片支持透明通道

convert() 转换的图片可以支持colorkeys和surface
convert_alpha() 转换后的图片可以支持 pixel alphas

5. Surface.get_at(x,y) -> Color:

> 返回该点（x, y）下的Color对象 --> 可用于设置透明颜色值
