#!/usr/bin/env python3

import os
import sys
import json
import shutil
import importlib.util
from datetime import datetime

# 导入Chrome和Safari书签脚本作为模块
def import_script(script_path):
    module_name = os.path.basename(script_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 获取最新的JSON文件
def get_latest_json_file(directory):
    if not os.path.exists(directory):
        return None
    
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not json_files:
        return None
    
    # 按文件修改时间排序，获取最新的
    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    return os.path.join(directory, latest_file)

# 合并书签
def merge_bookmarks(chrome_bookmarks, safari_bookmarks):
    # 为每个书签添加来源标记
    for bookmark in chrome_bookmarks:
        add_source_to_bookmarks(bookmark, 'Chrome')
    
    for bookmark in safari_bookmarks:
        add_source_to_bookmarks(bookmark, 'Safari')
    
    # 修改所有书签的path为"Bookmarks Bar"，depth设为0
    for bookmark in chrome_bookmarks:
        normalize_bookmark_path(bookmark)
    
    for bookmark in safari_bookmarks:
        normalize_bookmark_path(bookmark)
    
    # 合并两个列表
    merged_bookmarks = chrome_bookmarks + safari_bookmarks
    return merged_bookmarks

# 递归添加来源标记
def add_source_to_bookmarks(bookmark, source):
    bookmark['source'] = source
    
    # 如果是文件夹，递归处理子项
    if bookmark['type'] == 'folder' and 'children' in bookmark:
        for child in bookmark['children']:
            add_source_to_bookmarks(child, source)

# 标准化书签路径和深度
def normalize_bookmark_path(bookmark):
    # 保存原始path信息
    if 'path' in bookmark and 'original_path' not in bookmark:
        bookmark['original_path'] = bookmark['path']
    
    # 将path设为"Bookmarks Bar"
    bookmark['path'] = 'Bookmarks Bar'
    
    # 添加depth字段并设为0
    bookmark['depth'] = 0
    
    # 如果是文件夹，递归处理子项
    if bookmark['type'] == 'folder' and 'children' in bookmark:
        for child in bookmark['children']:
            normalize_bookmark_path(child)

# 保存合并后的书签
def save_merged_bookmarks(bookmarks):
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step3merged')
    
    # 如果目录存在，先清空目录
    if os.path.exists(output_dir):
        print(f"清空目录: {output_dir}")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        # 如果目录不存在，创建它
        os.makedirs(output_dir)
        print(f"创建目录: {output_dir}")
    
    # 创建时间戳文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(output_dir, f"merged_bookmarks_{timestamp}.json")
    
    # 保存为JSON格式
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)
    
    print(f"合并书签已保存到: {json_file}")
    return json_file

# 打印合并后的书签统计信息
def print_merged_stats(bookmarks):
    chrome_count = 0
    safari_count = 0
    chrome_folders = 0
    safari_folders = 0
    
    def count_bookmarks(items):
        nonlocal chrome_count, safari_count, chrome_folders, safari_folders
        
        for item in items:
            if item['type'] == 'folder':
                if item['source'] == 'Chrome':
                    chrome_folders += 1
                else:
                    safari_folders += 1
                    
                if 'children' in item:
                    count_bookmarks(item['children'])
            else:  # url
                if item['source'] == 'Chrome':
                    chrome_count += 1
                else:
                    safari_count += 1
    
    count_bookmarks(bookmarks)
    
    print("\n合并书签统计:")
    print("-" * 50)
    print(f"Chrome书签: {chrome_count} 个")
    print(f"Chrome文件夹: {chrome_folders} 个")
    print(f"Safari书签: {safari_count} 个")
    print(f"Safari文件夹: {safari_folders} 个")
    print(f"总计: {chrome_count + safari_count} 个书签, {chrome_folders + safari_folders} 个文件夹")
    print("-" * 50)

# 主函数
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 导入Chrome和Safari书签脚本
    chrome_script_path = os.path.join(script_dir, 'step1_chrome_bookmarks_viewer_fixed.py')
    safari_script_path = os.path.join(script_dir, 'step2_safari_bookmarks_viewer.py')
    
    # 检查脚本是否存在
    if not os.path.exists(chrome_script_path):
        print(f"错误: Chrome书签脚本不存在: {chrome_script_path}")
        return
    
    if not os.path.exists(safari_script_path):
        print(f"错误: Safari书签脚本不存在: {safari_script_path}")
        return
    
    # print("步骤1: 导入Chrome和Safari书签脚本...")
    # try:
    #     chrome_module = import_script(chrome_script_path)
    #     safari_module = import_script(safari_script_path)
    # except Exception as e:
    #     print(f"导入脚本时出错: {e}")
    #     return
    
    # print("步骤2: 运行Chrome书签脚本...")
    # try:
    #     # 运行Chrome书签脚本的main函数
    #     chrome_module.main()
    # except Exception as e:
    #     print(f"运行Chrome书签脚本时出错: {e}")
    #     return
    # 
    # print("\n步骤3: 运行Safari书签脚本...")
    # try:
    #     # 运行Safari书签脚本的main函数
    #     safari_module.main()
    # except Exception as e:
    #     print(f"运行Safari书签脚本时出错: {e}")
    #     return
    
    print("\n步骤4: 获取最新的书签JSON文件...")
    chrome_bookmarks_dir = os.path.join(script_dir, 'step1chromebookmarks')
    safari_bookmarks_dir = os.path.join(script_dir, 'step2safaribookmarks')
    
    chrome_json_file = get_latest_json_file(chrome_bookmarks_dir)
    safari_json_file = get_latest_json_file(safari_bookmarks_dir)
    
    if not chrome_json_file:
        print(f"错误: 未找到Chrome书签JSON文件")
        return
    
    if not safari_json_file:
        print(f"错误: 未找到Safari书签JSON文件")
        return
    
    print(f"找到Chrome书签文件: {chrome_json_file}")
    print(f"找到Safari书签文件: {safari_json_file}")
    
    print("\n步骤5: 读取并合并书签...")
    try:
        # 读取Chrome书签
        with open(chrome_json_file, 'r', encoding='utf-8') as f:
            chrome_bookmarks = json.load(f)
        
        # 读取Safari书签
        with open(safari_json_file, 'r', encoding='utf-8') as f:
            safari_bookmarks = json.load(f)
        
        # 合并书签
        merged_bookmarks = merge_bookmarks(chrome_bookmarks, safari_bookmarks)
        
        # 打印统计信息
        print_merged_stats(merged_bookmarks)
        
        # 保存合并后的书签
        save_merged_bookmarks(merged_bookmarks)
        
        print("\n书签合并完成!")
        
    except Exception as e:
        print(f"合并书签时出错: {e}")
        return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"执行过程中出错: {e}")