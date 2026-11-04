# 参与改进

提交问题时请注明 Windows 版本、CubeMX 版本、内置 Java 版本、发生问题的界面与复现步骤。分享截图和日志前，请去掉工程名称、完整路径、账号等私人信息。

## 补充翻译

编辑 `translations/zh_CN.tsv`：一行一个英文原文、Tab 和中文译文。使用 UTF-8，不改变引脚名、寄存器名、宏和代码标识符，不添加 HTML 标记。优先提供出现该文字的页面和版本，说明词条是完整文本还是 HTML 文本节点。

## 提交代码

使用 Windows、Python 3.11+ 和 JDK 21，按 README 构建，再运行：

```powershell
python tools/build.py
python tools/verify.py
```

测试无需安装 CubeMX：启动器测试使用独立临时样本，Java 测试直接验证 Swing 渲染。但若修改汉化路径，仍应在自己安装的 CubeMX 上验证对应页面，并说明未验证范围。

源码不应包含 ST 的程序包、数据库、JRE、用户工程、完整提取字符串清单或本地日志。`reports/`、`build/` 和 `dist/` 都是本地产物目录。
