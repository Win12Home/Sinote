# Function in Plugin

**Sinote Documentation,** by <span style="color:blue;">**Win12Home**</span> 2025, written in Markdown. 

---

## 1 Introduction

> Notice: This is an experimental feature.

Welcome to use Sinote Documentation!<br>
This Documentation supports Sinote API Version 1.<br>
<br>**Function Object** can be used in ***Plugin Header***.<br>
You need to enable ***enableCustomizeCommandRun*** option to open this feature.<br>
This is the normal function call struct: ```["\<funcname\>","\<required args\>",{"\<not required args\>","\<content\>"}]```<br>
There is a sample:
```json5
{
  "config": {
    // look at header.md
  },
  "function": {
    "func": [  // Name of Function
      ["log",0,"Hello! My Plugin World!"],
      ["print","Hello! My Plugin World!\n"]
    ]
  },
  "runFunc": [
    "func" // Automatic Trigger Function, can be used for Debug, settings.
  ],
  "coding": {
    // additional in there
  }
}
```

This code created a function named "func".<br>
When you run this function, it will log a message (Type: INFO) and word is "Hello! My Plugin World!", and it will out the same word in Python Terminal.<br>

## 2 The Built-in Function

For you create a function, you need to know the built-in functions in Sinote.
### ***Basic*** **Function** of **Sinote**:
**Since API 1.0.1**
 - ```print```: Print the string to the terminal. Struct: ```["print","\<string\>"]```
 - ```msgbox```: Out a Messagebox to the Main Application. Struct: ```["msgbox","\<title\>","\<content\>"]```
 - ```log```: Out customize content for log. Struct: ```["log", "\<type, 0: INFO, 1: WARN\>", "\<content\>"]```
 - ```var```: Set a temporary variable, use %var:\<varname\>% to use. Struct: ```["var","\<name\>","\<content\>"]``` (Content was not required.) 
 - ```vpr```: Only print content of variable. Struct: ```["vpr","\<variable name\>"]```
 - ```msgin```: Set a temporary variable with Message Box. Struct: ```["msgin","\<title\>","\<content\>","\<variable name\>]```
 - ```system```: Run a command in terminal. Struct: ```["system","\<command\>",{"out2term": false}]``` &#x26a0;&#xfe0f; A dangerous function
 - ```usefunc```: Use a Function. Struct: ```["usefunc","\<funcname\>"]```

### ***Advanced*** **Function** of **Sinote**:
**Since API 1.0.1**
 - ```set```: Set a **Sinote Setting** to customize content. Struct: ```["set","\<setting object\>","\<content\>"]```
 - ```mkdir```: Make a Directory (No error when file exists). Struct: ```["mkdir","\<directory\>"]```
 - ```cfile```: Create a file (No error when file exists). Struct: ```["cfile","\<file path\>"]```
 - ```efile```: Erase/Clear a file content (No error when file not exists, if not exists, create file yet). Struct: ```["efile","\<file path\>]``` &#x26a0;&#xfe0f; A dangerous function 
 - ```pfile```: Copy a file to another file (Also no error). Struct: ```["pfile","\<original file path\>","\<new file path\>",<always allow new file exists (true/false), default's false>]```
 - ```dfile```: Delete a file (No error when file not exists). Struct: ```["dfile","\<file path\>"]``` &#x26a0;&#xfe0f; A dangerous function
 - ```afile```: Append customize content (String) to a file (No error when file not exists). Struct: ```["afile","\<file path\>","\<content\>]```
 - ```wfile```: Write customize content (String) to a file (Automatic create file). Struct: ```["wfile","\<file path\>","\<content\>"]```
 - ```rfile```: Read a file and write the content to variable (Automatic create variable). Struct: ```["rfile","\<file path\>","\<variable name\>"]```
 - ```errbox```: Output an Error Messagebox. Struct: ```["errbox","\<error code like 0xffffffff\>"]```

## 3 Q&A of Function
**Q:** Why my plugin didn't work every start time?
<br>**A:** Did you forget put your function to `runFunc` or enable `enableCustomizeCommandRun`? If you've been did it, please open `Debug Mode` and send log to me!
<br>*Small tips about first one*: Use `-rl -db` arguments to enable `Debug Mode` and `Record Log Mode`, the log will be saved in `location/of/sinote/log`.
<br>**Q:** Why `system` and `usefunc` didn't work?
<br>**A:** I'm lazy. This is a plan!

## 4 End

> Note: This is a short Documentation, so it only has got 3 chapters.

Now, you might already be learnt it, you can continue study Sinote Header, or you can finish own your tasks.
<br>Thank you for your patient!