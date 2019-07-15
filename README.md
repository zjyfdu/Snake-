# Python(pygame) 贪吃蛇

# 使用

```shell
pip3 install requirements.txt
python3 main-bfs2.py
```

# 思路

主要是参考这篇 [实现贪吃蛇AI](http://mp.weixin.qq.com/s?__biz=MzA5ODUxOTA5Mg==&mid=211204280&idx=1&sn=4589891ff2ddff98058f44f3e9dd942e&scene=24&srcid=0923YmTbhMIczvNdLDgrgPMz#rd)，原实现在[这里](https://github.com/Hawstein/snake-ai)，主要的思路是下面这个图

主要的思路是派出一条假蛇去探路，假蛇吃完食物还能活着，真蛇才会去吃（假蛇吃完食物怎么样算能活，这个比较难判断，我的改动也主要在这里，后面会说）

```flow
st=>start: 开始
op_tmp_sanke=>operation: 一条虚拟的蛇探路
cond_food=>condition: 能否到食物
cond_tmp_snake=>condition: 虚蛇和尾巴之间有通路
op_shortest=>operation: 走离食物最短的路
cond_tail=>condition: 蛇和尾巴之间有通路
op_longest=>operation: 走离蛇尾最长的路
cond_move=>condition: 有可行的路
op_dead=>operation: 你死了
e=>end: 结束

st->cond_food
cond_food(yes)->op_tmp_sanke->cond_tmp_snake
cond_food(no)->cond_tail
cond_tmp_snake(yes)->op_shortest
cond_tmp_snake(no)->cond_tail
cond_tail(yes)->op_longest
cond_tail(no)->cond_move
cond_move(yes)->op_shortest
cond_move(no)->op_dead->e

```

# 改动

只是做了一些微小的修改

1. 把curses改为pygame，界面好看多了
2. 加了没有什么卵用的类
3. 假蛇吃到食物之后，怎么算和尾巴之间有通路？
   1. 头和尾相邻算没有通路（原方法），比较保守，走到最后经常会循环起来，不敢吃食
   2. 如果头尾相邻算成有通路，容易在前期就把自己撞死
   3. 没有解决这个问题，加了个判断，蛇默认是保守的，但如果长时间没有吃到食物，就变激进。从测试结果看解决了原有的问题<del>，虽然不优雅</del>

# 待改进

1. 这个算法调起来像无底洞，我应该不会再改进这个了，感觉要加逻辑判断的地方很多，应该会有更优雅的实现
2. 当最后蛇很长的时候，蛇走和食物的最短路径是不合理的，因为走最短路径留下的空隙很可能会被填上食物，还需要绕一大圈才能吃到。应该是到最后，蛇直接一排一排地扫，反而是最快的



