#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def verify_chrome_bookmarks():
    # 获取最新的Chrome格式书签文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    step4sync_dir = os.path.join(script_dir, 'step4sync')
    
    if not os.path.exists(step4sync_dir):
        print(f"错误: step4sync目录不存在: {step4sync_dir}")
        return
    
    json_files = [f for f in os.listdir(step4sync_dir) if f.endswith('.json')]
    if not json_files:
        print(f"错误: 未找到Chrome书签文件")
        return
    
    # 获取最新的文件
    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(step4sync_dir, f)))
    chrome_file = os.path.join(step4sync_dir, latest_file)
    
    print(f"验证Chrome书签文件: {chrome_file}")
    
    # 读取Chrome书签文件
    try:
        with open(chrome_file, 'r', encoding='utf-8') as f:
            chrome_data = json.load(f)
    except Exception as e:
        print(f"读取Chrome书签文件时出错: {e}")
        return
    
    # 统计各个文件夹中的书签数量
    def count_bookmarks(bookmarks_array, folder_name):
        count = 0
        for item in bookmarks_array:
            if item['type'] == 'url':
                count += 1
            elif item['type'] == 'folder' and 'children' in item:
                count += count_bookmarks(item['children'], f"{folder_name}/{item['name']}")
        return count
    
    # 获取各个根文件夹的书签数量
    bookmark_bar_count = count_bookmarks(chrome_data['roots']['bookmark_bar']['children'], 'Bookmarks Bar')
    other_count = count_bookmarks(chrome_data['roots']['other']['children'], 'Other Bookmarks')
    synced_count = count_bookmarks(chrome_data['roots']['synced']['children'], 'Mobile Bookmarks')
    
    print(f"\n书签分布统计:")
    print(f"书签栏 (Bookmarks Bar): {bookmark_bar_count} 个书签")
    print(f"其他书签 (Other Bookmarks): {other_count} 个书签")
    print(f"移动设备书签 (Mobile Bookmarks): {synced_count} 个书签")
    print(f"总计: {bookmark_bar_count + other_count + synced_count} 个书签")
    
    # 显示前几个书签的详细信息
    print(f"\n书签栏前5个书签:")
    bookmark_bar_items = chrome_data['roots']['bookmark_bar']['children']
    for i, item in enumerate(bookmark_bar_items[:5]):
        if item['type'] == 'url':
            print(f"  {i+1}. {item['name']} - {item['url']}")
        elif item['type'] == 'folder':
            print(f"  {i+1}. [文件夹] {item['name']}")
    
    print(f"\n其他书签前5个书签:")
    other_items = chrome_data['roots']['other']['children']
    for i, item in enumerate(other_items[:5]):
        if item['type'] == 'url':
            print(f"  {i+1}. {item['name']} - {item['url']}")
        elif item['type'] == 'folder':
            print(f"  {i+1}. [文件夹] {item['name']}")
    
    print(f"\n验证完成!")

if __name__ == "__main__":
    verify_chrome_bookmarks()