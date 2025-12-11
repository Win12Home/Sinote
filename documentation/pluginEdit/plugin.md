# Sinote Plugin Tutorial
**Sinote Documentation,** by <span style="color:blue;">**Win12Home**</span> 2025, written in Markdown.

![Sinote API Version Support](https://img.shields.io/badge/Sinote%20API%20Support-1.0.1-green) ![Python Supports](https://img.shields.io/badge/Python-3.14-blue?logo=python)

---

## 1 Introduction
Welcome to **Sinote Developer World**!<br>

> 💡 **Tips**: The *pluginEdit* documentation isn't included in the normal binary distribution. If you're reading this, you're **definitely on GitHub**!

**Plugin** is an **Important feature** in Sinote Editor, it has given developer an entry to add **Something new** to Sinote Editor.
<br>
The struct is like this.
```text
plugins/YourProject:
    headers/
           | header1.si_plug_h
           | header2.sph
           | header3.sp_header (Not recommend)
    info/
        | icon.png (Must a PNG)
        | LICENSE  (Not a necessary item)
        | docs.md  (Not a necessary item)
    info.json      (or info.json5)
    imports.txt    (Necessary item, use to import header files)
```
<br>
This Doc will **teach** you **HOW TO CREATE A MAIN FILE OF SINOTE PLUGIN**!

## 2 Write ```info.json``` and apply your LOGO/ICON of your Plugin

``info.json`` is a JSON5 File in the root of your project.
<br>
It gives an information of your plugin to **Sinote**.
<br>There is a struct of ``info.json``
```json5
{
  "icon": "%pluginPath%/icon/icon.png",  // Always use SinoteVariableInString
  "name": "Plugin", // The plugin name
  "objectName": "sample.plugin", // Recommend [a-zA-Z0-9]*+.[a-zA-Z0-9]*, but Sinote won't match
  "version": "1.0.1", // The version string
  "versionIterate": 1, // Means: 1st release, for better plugin update
  "customizeRemoveString": {
    "zh_CN": "自定义删除插件文本",
    "en_US": "Customize Remove String"
  }, // A Customize Remove String
  "author": [
    "Win12Home"
  ], //Authors of Plugin
  "description": "Description" // Description, you can use HTML context. (Automatic set \n to <br>)
}
```
Note: ``info.json`` can't edit to ``info.si_plug`` and similar.

## 3 Write ``imports.txt``

``imports.txt`` is a TXT file for load headers.
<br>There is a sample of ``imports.txt``, please use ``&space;`` to replace Space, like:
```text
python&space;syntax&space;highlighter.sp_header
```
for load ``python syntax highlighter.sp_header``

## 4 End

<!--What am I doing? It's too lite-->
<!--WC了，太短了！！！！！！！！！！！！-->

This is a short documentation.
<br>
It's easy to recognize when you have read ``header.md``.
<br>
Thanks for your patient!