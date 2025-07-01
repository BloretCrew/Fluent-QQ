<p align="center">
  <img width="16%" align="center" src="bloret.ico" alt="logo">
</p>
  <h1 align="center">
  Fluent QQ
</h1>
<p align="center">
  Fluent 设计的 QQ 客户端，依赖于 NapCat QQ
</p>

<div align="center">

[![应用程序打包](https://github.com/BloretCrew/Fluent-QQ/actions/workflows/build.yml/badge.svg)](https://github.com/BloretCrew/Fluent-QQ/actions/workflows/build.yml)
[![提交 Winget 更新软件包](https://github.com/BloretCrew/Fluent-QQ/actions/workflows/wingetcreate.yml/badge.svg)](https://github.com/BloretCrew/Fluent-QQ/actions/workflows/wingetcreate.yml)
[![讨论数](https://img.shields.io/github/discussions/BloretCrew/Fluent-QQ?style=social&label=%E8%AE%A8%E8%AE%BA)](https://github.com/BloretCrew/Fluent-QQ/discussions)
![仓库大小](https://img.shields.io/github/repo-size/BloretCrew/Fluent-QQ?style=social&label=%E4%BB%93%E5%BA%93%E5%A4%A7%E5%B0%8F)
![星标数](https://img.shields.io/github/stars/BloretCrew/Fluent-QQ?style=social&label=%E6%98%9F%E6%A0%87)  

[![下载量](https://img.shields.io/github/downloads/BloretCrew/Fluent-QQ/total?style=social&label=%E4%B8%8B%E8%BD%BD%E9%87%8F)](https://github.com/BloretCrew/Fluent-QQ/releases)
![最新正式版](https://img.shields.io/github/v/release/BloretCrew/Fluent-QQ?label=%E6%9C%80%E6%96%B0%E6%AD%A3%E5%BC%8F%E7%89%88)
![最新版（包括测试版）](https://img.shields.io/github/v/release/BloretCrew/Fluent-QQ?include_prereleases&style=social&label=%E6%9C%80%E6%96%B0%E7%89%88)
![WinGet 包版本](https://img.shields.io/winget/v/Bloret.Launcher?label=WinGet%20%E5%8C%85%E7%89%88%E6%9C%AC)
![WinGet 包名](https://img.shields.io/badge/WinGet_%E5%8C%85%E5%90%8D-Bloret.Launcher-blue&style=social)

</div>

![Show](img/show.gif)

> [!NOTE]
> Fluent QQ 现已加入 [Windows 包管理器 ( Windows Package Manager )](https://github.com/microsoft/winget-cli)
> 因此，现在您可以在终端中输入以下命令快速安装 百络谷启动器
> ```
> winget install Bloret.Launcher
> ```

> [!NOTE]
> 您可以以三种方式打开百洛谷启动器
> 1. 下载 `Fluent-QQ-Setup.exe` ，运行安装。
> 2. 下载 `Fluent-QQ-Windows.zip` ，解压后打开其中的 `Fluent-QQ.exe`
> 3. 下载软件源代码压缩包 `Source code (zip)` ，解压后在所在目录下运行 `python main.py`
>    （使用步骤二前请先安装 Python ， 运行 `winget install python` 即可）

> [!WARNING]
> 百络谷启动器已证书签名，一般不会被拦截了
> Windows 安全中心可能会拦截此软件，本软件不是任何病毒  
> 百洛谷启动器是开源项目，您可以查阅源代码。  
> 请按照下方操作打开软件
> <details>
>
> **<summary>单击此处展开，查看操作方法 (2 张图片)</summary>**
>
> ![](img/Windows1.jpg)
> ![](img/Windows2.jpg)
>
> </details>

## 托开发组要求，特添加此图 👇
<details>
  
**<summary>单击此处展开，查看宣传图 (1 张图片)</summary>**
![](img/if-not-use-jiedi-will.jpg)

</details>

## 功能与计划

- [x] 托盘与托盘菜单
- [x] 自定义启动
- [x] 下载 Minecraft
- [x] 启动 Minecraft
- [x] Minecraft 数据查询
- [x] 日志
- [x] 支持深浅色
- [x] 微软账户登录
- [x] 离线登录
- [x] 百络谷通行证登录
- [x] ……

## 软件截图
<details>

**<summary>单击此处展开，查看软件截图 (7 张图片)</summary>**

#### 主界面
![Home](img/Home.png)
#### 下载
![Download](img/Download.png)
#### 小工具
![tools](img/tools.png)
#### 通行证
![passport](img/passport.png)
#### 设置
![settings](img/settings.png)
#### 关于
![info](img/info.png)
#### 侧边栏
![menu](img/menu.png)

</details>

## 致谢以下存储库或项目
- [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [PyQt Fluent Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- [SF Symbols](https://developer.apple.com/cn/sf-symbols/)
<details>

**<summary>[Console Minecraft Launcher](https://github.com/MrShieh-X/console-minecraft-launcher)</summary>**

本项目有一部分基于此项目构建
> 本软件已取得 CMCL 作者许可，请不要像 [不符合 Console Minecraft Launcher (CMCL) 的使用协议 #12](https://github.com/BloretCrew/Fluent-QQ/issues/12) 一样来问关于 CMCL 的版权问题
> ![CMCLLICENSE](img/CMCLLICENSE.png)

</details>

<details>

**<summary>[Class Widgets](https://github.com/Class-Widgets)</summary>**
关于为什么会致谢 [Class Widgets](https://github.com/Class-Widgets)：  
[Class Widgets](https://github.com/Class-Widgets) 为 Fluent QQ 有以下值得我们致谢的点：
 - 为 Fluent QQ 的 UI 提供了想法
 - Fluent QQ 已加入 Class Widgets 插件广场
 - [@RinLit](https://github.com/RinLit-233-shiroko) 为本作品有写法指导
 - [[not cw] 求助为什么崩溃 #392](https://github.com/orgs/Class-Widgets/discussions/392)
 - [求教如何往下拉选择框做东西进去 #338](https://github.com/orgs/Class-Widgets/discussions/338)
</details>

## 使用人数统计（实时）

 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="http://pcfs.top:2/api/BL/madeuserpic" />
   <source media="(prefers-color-scheme: light)" srcset="http://pcfs.top:2/api/BL/madeuserpic" />
   <img alt="Fluent QQ 实时新增使用人数" src="http://pcfs.top:2/api/BL/madeuserpic" />
 </picture>

## 星标历史

 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=BloretCrew/Fluent-QQ&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=BloretCrew/Fluent-QQ&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=BloretCrew/Fluent-QQ&type=Date" />
 </picture>

## 相关链接
[Bloret QQ 群](https://qm.qq.com/q/clE5KHaVDG)
