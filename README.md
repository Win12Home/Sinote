# Sinote Editor

***English (United States)*** | [**中文（简体）**](README/README_CN.md)

## Introduction
![Python Support](https://img.shields.io/badge/Python%20Support-3.12%20to%203.14-green) ![PySide6 6.10](https://img.shields.io/badge/PySide6-6.10-blue) ![Style Material](https://img.shields.io/badge/Style-Material%20Style-purple) ![Last Release](https://img.shields.io/badge/Last%20Release-0.06.26001-green) ![Develop Status](https://img.shields.io/badge/Develop%20Status-Pre%20Release-blue)

Sinote [ˈsaɪnoʊt] is an ***Open Source*** Project with **PySide6** and more.<br>
This project *import* ***Customize Plugin System***! Please skip ``/Documentation/pluginEdit``.<br>
Meaning of **Sinote**: **SI**mple **N**ative P**O**r**T**able **E**ditor. That is Simple Native Portable Editor.<br>
We preferred you use these OS.
 - Windows **Vista** and above. (Windows 10 and lower might install VC Runtime.)
 - Linux with **Python**. (Of course you can run binary file.)
 - Mac OS X with **Python**. (I never tried binary file of macOS, can you try?)

Or you also can use ```--bypass-system-check``` to bypass check.

## How to Install

You only need to download the latest release. <br>
You also can make and run it. <br>
```bash
git clone https://github.com/Win12Home/Sinote ./Sinote --depth=1
cd ./Sinote/
PYTHON_PATH="/bin/python" make   # Pyinstaller build, only tested in GNU/Linux
# Also you can build with NUITKA: PYTHON_PATH="/bin/python" make nuitka
cd make-temporary/
./Sinote   # Same name from Pyinstaller and Nuitka
```
Or you can run it through Python. <br>
```bash
git clone https://github.com/Win12Home/Sinote ./Sinote --depth=1
cd ./Sinote/
PYTHON_PATH="/bin/python" make requirements    # Install requirements, also you can run 'pip install -r requirements.txt'
/bin/python main.py   # Run Sinote
# You also can run shell script
# cd ./shell
# ./run.sh    # Windows User use run.cmd
```
## Contributing

Look `CONTRIBUTING.md` in the root directory

<!--## Author Information-->

<!--滚木-->

