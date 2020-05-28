import os
import pygame
from config import Config



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