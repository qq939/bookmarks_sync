#!/usr/bin/env python3

import os
import json
import sys
import fcntl
import atexit
import tempfile
from datetime import datetime

# 关闭chrome
def close_chrome():
    if sys.platform == 'darwin':
        os.system('osascript -e \'tell application "Google Chrome" to quit\'')
    elif sys.platform.startswith('win'):
        os.system('taskkill /f /im chrome.exe')
    elif sys.platform.startswith('linux'):
        os.system('pkill -f chrome')
    else:
        print(f"不支持的操作系统: {sys.platform}")
# 关闭safari
def close_safari():
    if sys.platform == 'darwin':
        os.system('osascript -e \'tell application "Safari" to quit\'')
    elif sys.platform.startswith('win'):
        os.system('taskkill /f /im safari.exe')
    elif sys.platform.startswith('linux'):
        os.system('pkill -f safari')
    else:
        print(f"不支持的操作系统: {sys.platform}")

# 锁文件路径
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'chrome_bookmarks_viewer.lock')

# 锁文件句柄
lock_handle = None

# 清理锁文件
def cleanup_lock():
    global lock_handle
    if lock_handle:
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_UN)
            lock_handle.close()
            os.unlink(LOCK_FILE)
        except:
            pass

# 获取锁
def acquire_lock():
    global lock_handle
    try:
        lock_handle = open(LOCK_FILE, 'w')
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 写入PID
        lock_handle.write(str(os.getpid()))
        lock_handle.flush()
        # 注册退出时清理
        atexit.register(cleanup_lock)
        return True
    except IOError:
        # 已被锁定
        if lock_handle:
            lock_handle.close()
            lock_handle = None
        return False

# 定义Chrome书签文件的路径（根据操作系统不同）
def get_bookmarks_path():
    # macOS路径
    if sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')
    # Windows路径
    elif sys.platform.startswith('win'):
        return os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data\Default\Bookmarks')
    # Linux路径
    elif sys.platform.startswith('linux'):
        return os.path.expanduser('~/.config/google-chrome/Default/Bookmarks')
    else:
        print(f"不支持的操作系统: {sys.platform}")
        return None

# 递归解析书签文件夹
def parse_bookmarks(node, depth=0, path=""):
    results = []
    
    # 如果是文件夹
    if node.get('type') == 'folder':
        name = node.get('name', 'Unnamed Folder')
        # 更新路径
        current_path = f"{path}/{name}" if path else name
        
        # 添加文件夹信息
        folder_info = {
            'type': 'folder',
            'name': name,
            'path': current_path,
            'depth': depth,
            'children': []
        }
        
        # 递归处理子项
        if 'children' in node:
            for child in node['children']:
                child_items = parse_bookmarks(child, depth + 1, current_path)
                folder_info['children'].extend(child_items)
        
        results.append(folder_info)
    
    # 如果是书签
    elif node.get('type') == 'url':
        bookmark_info = {
            'type': 'url',
            'name': node.get('name', 'Unnamed Bookmark'),
            'url': node.get('url', ''),
            'path': path,
            'depth': depth
        }
        results.append(bookmark_info)
    
    return results

# 打印书签树
def print_bookmarks_tree(bookmarks, indent=0):
    for item in bookmarks:
        # 缩进显示层级
        prefix = '  ' * indent
        
        if item['type'] == 'folder':
            # 文件夹用方括号标识
            print(f"{prefix}[{item['name']}]")
            # 递归打印子项
            print_bookmarks_tree(item['children'], indent + 1)
        else:
            # 书签显示名称和URL
            print(f"{prefix}- {item['name']}: {item['url']}")

# 打印书签列表（扁平化显示）
def print_bookmarks_list(bookmarks):
    flat_list = []
    
    # 递归展平书签树
    def flatten(items, current_path=""):
        for item in items:
            if item['type'] == 'folder':
                path = item['path']
                flatten(item['children'], path)
            else:
                flat_list.append({
                    'name': item['name'],
                    'url': item['url'],
                    'path': item['path']
                })
    
    flatten(bookmarks)
    
    # 打印表头
    print("\n书签列表:")
    print("-" * 100)
    print(f"{'标题':<40} {'路径':<30} {'URL':<40}")
    print("-" * 100)
    
    # 打印书签
    for bookmark in flat_list:
        title = bookmark['name']
        path = bookmark['path']
        url = bookmark['url']
        
        # 截断过长的字符串以便于显示
        if len(title) > 38:
            title = title[:35] + '...'
        if len(path) > 28:
            path = path[:25] + '...'
        if len(url) > 38:
            url = url[:35] + '...'
            
        print(f"{title:<40} {path:<30} {url:<40}")
    
    print("-" * 100)
    print(f"总计: {len(flat_list)} 个书签")

# 保存书签到JSON文件
def save_bookmarks(bookmarks):
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step1chromebookmarks')
    
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
    json_file = os.path.join(output_dir, f"chrome_bookmarks_{timestamp}.json")
    
    # 保存为JSON格式
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)
    
    print(f"书签已保存到: {json_file}")
    return json_file

# 主函数
def main():
    # 关闭Chrome浏览器以确保书签文件可以被读取
    print("正在关闭Chrome浏览器...")
    close_chrome()
    
    # 尝试获取锁
    if not acquire_lock():
        print("另一个实例正在运行，退出...")
        return

    print(f"脚本路径: {os.path.abspath(__file__)}")

    # 获取Chrome书签文件路径
    bookmarks_file = get_bookmarks_path()
    if not bookmarks_file or not os.path.exists(bookmarks_file):
        print(f"错误: Chrome书签文件不存在: {bookmarks_file}")
        return
    
    print(f"正在读取Chrome书签文件: {bookmarks_file}")
    
    try:
        # 读取并解析书签文件
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Chrome书签文件的根结构
        roots = data.get('roots', {})
        bookmarks = []
        
        # 处理主要的书签文件夹（书签栏、其他书签等）
        for root_name, root_data in roots.items():
            if root_name not in ['sync_transaction_version', 'version']:
                print(f"处理书签根目录: {root_name}")
                root_bookmarks = parse_bookmarks(root_data)
                bookmarks.extend(root_bookmarks)
        
        if not bookmarks:
            print("未找到书签")
            return
        
        # 打印书签树（层级结构）
        print("\n书签树结构:")
        print("-" * 50)
        print_bookmarks_tree(bookmarks)
        
        # 打印书签列表
        print_bookmarks_list(bookmarks)
        
        # 保存书签到JSON文件
        save_bookmarks(bookmarks)
        
    except Exception as e:
        print(f"读取或解析书签文件时出错: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"执行过程中出错: {e}")