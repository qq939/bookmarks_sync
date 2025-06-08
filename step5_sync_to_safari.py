#!/usr/bin/env python3

import os
import sys
import json
import shutil
import time
from datetime import datetime

# 导入merge_bookmarks.py中的函数
import step3_merge_bookmarks

# 获取最新的合并书签文件
def get_latest_merged_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step3merged_dir = os.path.join(script_dir, 'step3merged')
    
    if not os.path.exists(step3merged_dir):
        print(f"错误: 目录不存在: {step3merged_dir}")
        return None
    
    # 获取目录中的所有JSON文件
    json_files = [f for f in os.listdir(step3merged_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"错误: 在 {step3merged_dir} 中没有找到JSON文件")
        return None
    
    # 按文件名排序（假设文件名包含日期时间信息）
    json_files.sort(reverse=True)
    latest_file = os.path.join(step3merged_dir, json_files[0])
    
    print(f"找到最新的合并书签文件: {latest_file}")
    return latest_file

# 将合并后的书签转换为Safari书签格式
def convert_to_safari_format(merged_bookmarks):
    # 创建一个简化的Safari格式书签结构
    safari_format = []
    
    # 递归处理书签
    def process_bookmarks(items, parent):
        for item in items:
            if item.get("type") == "folder":
                # 创建新文件夹
                new_folder = {
                    "type": "folder",
                    "name": item.get("name", ""),
                    "children": []
                }
                parent.append(new_folder)
                
                # 递归处理子项
                if "children" in item and isinstance(item["children"], list):
                    process_bookmarks(item["children"], new_folder["children"])
            elif item.get("type") == "url":
                # 添加URL
                parent.append({
                    "type": "url",
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", "")
                })
    
    # 处理根书签
    process_bookmarks(merged_bookmarks, safari_format)
    
    return safari_format



# 将书签转换为HTML格式
def convert_to_html_format(bookmarks):
    # HTML头部
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
"""
    
    # 递归处理书签
    def process_bookmarks(items, indent="    "):
        result = ""
        for item in items:
            if item.get("type") == "folder":
                # 处理文件夹
                folder_name = item.get("name", "")
                result += f"{indent}<DT><H3>{folder_name}</H3>\n{indent}<DL><p>\n"
                if "children" in item and isinstance(item["children"], list):
                    result += process_bookmarks(item["children"], indent + "    ")
                result += f"{indent}</DL><p>\n"
            elif item.get("type") == "url":
                # 处理URL
                url_name = item.get("name", "")
                url = item.get("url", "")
                source = item.get("source", "")
                add_date = int(datetime.now().timestamp())
                result += f"{indent}<DT><A HREF=\"{url}\" ADD_DATE=\"{add_date}\" SOURCE=\"{source}\">{url_name}</A>\n"
        return result
    
    # 处理根书签
    html += process_bookmarks(bookmarks)
    
    # HTML尾部
    html += "</DL><p>"
    
    return html

# 保存书签到step5sync2safari目录
def save_to_step5sync2safari(safari_format):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step5sync2safari_dir = os.path.join(script_dir, 'step5sync2safari')
    
    # 如果目录不存在，创建它
    if not os.path.exists(step5sync2safari_dir):
        os.makedirs(step5sync2safari_dir)
        print(f"创建目录: {step5sync2safari_dir}")
    else:
        # 如果目录存在，先清空目录
        print(f"清空目录: {step5sync2safari_dir}")
        for file in os.listdir(step5sync2safari_dir):
            file_path = os.path.join(step5sync2safari_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # 创建时间戳文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(step5sync2safari_dir, f"safari_bookmarks_{timestamp}.json")
    html_file = os.path.join(step5sync2safari_dir, f"safari_bookmarks_{timestamp}.html")
    
    success = True
    
    # 保存为JSON格式
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(safari_format, f, ensure_ascii=False, indent=2)
        print(f"已成功将Safari格式书签保存到: {json_file}")
    except Exception as e:
        print(f"保存JSON格式书签时出错: {e}")
        success = False
    
    # 转换为HTML格式并保存
    try:
        html_content = convert_to_html_format(safari_format)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已成功将HTML格式书签保存到: {html_file}")
    except Exception as e:
        print(f"保存HTML格式书签时出错: {e}")
        success = False
    
    return success

# 生成Safari导入说明文件
def create_import_instructions():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step5sync2safari_dir = os.path.join(script_dir, 'step5sync2safari')
    instructions_file = os.path.join(step5sync2safari_dir, "导入说明.txt")
    
    instructions = """
如何将书签导入到Safari浏览器：

方法1 - 使用HTML文件（推荐）：
1. 打开Safari浏览器
2. 点击菜单栏中的"文件" > "导入自" > "书签HTML文件..."
3. 在弹出的文件选择器中，选择本目录中的HTML文件（文件名类似于 safari_bookmarks_YYYYMMDD_HHMMSS.html）
4. 点击"导入"按钮完成导入

方法2 - 手动导入：
1. 在Safari中，点击菜单栏中的"书签" > "编辑书签"
2. 手动创建与JSON文件中相同的书签结构

注意：
- 由于Safari的安全限制，无法通过脚本直接修改Safari的书签文件
- 本目录中的HTML文件是专门为Safari导入而创建的，可以直接导入
- JSON文件仅用于备份和参考
"""
    
    try:
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        print(f"已创建导入说明文件: {instructions_file}")
        return True
    except Exception as e:
        print(f"创建导入说明文件时出错: {e}")
        return False

# 主函数
def main():
    print("步骤1: 调用merge_bookmarks.py处理和合并书签...")
    try:
        # 调用merge_bookmarks.py的main函数
        step3_merge_bookmarks.main()
    except Exception as e:
        print(f"调用merge_bookmarks.py时出错: {e}")
        return
    
    print("\n步骤2: 获取最新的合并书签文件...")
    merged_file = get_latest_merged_file()
    if not merged_file:
        return
    
    print(f"找到合并书签文件: {merged_file}")
    
    print("\n步骤3: 读取合并书签文件...")
    try:
        with open(merged_file, 'r', encoding='utf-8') as f:
            merged_bookmarks = json.load(f)
    except Exception as e:
        print(f"读取合并书签文件时出错: {e}")
        return
    
    print("\n步骤4: 转换为Safari书签格式...")
    safari_format = convert_to_safari_format(merged_bookmarks)
    
    print("\n步骤5: 保存到step5sync2safari目录...")
    if save_to_step5sync2safari(safari_format):
        # 创建导入说明文件
        create_import_instructions()
        print("\n同步完成! 书签已保存到step5sync2safari目录。")
        print("由于Safari的安全限制，无法通过脚本直接修改Safari的书签文件。")
        print("请参考step5sync2safari目录中的导入说明.txt文件，手动将书签导入到Safari。")
    else:
        print("\n同步失败，请检查错误信息。")

if __name__ == "__main__":
    # 调用step3_merge_bookmarks.py来确保合并书签是最新的
    try:
        step3_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step3_merge_bookmarks.py')
        print(f"运行脚本: {step3_script_path}")
        exec(open(step3_script_path).read())
    except Exception as e:
        print(f"运行step3_merge_bookmarks.py时出错: {e}")
    
    # 获取最新的合并书签文件
    latest_file = get_latest_merged_file()
    if not latest_file:
        print("无法获取最新的合并书签文件，退出程序")
        sys.exit(1)
    
    # 读取合并书签
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            merged_bookmarks = json.load(f)
        print(f"已读取合并书签文件: {latest_file}")
    except Exception as e:
        print(f"读取合并书签文件时出错: {e}")
        sys.exit(1)
    
    # 转换为Safari格式
    safari_format = convert_to_safari_format(merged_bookmarks)
    
    # 保存到step5sync2safari目录
    if save_to_step5sync2safari(safari_format):
        # 创建导入说明文件
        create_import_instructions()
        print("完成！由于Safari的安全限制，无法直接通过脚本导入书签。请按照导入说明手动导入。")
    else:
        print("保存Safari格式书签失败，请检查错误信息。")
        sys.exit(1)