# Sinote Editor

***English (United States)*** | [**中文（简体）**](README/README_CN.md)

## Introduction
![Python 3.14](https://img.shields.io/badge/Python-3.14-green) ![PySide6 6.10](https://img.shields.io/badge/PySide6-6.10-blue) ![Style Material](https://img.shields.io/badge/Style-Material%20Style-purple) ![Last Release](https://img.shields.io/badge/Last%20Release-0.06.25542-green)

Sinote [ˈsaɪnoʊt] is an ***Open Source*** Project with **PySide6** and more.<br>
This project *import* ***Customize Plugin System***! Please skip ``<project dir>/documentation/pluginEdit``.<br>
Meaning of **Sinote**: **SI**mple **N**ative P**O**r**T**able **E**ditor. That is Simple Native Portable Editor.<br>
We preferred you use these OS.
 - Windows **Vista** and above. (Windows 10 and lower might install VC Runtime.)
 - Linux with **Python**. (Of course you can run binary file.)
 - Mac OS X with **Python**. (Never tried binary file of macOS)

Or you also can use ```--bypass-system-check``` to bypass check.

## How to Install

Sinote is a **CROSS-PLATFORM** software
<br>You only need open Release and download latest one, then you only need extract and run Sinote(.exe).
<br>
<br>You also can clone it and make like this.
```shell
git clone https://github.com/Win12Home/Sinote.git
cd Sinote/
make build_all # If you can run Pyinstaller
rm -rf ./temporary # Remove Temporary, ~20MiB
cd ./make-temporary # Binary file, ~150MiB
./Sinote #--bypass-system-check
```
Especially, you can run it directly
```shell
git clone https://github.com/Win12Home/Sinote.git
cd Sinote/
make requirement # Install requirement
python main.py #--bypass-system-check
```

## Author Information

**Name:** Win12Home<br>
**Realistic Name:** Wang<br>
**Study in**: Longquan Primary School<br>
**Grade**: Grade 6 in Primary School