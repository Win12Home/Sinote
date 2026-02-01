# Sinote Editor

## 介绍
![支持的Python版本](https://img.shields.io/badge/支持Python-3.12%20to%203.14-green) ![PySide6 6.10](https://img.shields.io/badge/PySide6版本-6.10-blue) ![Material主题](https://img.shields.io/badge/界面主题-Material%20Style-purple) ![最新版本](https://img.shields.io/badge/最新版本-0.06.26014-green) ![开发进展](https://img.shields.io/badge/开发进展-预发布版本-blue)

Sinote [ˈsaɪnoʊt] 是一个使用PySide6以及非常多的库的编辑器。<br>
这个项目*引入了****学习简（难）易（懂）的插件系统***! 要学习请跳转到``/Documentation/pluginEdit``.<br>
**Sinote**的意思: **SI**mple **N**ative P**O**r**T**able **E**ditor. 中文意思就是简单原生便携<!--200MB还叫便携？-->编辑器<br>
我们推荐你使用这些系统
 - Windows **Vista** 及以上 (Windows 10及以下可能需要安装VC Runtime)
 - 带**Python**的GNU/Linux*发行版* (你也可以下载编译之后的包)
 - 用Homebrew安装**Python**的macOS X. (你试试编译之后的，我没有苹果电脑)

或者你也可以用```--bypass-system-check```来规避系统检测。<!--卧槽我加系统检测干个集贸啊-->

## 安装方式

你只需要下载最新Release的编译之后的包 <br>
你也可以自己编译并且运行。 <br>
```bash
git clone https://github.com/Win12Home/Sinote ./Sinote --depth=1
cd ./Sinote/
PYTHON_PATH="/bin/python" make   # Pyinstaller构建，我只在GNU/Linux试过哈
# 你也可以用nuitka构建，使用 make nuitka 即可
cd make-temporary/
./Sinote   # Pyinstaller和Nuitka的二进制文件一个名字
```
你也可以直接运行。 <br>
```bash
git clone https://github.com/Win12Home/Sinote ./Sinote --depth=1
cd ./Sinote/
PYTHON_PATH="/bin/python" make requirements    # 安装需求，你也可以运行'pip install -r requirements.txt'
/bin/python main.py   # 运行Sinote
# 你也可以使用shell文件
# cd ./shell
# ./run.sh    # Windows用户请使用run.cmd
```
## 贡献

开游览器翻译看根目录下的`CONTRIBUTING.md`。

<!--我也是个神人-->
