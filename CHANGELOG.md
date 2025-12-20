# Change log of Sinote Editor

## Recently Build
***Now no any build because only Pre-release out!***
## Recently Pre-release
### 0.06.26001
1. **Add feature**: Add Loading Screen when Sinote is loading plugins or fonts.
2. **Fix issue**: Fix issue ``When trigger Save As, it will pop out an Exception Window``
3. **Add feature in CLI**: Realized ``check`` command to check plugins
4. **Add feature**: Add many shortcuts to Sinote.
5. **Add feature**: Add Pop-up Dialog to confirm exit Sinote.
6. **Fix issue**: Replace Python normal `dict` to `SafetyDict` for safety.
7. **Add feature**: Session restore now includes cursor position and text selection state. Your cursor will be exactly where you left it!
8. **Add feature**: *(Now planned)* Add **project** feature
9. **Fix issue**: Fix issue that it will make a crash if you make a type=0 plugin and put it to `./resources/plugins/`
10. **Documentation Edit**: Edit `function.md`, add Q&A chapter.
### 0.06.25542
1. **Add feature**: Add **+** button to create new Tab. (I forgot add it in 0.06.25530)
2. **Add feature**: It automatically restores last session every start. (It won't be restored your cursor position.)
3. **Re-write**: Object *SpacingSupportEdit* **re-write** and discard before version. **(Before was written by AI)**
4. **Add feature**: Support **Fallback Font**. (Normal will be ***MiSans VF***)
5. **Add feature**: Support **Theme change**. (It's different from FluentCpp, it can change, but it need not to re-start application.)
6. **Add feature**: Support **open file with argument**. Like ``Sinote.exe MyFile.txt``, Sinote will open MyFile.txt!
7. **Optimize**: Optimized start time. (My old PC, CPU: ``Intel i3-2120 @ 3.3GHz``) Before: ``8s+`` Now: ``1.98s-3.68s``
8. **Add feature**: Sinote is wrong, its truly name is ```Arguments++```. (JOKE) Exactly, add ``--only-create-cache``, ``--no-color/-nc``, ``--no-theme/-nt``, ``--record-log/-rl``. Look Help for learn more.
9. **Something not important**: Add software icon.
10. **Add feature**: Add **Plugin Setting** for config your plugin!
11. **Add software**: Add **Sinote CLI** (SinoteCLI.py) for create plugin quickly.
### 0.06.25530
1. First version, no **any** update.