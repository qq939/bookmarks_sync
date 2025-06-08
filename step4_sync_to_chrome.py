#!/usr/bin/env python3

import os
import sys
import json
import shutil
import time
from datetime import datetime

# 导入merge_bookmarks.py和chrome_bookmarks_viewer_fixed.py中的函数
import step3_merge_bookmarks
from step1_chrome_bookmarks_viewer_fixed import get_bookmarks_path as get_chrome_bookmarks_path

# 获取最新的合并书签文件
def get_latest_merged_bookmarks_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    merged_dir = os.path.join(script_dir, 'step3merged')
    
    if not os.path.exists(merged_dir):
        print(f"错误: 合并书签目录不存在: {merged_dir}")
        return None
    
    json_files = [f for f in os.listdir(merged_dir) if f.endswith('.json')]
    if not json_files:
        print(f"错误: 未找到合并书签文件")
        return None
    
    # 按文件修改时间排序，获取最新的
    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(merged_dir, f)))
    return os.path.join(merged_dir, latest_file)

# 将合并后的书签转换为Chrome书签格式
def convert_to_chrome_format(merged_bookmarks):
    # Chrome书签的基本结构
    chrome_format = {
        "checksum": "",
        "version": 1,
        "roots": {
            "bookmark_bar": {
                "children": [],
                "date_added": str(int(time.time() * 1000000)),
                "date_modified": str(int(time.time() * 1000000)),
                "id": "1",
                "name": "书签栏",
                "type": "folder"
            },
            "other": {
                "children": [],
                "date_added": str(int(time.time() * 1000000)),
                "date_modified": str(int(time.time() * 1000000)),
                "id": "2",
                "name": "其他书签",
                "type": "folder"
            },
            "synced": {
                "children": [],
                "date_added": str(int(time.time() * 1000000)),
                "date_modified": str(int(time.time() * 1000000)),
                "id": "3",
                "name": "移动设备书签",
                "type": "folder"
            }
        }
    }
    
    # 递归处理书签和文件夹
    def process_bookmarks(bookmarks, parent_array):
        for bookmark in bookmarks:
            current_time = int(time.time() * 1000000)
            bookmark_id = str(current_time + len(parent_array))
            
            if bookmark['type'] == 'url':
                # 处理URL类型的书签
                chrome_bookmark = {
                    "date_added": str(current_time),
                    "id": bookmark_id,
                    "name": bookmark['name'],
                    "type": "url",
                    "url": bookmark['url']
                }
                parent_array.append(chrome_bookmark)
            elif bookmark['type'] == 'folder':
                # 处理文件夹类型的书签
                folder = {
                    "children": [],
                    "date_added": str(current_time),
                    "date_modified": str(current_time),
                    "id": bookmark_id,
                    "name": bookmark['name'],
                    "type": "folder"
                }
                parent_array.append(folder)
                
                # 递归处理子书签
                if 'children' in bookmark and bookmark['children']:
                    process_bookmarks(bookmark['children'], folder["children"])
    
    # 根据原始path来源正确归属书签到对应的Chrome文件夹
    def get_target_folder(bookmark):
        source = bookmark.get('source', '')
        original_path = bookmark.get('original_path', bookmark.get('path', ''))
        
        if source == 'Chrome':
            # Chrome书签根据原始路径归属
            if original_path == 'Bookmarks Bar':
                return chrome_format["roots"]["bookmark_bar"]["children"]
            elif original_path == 'Other Bookmarks':
                return chrome_format["roots"]["other"]["children"]
            elif original_path == 'Mobile Bookmarks':
                return chrome_format["roots"]["synced"]["children"]
            else:
                # 默认放入书签栏
                return chrome_format["roots"]["bookmark_bar"]["children"]
        elif source == 'Safari':
            # Safari书签根据原始路径归属
            if original_path == '根目录':
                # Safari的根目录书签放入其他书签
                return chrome_format["roots"]["other"]["children"]
            else:
                # 其他Safari书签也放入其他书签
                return chrome_format["roots"]["other"]["children"]
        else:
            # 未知来源，默认放入其他书签
            return chrome_format["roots"]["other"]["children"]
    
    # 递归处理书签，根据original_path分组到正确的Chrome文件夹
    def distribute_bookmarks(bookmarks, target_roots):
        for bookmark in bookmarks:
            source = bookmark.get('source', '')
            original_path = bookmark.get('original_path', bookmark.get('path', ''))
            
            # 跳过顶级文件夹名称与Chrome文件夹名称相同的情况，避免嵌套
            if bookmark['type'] == 'folder' and bookmark['name'] in ['Bookmarks Bar', 'Other Bookmarks', 'Mobile Bookmarks']:
                # 直接处理其子书签，不创建同名文件夹
                if 'children' in bookmark and bookmark['children']:
                    distribute_bookmarks(bookmark['children'], target_roots)
                continue
            
            # 确定目标文件夹
            if source == 'Chrome':
                if original_path == 'Bookmarks Bar':
                    target_folder = target_roots['bookmark_bar']['children']
                elif original_path == 'Other Bookmarks':
                    target_folder = target_roots['other']['children']
                elif original_path == 'Mobile Bookmarks':
                    target_folder = target_roots['synced']['children']
                else:
                    target_folder = target_roots['bookmark_bar']['children']
            elif source == 'Safari':
                # Safari书签放入其他书签
                target_folder = target_roots['other']['children']
            else:
                target_folder = target_roots['other']['children']
            
            # 处理当前书签
            current_time = int(time.time() * 1000000)
            bookmark_id = str(current_time + len(target_folder))
            
            if bookmark['type'] == 'url':
                chrome_bookmark = {
                    "date_added": str(current_time),
                    "id": bookmark_id,
                    "name": bookmark['name'],
                    "type": "url",
                    "url": bookmark['url']
                }
                target_folder.append(chrome_bookmark)
            elif bookmark['type'] == 'folder':
                folder = {
                    "children": [],
                    "date_added": str(current_time),
                    "date_modified": str(current_time),
                    "id": bookmark_id,
                    "name": bookmark['name'],
                    "type": "folder"
                }
                target_folder.append(folder)
                
                # 递归处理子书签，子书签放在当前文件夹内
                if 'children' in bookmark and bookmark['children']:
                    # 为子书签创建临时的target_roots，指向当前文件夹
                    child_target_roots = {
                        'bookmark_bar': {'children': folder['children']},
                        'other': {'children': folder['children']},
                        'synced': {'children': folder['children']}
                    }
                    distribute_bookmarks(bookmark['children'], child_target_roots)
    
    # 处理合并后的书签
    distribute_bookmarks(merged_bookmarks, chrome_format["roots"])
    
    return chrome_format

