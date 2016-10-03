# Python(pygame) 贪吃蛇

main.py 100行代码的贪吃蛇


![image](https://raw.githubusercontent.com/codetask/Snake-/master/1.png)

main_bfs.py 通过BFS自动规划到食物的最短路径
但是蛇身太长之后很容易找不到路径而死掉


main_bfs2.py [实现贪吃蛇AI](http://mp.weixin.qq.com/s?__biz=MzA5ODUxOTA5Mg==&mid=211204280&idx=1&sn=4589891ff2ddff98058f44f3e9dd942e&scene=24&srcid=0923YmTbhMIczvNdLDgrgPMz#rd)，按照这个思路进行修改。[code here](https://github.com/Hawstein/snake-ai)

只是做了一些微小的修改，把curses改为pygame

to do list

1. 蛇走过的路径看不清
2. 可能会出现死循环
