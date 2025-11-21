# Create Header (.si_plug_h, .sph)
**Sinote Documentation,** by <span style="color:blue;">**Win12Home**</span> 2025, written in Markdown. 

---

# 1 Basic Headers

## 1.1 Introduction

Welcome to use Sinote Documentation!<br>
This Documentation supports Sinote API Version 1.<br>
<br>
**Plugin** is an **Important feature** in Sinote Editor, it has given developer an entry to add **Something new** to Sinote Editor.
<br>
Headers almost are the sub-plugin of the main plugin.
<br>
They always put in ```./headers/``` directory
<br>
This Doc will **teach** you **HOW TO CREATE A HEADER OF SINOTE PLUGIN**!
___
## 1.2 Define a Plugin Header
### 1.2.1 Create a Sinote Plugin Header File
> **<span style="color:red;font-style:oblique">&#x26a0;&#xfe0f; IMPORTANT NOTICE:</span> Please learn JSON or JSON5 Language if you haven't learnt before!**<br>
> Learn [here](https://www.json.org "Skip to JSON.ORG website")

First, you need to create a <strong>JSON File</strong> like this.<br>
```json5
{
  "config": {
    "type": 0,  // 0: Just a Placeholder; 1: Code Highlighter; 2: Complex Runner Define
    "api": [1,1], // Means API Version 1 to API Version 1
    "enableCustomizeCommandRun": false, // Enable Customize Command to run
    "useSinoteVariableInString": true, // Use Sinote Variable, look at variable.md to learn
    "objectName": "a_test_obj"
  },
  "coding": {
    // Coding there
  }
}
```
This is a base of Sinote Plugin Header aka ***SPH***.
> &#x2139;&#xfe0f; **Note**<br>
> Naturally, you need to rename your file extension to **(.si_plug_h, .sph)** when you've written it.<br>
> Such as linux: **(If you are using Vim or other editor in Terminal)**
> ```shell 
> mv (Your file) (Your file name).sph
> ```
> Windows:
> ```shell
> rename (Your file) (Your file name).sph
> ```
> If you know what is the definitions of **SPH Configuration**, skip 1.2.2!
### 1.2.2 Config your Sinote Plugin Header
If you didn't know anything about **SPH Configuration**, look at this page.<br>
Here are the definitions of configuration of Sinote Plugin Header:
 - ```type```: 0: Just for settings and other; 1: Code Highlighter; 2: Complex Runner Define
 - ```api```: \[*\<Minimum Support API Version\>*, *\<Maximum Support API Version\>*\]
 - ```enableCustomizeCommandRun```: boolean (false or true), A Dangerous Selection, when you open it, you can run Customize Command.
 - ```useSinoteVariableInString```: also boolean, look at variable.md to learn.
 - ```objectName```: string, needed to write. (Showed objectName is objectName of main plugin file (.sp, .si_plug) append objectName of this. like (Main: sinote.plugin, Header: headerActivity, Show name: sinote.plugin.headerActivity)

Not required configuration:
 - ```excClose```: Exception Close, true is default, if true, when error occurred, stop load it. if false, when error occurred, use sys.**\_\_excepthook\_\_**.
___
## 1.3 Coding in Plugin Header
### 1.3.1 Code Highlighter (Type equals one)
> &#x2139;&#xfe0f; **Note**<br>
> Primary Programming Language Code Highlighter's code is in /root/of/sinote/**resources/plugins/sinote.official.codeHighlighter**<br>
> You can copy one and learn from it.
> <br><br>Naturally, we recommend reading ```function.md``` at first.

In the official plugin *(objName: ```sinote.official.codeHighlighter```)* gives you the syntaxHighlight of Python, CPL, C++.
<br>You can write a Sinote Plugin Header for syntaxHighlight about your liked programming language. (Like Kotlin, Java, Pascal, HTML5, CSS, JavaScript etc.)<br>
A example of Python:
```json5
{
  "config": {
    // Configuration
  },
  "coding": {
    "codeName": "Python 3",
    "fileExtension": ["py","pyi"],
    "keywords": [/* Keywords of Python, like raise, async etc */],
    "symbols": [/* Symbols, like , . ^ & */],
    "remKeywords": ["#"],
    "remKeywordsLikeString": ["\"\"\""],
    "enableSelfColorOfRemKeywordsLikeString": false, //"""<text>""" also can use for str
    "textKeywords": ["'","\""]
    
  }
}
```

**Definitions of coding:**

 - ```codeName```: str, name of programming language.
 - ```fileExtension```: list, appendix or extension of file.
 - ```keywords```: list, the keywords like static, void, protect, private etc.
 - ```symbols```: list, the symbols like ```,``` ```\\``` etc.
 - ```remKeywords```: list, the symbols like ```#```(Python) ```//``` (C++, Java, CPL etc.) etc.
 - ```remKeywordsLikeString```: list, the symbols like ```"""``` (Only Python)
 - ```enableSelfColorOfRemKeywordsLikeString```: boolean, ```"""``` in Python can be used for String, so it need to write false.
 - ```textKeywords```: list, the symbols like ```'' , ""``` (Only One-character)

> **<span style="color:red;font-style:oblique">&#x26a0;&#xfe0f; IMPORTANT NOTICE:</span> The all the selection is required!**
> <br>Excepted ```enableSelfColorOfRemKeywordsLikeString``` selection. (Always false)

### 1.3.2 Complex Runner Define (type equals two)

> **&#x2139;&#xfe0f; NOTICE:**
> Runner Define is very important for Your Customize Programming Language or a Programming Language that Sinote not support.
> <br>
> If this documentation cannot give you an ***EASY WAY TO CREATE IT***, please give me an issue in GitHub.

It's difficult to create a Runner or Compiler Define for a pre-learner.<br>
<br> This is an example for C++<br>
**./headers/cpp.sph**
```json5
{
  "config": {
    "type": 2,
    "api": [1,1],
    //"enableCustomizeCommandRun": true,       (Default is true)
    //"useSinoteVariableInString": true,       (Default is true)
    "objectName": "cppRunnerDefine"
  },
  "functions": { // Learn in function.md
    "compileFunc": [
      ["system","%giveCompiler% %argumentOfCompiler% %originalFile% -o %pathOfFile%/%fileNameWithoutAppendix%.%binAppendix%",{"out2term": true}], // look at func.md to see function
    ],
    "runFunc": [
      ["system","cd %pathOfFile% && %fileNameWithoutAppendix%.%binAppendix% %argumentOfRunner%"]
    ]
  },
  "coding": {
    "codeName": "C++",
    "fileExtension": [".cpp",".cxx"],
    "compilerSupport": ["g++.exe","gcc.exe"], // Only windows, if you need to support linux, add g++, gcc.
    "runnerSupport": null, // No Runner
    "compiler": "compileFunc",
    "runner": "runFunc",
    "compilerDefaultArg": ["-G","-std=c++23"],
    "runnerDefaultArg": []
  }
}
```

**Definitions of coding:**

 - ```codeName```: str, name of programming language.
 - ```fileExtension```: list, appendix or extension of file.
 - ```compilerSupport```: list, supported compiler name. (e.g. ```javac.exe```, ```gcc.exe```, ```clang.exe```, ```gcc```, ```g++``` etc.)
 - ```runnerSupport```: list (```null``` for no settings in Sinote), supported runner name. (e.g. ```java.exe``` to run jar)
 - ```compiler```: funcName, define in ```functions``` tag.
 - ```runner```: funcName, define in ```functions``` tag yet.
 - ```compilerDefaultArg```: list, default arguments for compile. (e.g. ```["-G", "-std=c++23"]``` for C++)
 - ```runnerDefaultArg```: list, default arguments for run. (e.g. ```["-Xms512M","-Xmx2G","--server.port=8888"]```)
 - ```noCompiler```: boolean, for Python and more programming language that no compiler. (Always ```false```)

### 1.3.3 Automatic Set Some Setting (type equals 0)

> **&#x2139;&#xfe0f; NOTICE:**
> <br>In fact, you have to read ```function.md```. <br>Then you can continue read this page.

A Plugin might need to set something to run.<br>
This page will **teach** you how to **adjust** a setting automatically.

<br><br>e.g. Adjust font size to 11:
```json5
{
  "config": {
    // Configuration
  },
  "functions": {
    "set_sth": [
      ["set","sinote.editor.fontSize",11], // Adjust font size
      ["log",0,"Adjusted fontSize to eleven!"] // Log a message there
    ]
  },
  "runFunc": [
    "set_sth"
  ],
  "coding": {
    // additional in there
  }
}
```

If you imported this header. It will adjust font size of editor to 11 and log a message (Type: INFO) and leave.<br>
___
### 1.4 End of Basic

Now, you might already be learnt it, you can continue study Chapter 2, or you can finish own your tasks.
<br>Thank you for your patient!
___
## 2 Advanced Header

#### This will *release* when API Version upgrade to two.
#### Now API Version: 1.0.1 (INITIAL)
#### Next Version: 1.0.3