# 保存书签到step4sync目录
def save_to_step4sync(chrome_format):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step4sync_dir = os.path.join(script_dir, 'step4sync')
    
    # 如果目录不存在，创建它
    if not os.path.exists(step4sync_dir):
        os.makedirs(step4sync_dir)
        print(f"创建目录: {step4sync_dir}")
    else:
        # 如果目录存在，先清空目录
        print(f"清空目录: {step4sync_dir}")
        for file in os.listdir(step4sync_dir):
            file_path = os.path.join(step4sync_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # 创建时间戳文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(step4sync_dir, f"chrome_bookmarks_{timestamp}.json")
    
    # 保存为JSON格式
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(chrome_format, f, ensure_ascii=False, indent=2)
        print(f"已成功将Chrome格式书签保存到: {json_file}")
        return True
    except Exception as e:
        print(f"保存到step4sync目录时出错: {e}")
        return False

# 保存书签到Chrome书签文件
def save_to_chrome_bookmarks(chrome_format):
    chrome_bookmarks_path = get_chrome_bookmarks_path()
    
    if not chrome_bookmarks_path:
        print("错误: 无法获取Chrome书签文件路径")
        return False
    
    # 备份原始书签文件
    backup_path = chrome_bookmarks_path + ".backup." + datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        shutil.copy2(chrome_bookmarks_path, backup_path)
        print(f"已备份原始Chrome书签文件到: {backup_path}")
    except Exception as e:
        print(f"备份Chrome书签文件时出错: {e}")
        return False
    
    # 保存新的书签文件
    try:
        with open(chrome_bookmarks_path, 'w', encoding='utf-8') as f:
            json.dump(chrome_format, f, ensure_ascii=False, indent=2)
        print(f"已成功将合并书签保存到Chrome书签文件: {chrome_bookmarks_path}")
        
        # 同时保存到step4sync目录
        save_to_step4sync(chrome_format)
        
        return True
    except Exception as e:
        print(f"保存到Chrome书签文件时出错: {e}")
        # 如果保存失败，恢复备份
        try:
            shutil.copy2(backup_path, chrome_bookmarks_path)
            print("已恢复原始Chrome书签文件")
        except Exception as restore_error:
            print(f"恢复备份时出错: {restore_error}")
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
    merged_file = get_latest_merged_bookmarks_file()
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
    
    print("\n步骤4: 转换为Chrome书签格式...")
    chrome_format = convert_to_chrome_format(merged_bookmarks)
    
    print("\n步骤5: 保存到Chrome书签文件...")
    if save_to_chrome_bookmarks(chrome_format):
        print("\n同步完成! 请重启Chrome浏览器以加载更新后的书签。")
    else:
        print("\n同步失败，请检查错误信息。")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"执行过程中出错: {e}")