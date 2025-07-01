from qfluentwidgets import InfoBar, InfoBarPosition
import os,subprocess,json
from modules.log import log, importlog

def CustomizeRun(self,version):
    ''' 
    # Fluent QQ 自定义启动
    启动版本 version  
    version 版本必须包含在 config 配置文件 中的 Customize 列表内。

    
    ***
    ###### Fluent QQ 所有 © 2025 Fluent QQ All rights reserved. © 2025 Bloret All rights reserved.
    '''
    # 查找 config.json 中 Customize 的 showname 是否匹配 version
    for item in self.config.get("Customize", []):
        if item.get("showname") == version:
            program_path = item.get("path")
            if program_path and os.path.exists(program_path):
                InfoBar.success(
                    title=f'🔄️ 正在启动 {version}',
                    content=f"...",
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                subprocess.Popen(program_path, shell=True)
                return
            else:
                InfoBar.error(
                    title='❌ 启动失败',
                    content=f"路径 {program_path} 不存在或无效",
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                return
    InfoBar.error(
        title='❌ 启动失败',
        content=f"未找到与 {version} 匹配的自定义程序",
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=5000,
        parent=self
    )
def find_Customize(self,version):
    '''
    ## 查找 config.json 中 Customize 的 showname 是否匹配 version

    ***
    ###### Fluent QQ 所有 © 2025 Fluent QQ All rights reserved. © 2025 Bloret All rights reserved.
    '''
    with open('config.json', 'r', encoding='utf-8') as file:
        config_data = json.load(file)
    if "Customize" not in config_data:
        config_data["Customize"] = []
    for item in self.config.get("Customize", []):
        if item.get("showname") == version:
            program_path = item.get("path")
            if program_path and os.path.exists(program_path):
                log(f"找到：{item}")
                return True,item
            else:
                log(f"找到：{item}，但路径 {program_path} 不存在或无效")
                return False,item
    log(f"无法找到：{version}")
    return False,version

importlog("CUSTOMIZE.PY")