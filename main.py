# coding: utf-8

import pygame
import sys
from random import randint, seed

seed(1)

class SnakeConf(object):
    # 蛇运动的场地长宽
    HEIGHT, WIDTH = 20, 20
    LINE_WIDTH = 25
    LINE_MARGIN = 4
    LINE_TRUEWIDTH = LINE_WIDTH - 2 * LINE_MARGIN
    SCREEN_X, SCREEN_Y = LINE_WIDTH * HEIGHT, LINE_WIDTH * WIDTH
    FIELD_SIZE = HEIGHT * WIDTH

    # 用来代表不同东西的数字，由于矩阵上每个格子会处理成到达食物的路径长度，
    # 因此这三个变量间需要有足够大的间隔(>HEIGHT*WIDTH)
    FOOD, UNDEFINED = 0, (HEIGHT + 1) * (WIDTH + 1)
    SNAKE = 2 * UNDEFINED

    LEFT, RIGHT, UP, DOWN = -1, 1, -WIDTH, WIDTH

    # 错误码
    ERR = SNAKE

    BG_COLOR = (255, 255, 255)
    SNAKE_COLOR = (136, 0, 21)
    FOOD_COLOR = (20, 220, 39)


class Snake(object):

    def __init__(self):

        # 用一维数组来表示二维的东西
        # board表示蛇运动的矩形场地
        # 初始化蛇头在(1,1)的地方，第0行，HEIGHT行，第0列，WIDTH列为围墙，不可用
        # 初始蛇长度为1
        self.board = [0] * SnakeConf.FIELD_SIZE
        self.snake = [0] * (SnakeConf.FIELD_SIZE + 1)
        self.snake[0] = 1 * SnakeConf.WIDTH + 1
        self.snake_size = 1

        self.desperate = False

        # 与上面变量对应的临时变量，蛇试探性地移动时使用
        self.tmpboard = [0] * SnakeConf.FIELD_SIZE
        self.tmpsnake = [0] * (SnakeConf.FIELD_SIZE + 1)
        self.tmpsnake[0] = 1 * SnakeConf.WIDTH + 1
        self.tmpsnake_size = 1

        # food:食物位置(0~FIELD_SIZE-1),初始在(3, 3)
        self.food = 3 * SnakeConf.WIDTH + 3

        # 运动方向数组
        self.mov = [SnakeConf.LEFT, SnakeConf.RIGHT, SnakeConf.UP, SnakeConf.DOWN]

        self.desperate = False

    def show_text(self, screen, pos, text, color, font_bold = False, font_size = 60, font_italic = False):
        #获取系统字体，并设置文字大小
        cur_font = pygame.font.SysFont("宋体", font_size)
        #设置是否加粗属性
        cur_font.set_bold(font_bold)
        #设置是否斜体属性
        cur_font.set_italic(font_italic)
        #设置文字内容
        text_fmt = cur_font.render(text, 1, color)
        #绘制文字
        screen.blit(text_fmt, pos)

    def is_cell_free(self, idx, psize, psnake):
        # 检查一个cell有没有被蛇身覆盖，没有覆盖则为free，返回true
        return not (idx in psnake[:psize])

    # 检查某个位置idx是否可向move方向运动
    def is_move_possible(self, idx, move):
        flag = False
        if move == SnakeConf.LEFT:
            flag = idx % SnakeConf.WIDTH > 1
        elif move == SnakeConf.RIGHT:
            flag = idx % SnakeConf.WIDTH < (SnakeConf.WIDTH - 2)
        elif move == SnakeConf.UP:
            flag = idx > (2 * SnakeConf.WIDTH - 1) # 即idx/WIDTH > 1
        elif move == SnakeConf.DOWN:
            flag = idx < (SnakeConf.FIELD_SIZE - 2 * SnakeConf.WIDTH) # 即idx/WIDTH < HEIGHT-2
        return flag

    # 重置board
    # board_refresh后，UNDEFINED值都变为了到达食物的路径长度
    # 如需要还原，则要重置它
    def board_reset(self, psnake, psize, pboard):
        for i in range(SnakeConf.FIELD_SIZE):
            if i == self.food:
                pboard[i] = SnakeConf.FOOD
            elif self.is_cell_free(i, psize, psnake): # 该位置为空
                pboard[i] = SnakeConf.UNDEFINED
            else: # 该位置为蛇身
                pboard[i] = SnakeConf.SNAKE
    
    # 广度优先搜索遍历整个board，
    # 计算出board中每个非SNAKE元素到达食物的路径长度
    # 返回当前能否到达食物
    def board_refresh(self, pfood, psnake, pboard):
        queue = []
        queue.append(pfood)
        inqueue = [0] * SnakeConf.FIELD_SIZE #inque表示是否检查过这个点
        found = False
        # while循环结束后，除了蛇的身体，
        # 其它每个方格中的数字代码从它到食物的路径长度
        while len(queue) != 0:
            idx = queue.pop(0)
            if inqueue[idx] == 1:
                continue
            inqueue[idx] = 1
            for move in self.mov:
                if self.is_move_possible(idx, move):
                    if idx + move == psnake[0]:
                        found = True
                    if pboard[idx+move] < SnakeConf.SNAKE: # 如果该点不是蛇的身体
                        if pboard[idx + move] > pboard[idx] + 1:
                            pboard[idx + move] = pboard[idx] + 1
                        if inqueue[idx + move] == 0:
                            queue.append(idx + move)

        return found

    # 从蛇头开始，根据board中元素值，
    # 从蛇头周围4个领域点中选择最短路径
    def choose_shortest_safe_move(self, psnake, pboard):
        best_move = SnakeConf.ERR
        min = SnakeConf.UNDEFINED
        for move in self.mov:
            if self.is_move_possible(psnake[0], move) \
                    and pboard[psnake[0] + move] < min:
                min = pboard[psnake[0] + move]
                best_move = move
        return best_move

    # 从蛇头开始，根据board中元素值，
    # 从蛇头周围4个领域点中选择最远路径
    def choose_longest_safe_move(self, psnake, pboard):
        best_move = SnakeConf.ERR
        max = -1
        for move in self.mov:
            if self.is_move_possible(psnake[0], move) \
                    and max < pboard[psnake[0] + move] < SnakeConf.UNDEFINED:
                max = pboard[psnake[0] + move]
                best_move = move
        return best_move

    # 检查是否可以追着蛇尾运动，即蛇头和蛇尾间是有路径的
    # 为的是避免蛇头陷入死路
    # 虚拟操作，在tmpboard,tmpsnake中进行
    def is_tail_inside(self):
        self.tmpboard[self.tmpsnake[self.tmpsnake_size - 1]] = SnakeConf.FOOD # 虚拟地将蛇尾变为食物(因为是虚拟的，所以在tmpsnake,tmpboard中进行)
        self.tmpboard[self.food] = SnakeConf.SNAKE # 放置食物的地方，看成蛇身
        result = self.board_refresh(self.tmpsnake[self.tmpsnake_size-1], self.tmpsnake, self.tmpboard) # 求得每个位置到蛇尾的路径长度
        if not result: # 如果没有路直接返回
            return False

        if self.desperate:
            result = False
            for move in self.mov: # 如果蛇头和蛇尾紧挨着，则返回False。即不能follow_tail，追着蛇尾运动了
                if self.is_move_possible(self.tmpsnake[0], move) \
                        and self.tmpsnake[0] + move != self.tmpsnake[self.tmpsnake_size - 1]: # \
                    result = True
                else:
                    self.tmpboard[self.tmpsnake[0] + move] = SnakeConf.UNDEFINED # 不符合
        else: #蛇绝望前，走得比较保守，只要蛇头和蛇尾挨着，就不走
            for move in self.mov: # 如果蛇头和蛇尾紧挨着，则返回False。即不能follow_tail，追着蛇尾运动了
                if self.is_move_possible(self.tmpsnake[0], move) \
                        and self.tmpsnake[0] + move == self.tmpsnake[self.tmpsnake_size - 1] \
                        and self.tmpsnake_size > 3: # 如果不限制3的话，长度为1的蛇就不会再吃，seed(101)
                    result = False

        return result

    # 让蛇头朝着蛇尾运行一步
    # 不管蛇身阻挡，朝蛇尾方向运行
    def follow_tail(self):
        self.tmpsnake_size = self.snake_size
        self.tmpsnake = self.snake[:]
        self.board_reset(self.tmpsnake, self.tmpsnake_size, self.tmpboard) # 重置虚拟board
        self.tmpboard[self.tmpsnake[self.tmpsnake_size - 1]] = SnakeConf.FOOD # 让蛇尾成为食物
        self.tmpboard[self.food] = SnakeConf.SNAKE # 让食物的地方变成蛇身
        self.board_refresh(self.tmpsnake[self.tmpsnake_size - 1], self.tmpsnake, self.tmpboard) # 求得各个位置到达蛇尾的路径长度
        self.tmpboard[self.tmpsnake[self.tmpsnake_size - 1]] = SnakeConf.SNAKE # 还原蛇尾

        return self.choose_longest_safe_move(self.tmpsnake, self.tmpboard) # 返回运行方向(让蛇头运动1步)

    # 在各种方案都不行时，随便找一个可行的方向来走(1步),
    def any_possible_move(self):
        best_move = SnakeConf.ERR
        self.board_reset(self.snake, self.snake_size, self.board)
        self.board_refresh(self.food, self.snake, self.board)
        min = SnakeConf.SNAKE

        for move in self.mov:
            if self.is_move_possible(self.snake[0], move) \
                    and self.board[self.snake[0] + move] < min:
                min = self.board[self.snake[0] + move]
                best_move = move
        return best_move

    def shift_array(self, arr, size):
        arr[1:size + 1] = arr[:size]

    def new_food(self):
        while True:
            w = randint(1, SnakeConf.WIDTH-2)
            h = randint(1, SnakeConf.HEIGHT-2)
            food = h * SnakeConf.WIDTH + w
            cell_free = self.is_cell_free(food, self.snake_size, self.snake)
            if cell_free:
                self.food = food
                return

    # 真正的蛇在这个函数中，朝pbest_move走1步
    def make_move(self, pbest_move):
        self.shift_array(self.snake, self.snake_size)
        self.snake[0] += pbest_move

        # 如果新加入的蛇头就是食物的位置
        # 蛇长加1，产生新的食物，重置board(因为原来那些路径长度已经用不上了)
        if self.snake[0] == self.food:
            self.board[self.snake[0]] = SnakeConf.SNAKE # 新的蛇头
            self.snake_size += 1
            if self.snake_size < SnakeConf.FIELD_SIZE:
                self.new_food()
        else: # 如果新加入的蛇头不是食物的位置
            self.board[self.snake[0]] = SnakeConf.SNAKE # 新的蛇头
            self.board[self.snake[self.snake_size]] = SnakeConf.UNDEFINED # 蛇尾变为空格

    # 虚拟地运行一次，然后在调用处检查这次运行可否可行
    # 可行才真实运行。
    # 虚拟运行吃到食物后，得到虚拟下蛇在board的位置
    def virtual_shortest_move(self):
        self.tmpsnake_size = self.snake_size
        self.tmpsnake = self.snake[:] # 如果直接tmpsnake=snake，则两者指向同一处内存
        self.tmpboard = self.board[:] # board中已经是各位置到达食物的路径长度了，不用再计算
        self.board_reset(self.tmpsnake, self.tmpsnake_size, self.tmpboard)

        food_eated = False
        while not food_eated:
            self.board_refresh(self.food, self.tmpsnake, self.tmpboard)
            move = self.choose_shortest_safe_move(self.tmpsnake, self.tmpboard)
            self.shift_array(self.tmpsnake, self.tmpsnake_size)
            self.tmpsnake[0] += move # 在蛇头前加入一个新的位置
            # 如果新加入的蛇头的位置正好是食物的位置
            # 则长度加1，重置board，食物那个位置变为蛇的一部分(SNAKE)
            if self.tmpsnake[0] == self.food:
                self.tmpsnake_size += 1
                self.board_reset(self.tmpsnake, self.tmpsnake_size, self.tmpboard) # 虚拟运行后，蛇在board的位置(label101010)
                self.tmpboard[self.food] = SnakeConf.SNAKE
                food_eated = True
            else: # 如果蛇头不是食物的位置，则新加入的位置为蛇头，最后一个变为空格
                self.tmpboard[self.tmpsnake[0]] = SnakeConf.SNAKE
                self.tmpboard[self.tmpsnake[self.tmpsnake_size]] = SnakeConf.UNDEFINED

    def draw_snake(self, screen):
        left = (self.snake[0] // SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2 # margin 2
        top = (self.snake[0] % SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2
        rect = pygame.Rect(left, top, SnakeConf.LINE_TRUEWIDTH, SnakeConf.LINE_TRUEWIDTH)
        pygame.draw.rect(screen, SnakeConf.SNAKE_COLOR, rect, 0)
        for i in range(1, self.snake_size):
            left_pre = (self.snake[i - 1] // SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2 # margin 2
            top_pre = (self.snake[i - 1] % SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2
            left = (self.snake[i] // SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2 # margin 2
            top = (self.snake[i] % SnakeConf.WIDTH) * SnakeConf.LINE_WIDTH + 2
            if (top_pre == top):
                rect = pygame.Rect(min(left, left_pre), top, SnakeConf.LINE_TRUEWIDTH + SnakeConf.LINE_WIDTH, SnakeConf.LINE_TRUEWIDTH)
            else:
                rect = pygame.Rect(left, min(top, top_pre), SnakeConf.LINE_TRUEWIDTH, SnakeConf.LINE_TRUEWIDTH + SnakeConf.LINE_WIDTH)
            pygame.draw.rect(screen, SnakeConf.SNAKE_COLOR, rect, 0)

    def main(self):
        pygame.init()
        screen = pygame.display.set_mode((SnakeConf.SCREEN_X, SnakeConf.SCREEN_Y))
        pygame.display.set_caption('Snake')
        clock = pygame.time.Clock()

        isdead = False

        dead_loop = 0
        pre_score = 0

        pause = False
        onestep = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pause = not pause
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    onestep = True

            if pause and not onestep:
                continue

            onestep = False

            screen.fill(SnakeConf.BG_COLOR)

            self.draw_snake(screen)

            rect = pygame.Rect((self.food//SnakeConf.WIDTH)*SnakeConf.LINE_WIDTH + 2,(self.food%SnakeConf.WIDTH)*SnakeConf.LINE_WIDTH +2 ,SnakeConf.LINE_TRUEWIDTH, SnakeConf.LINE_TRUEWIDTH)
            pygame.draw.rect(screen,SnakeConf.FOOD_COLOR,rect,0)

            # 重置矩阵
            self.board_reset(self.snake, self.snake_size, self.board)

            # 如果蛇可以吃到食物，board_refresh返回true
            # 并且board中除了蛇身(=SNAKE)，其它的元素值表示从该点运动到食物的最短路径长
            if self.board_refresh(self.food, self.snake, self.board):
                # 虚拟地运行一次，因为已经确保蛇与食物间有路径，所以执行有效
                # 运行后得到虚拟下蛇在board中的位置，即tmpboard
                self.virtual_shortest_move()  # 该函数唯一调用处，在虚拟的board
                if self.is_tail_inside():  # 如果虚拟运行后，蛇头蛇尾间有通路，则选最短路运行(1步)
                    best_move = self.choose_shortest_safe_move(self.snake, self.board)
                else:
                    best_move = self.follow_tail()  # 否则虚拟地follow_tail 1步，如果可以做到
            else:
                best_move = self.follow_tail()

            if best_move == SnakeConf.ERR:
                best_move = self.any_possible_move()
            # 上面一次思考，只得出一个方向，运行一步
            if best_move != SnakeConf.ERR:
                self.make_move(best_move)
            else:
                isdead = True

            if isdead:
                self.show_text(screen,(100,200),'YOU DEAD!',(227,29,18), False, 100)
                self.show_text(screen,(150,260),'press space to try again...',(0,0,22), False, 30)

            # 显示分数文字
            self.show_text(screen,(50,500),'Scores: '+str(self.snake_size),(223,223,223))

            pygame.display.update()
            if (self.snake_size == pre_score):
                dead_loop += 1
            else:
                dead_loop = 0
            if dead_loop > SnakeConf.FIELD_SIZE:
                self.desperate = True # 蛇绝望了
                print('desperate')
            pre_score = self.snake_size

            clock.tick(100) # 这里调的是帧律
    
    
if __name__ == '__main__':
    snake1 = Snake()
    snake1.main()
