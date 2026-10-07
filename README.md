# Durian-Corner



## 命令行学习记录

- `pwd`：显示当前所在的文件夹。
- `cd`：进入或切换文件夹。
- `ls`：列出当前文件夹中的文件。我运行后看到了项目里的三个文件。
- `mkdir`：新建文件夹。
- `git status`：查看当前分支和文件修改状态。

## 分支与合并

分支是从项目当前版本分出的一条独立开发线；合并是把这条开发线上的修改整合回另一条分支。
我在main上建立了practice/branch-rehearsal，接着在分支上提交修改并且最后整合回main

## 贪吃蛇游戏

打开项目中的 `snake.html`，即可在浏览器中游玩，无需安装其他工具。

- 使用方向键或 WASD 控制蛇移动。
- 吃到食物后得分增加，蛇身变长。
- 撞到墙壁或蛇身后，游戏结束。
- 点击“切换主题”可以更改页面主题。

### AI 自动游玩

点击“AI自动玩”，蛇会沿着覆盖整个棋盘的循环路线移动，自动寻找食物并得分。AI 得到 15 分后会停止。

## 许可证

贪吃蛇游戏代码（`snake.html`）采用 MIT 许可证。该许可仅适用于 `snake.html`，不适用于 `README.md`、个人简介 PDF 或仓库中的其他文件。详见 `LICENSE`。

### AI 信息查证记录

- 日期与问题：十月三号；我问“我没有明白为什么要将startButton改成startBtn，当时在给贪吃蛇游戏接上开始按钮功能。
- AI 的原话：建议给开始按钮添加 `id="startBtn"`，示例为 `<button id="startBtn">开始游戏</button>`。
- 我用什么资料或实验查证：检查 `snake.html`，并查阅 [MDN：Document.getElementById()](https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById)。
- 我实际观察到的证据：`snake.html` 第 114 行按钮的 ID 是 `startButton`，第 250 行脚本也用 `getElementById("startButton")` 查找它。
- 我的判断：这条建议不适用于当时的代码。如果只把按钮 ID 改为 `startBtn`，脚本仍按 `startButton` 查找，就会找不到按钮。
- 这次查证让我学到什么：HTML 元素的 ID 和脚本查找时使用的 ID 必须一致。