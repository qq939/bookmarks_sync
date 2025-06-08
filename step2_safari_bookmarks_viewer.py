#!/usr/bin/env python3

import os
import json
import sys
import fcntl
import atexit
import tempfile
import subprocess
import plistlib
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
LOCK_FILE = os.path.join(tempfile.gettempdir(), 'safari_bookmarks_viewer.lock')

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

# 定义Safari书签文件的路径
def get_bookmarks_path():
    # macOS路径
    if sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Safari/Bookmarks.plist')
    else:
        print(f"Safari书签仅支持macOS系统")
        return None

# 显示授权指导
def show_authorization_guide():
    print("\n" + "="*60)
    print("Safari书签访问授权指导")
    print("="*60)
    print("\n为了让此脚本能够访问Safari书签，您需要在系统偏好设置中进行授权：")
    print("\n步骤1: 打开系统偏好设置")
    print("  - 点击苹果菜单 → 系统偏好设置")
    print("  - 或者按 Command + 空格键，搜索'系统偏好设置'")
    
    print("\n步骤2: 进入安全性与隐私设置")
    print("  - 点击'安全性与隐私'图标")
    print("  - 选择'隐私'标签页")
    
    print("\n步骤3: 授权自动化权限")
    print("  - 在左侧列表中找到并点击'自动化'")
    print("  - 找到'Terminal'或'Python'条目")
    print("  - 勾选'Safari'复选框")
    print("  - 如果需要，点击左下角的锁图标并输入密码")
    
    print("\n步骤4: 授权完整磁盘访问权限（可选但推荐）")
    print("  - 在左侧列表中找到并点击'完整磁盘访问权限'")
    print("  - 点击'+'按钮添加Terminal或Python")
    print("  - 如果需要，点击左下角的锁图标并输入密码")
    
    print("\n步骤5: 重启Terminal并重新运行脚本")
    print("  - 关闭当前Terminal窗口")
    print("  - 重新打开Terminal并运行脚本")
    
    print("\n" + "="*60)
    print("注意事项：")
    print("- 如果您使用的是macOS Catalina (10.15)或更新版本，这些权限是必需的")
    print("- 授权后可能需要重启Terminal才能生效")
    print("- 如果仍然遇到问题，请尝试重启Safari")
    print("="*60 + "\n")
    
    # 询问用户是否已完成授权
    while True:
        response = input("请问您是否已完成上述授权步骤？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是', 'Y']:
            return True
        elif response in ['n', 'no', '否', 'N']:
            print("\n请先完成授权步骤，然后重新运行脚本。")
            return False
        else:
            print("请输入 y 或 n")

# 获取实际的Safari书签数据
def get_actual_safari_bookmarks():
    try:
        print("正在获取Safari书签...")
        
        # 更简单的AppleScript来获取书签
        script = '''
        tell application "Safari"
            try
                -- 尝试获取书签信息
                set bookmarkInfo to "Safari书签获取功能正在开发中"
                return bookmarkInfo
            on error errMsg
                return "获取书签时出错: " & errMsg
            end try
        end tell
        '''
        
        # 执行AppleScript
        process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"AppleScript执行错误: {stderr.decode('utf-8')}")
            return []
        
        # 解析输出
        output = stdout.decode('utf-8').strip()
        print(f"AppleScript输出: {output}")
        
        if not output or output == "":
            print("Safari中没有找到书签")
            return []
        
        if "获取书签时出错" in output:
            print(f"获取书签失败: {output}")
            return []
        
        # 检查是否是开发中的消息
        if "Safari书签获取功能正在开发中" in output:
            print("\n📝 说明: Safari书签获取功能正在开发中")
            print("\n由于Safari的安全限制，直接通过AppleScript获取书签比较复杂。")
            print("目前可以使用以下替代方案：")
            print("\n方案1: 手动导出Safari书签")
            print("  1. 打开Safari浏览器")
            print("  2. 菜单栏选择 '文件' → '导出书签...'")
            print("  3. 将导出的HTML文件保存到项目目录")
            print("  4. 脚本可以解析HTML格式的书签文件")
            print("\n方案2: 直接读取Safari书签文件")
            print("  - 脚本会尝试直接读取 ~/Library/Safari/Bookmarks.plist 文件")
            print("  - 这需要完整磁盘访问权限")
            
            # 尝试直接读取plist文件
            print("\n正在尝试直接读取Safari书签文件...")
            return read_safari_plist_directly()
        
        # 如果有其他格式的输出，尝试解析
        print(f"收到未知格式的输出，返回空列表: {output}")
        return []
        
    except Exception as e:
        print(f"获取Safari书签时发生错误: {e}")
        return []

# 直接读取Safari的plist文件
def read_safari_plist_directly():
    try:
        bookmarks_path = get_bookmarks_path()
        if not bookmarks_path or not os.path.exists(bookmarks_path):
            print(f"❌ 无法找到Safari书签文件: {bookmarks_path}")
            return []
        
        print(f"📁 正在读取Safari书签文件: {bookmarks_path}")
        
        # 读取plist文件
        with open(bookmarks_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        # 解析书签数据
        bookmarks = []
        
        def extract_bookmarks(item, path="根目录"):
            if isinstance(item, dict):
                if item.get('WebBookmarkType') == 'WebBookmarkTypeLeaf':
                    # 这是一个书签
                    url = item.get('URLString', '')
                    
                    # 尝试多种方式获取标题
                    title = ''
                    if 'URIDictionary' in item and item['URIDictionary'] and 'title' in item['URIDictionary']:
                        title = item['URIDictionary']['title']
                    elif 'Title' in item:
                        title = item['Title']
                    
                    # 调试信息：打印前几个书签的详细信息
                    if len(bookmarks) < 3:
                        print(f"调试 - 书签 {len(bookmarks)+1}:")
                        print(f"  URL: {url}")
                        print(f"  URIDictionary: {item.get('URIDictionary', {})}")
                        print(f"  Title字段: {item.get('Title', 'None')}")
                        print(f"  最终标题: {title}")
                        print()
                    
                    if url:
                        # 如果没有标题，使用URL作为名称或默认名称
                        if not title:
                            title = url if len(url) < 50 else 'Unnamed Bookmark'
                        bookmarks.append({
                            'name': title,
                            'url': url,
                            'path': path
                        })
                elif item.get('WebBookmarkType') == 'WebBookmarkTypeList':
                    # 这是一个文件夹
                    folder_title = item.get('Title', '未命名文件夹')
                    children = item.get('Children', [])
                    new_path = f"{path}/{folder_title}" if path != "根目录" else folder_title
                    for child in children:
                        extract_bookmarks(child, new_path)
            elif isinstance(item, list):
                for child in item:
                    extract_bookmarks(child, path)
        
        # 从根开始提取
        if 'Children' in plist_data:
            extract_bookmarks(plist_data['Children'])
        
        print(f"✅ 成功从plist文件中获取到 {len(bookmarks)} 个书签")
        return bookmarks
        
    except PermissionError:
        print("❌ 权限不足，无法读取Safari书签文件")
        print("请在'系统偏好设置 → 安全性与隐私 → 隐私 → 完整磁盘访问权限'中添加Terminal")
        return []
    except Exception as e:
        print(f"❌ 读取Safari书签文件时发生错误: {e}")
        return []

# 使用AppleScript导出Safari书签
def export_safari_bookmarks():
    try:
        # 首先显示授权指导
        if not show_authorization_guide():
            return None
            
        print("\n正在尝试访问Safari书签...")
        
        # AppleScript命令 - 简化版本，仅测试访问权限
        script = '''
        tell application "Safari"
            activate
            delay 1
            
            try
                -- 尝试访问Safari来测试权限
                set windowCount to count of windows
                return "成功访问Safari，当前有 " & windowCount & " 个窗口"
            on error errMsg
                return "权限错误: " & errMsg
            end try
        end tell
        '''
        
        # 执行AppleScript
        process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"AppleScript执行错误: {stderr.decode('utf-8')}")
            return None
        
        # 解析输出
        output = stdout.decode('utf-8').strip()
        if not output:
            print("AppleScript未返回任何信息")
            return None
        
        print(f"AppleScript输出: {output}")
        
        # 检查权限测试结果
        if "成功访问Safari" in output:
            print("✅ Safari访问权限验证成功！")
            print("现在开始获取完整的书签数据...")
            
            # 获取实际的书签数据
            return get_actual_safari_bookmarks()
        elif "权限错误" in output:
            print("❌ Safari访问权限验证失败！")
            print("请按照上述指导完成系统偏好设置中的授权，然后重新运行脚本。")
            print("\n常见解决方案：")
            print("1. 确保在'系统偏好设置 → 安全性与隐私 → 隐私 → 自动化'中授权了Terminal访问Safari")
            print("2. 尝试重启Terminal")
            print("3. 尝试重启Safari")
            print("4. 如果问题持续，请尝试添加'完整磁盘访问权限'")
            return None
        else:
            print(f"未知的AppleScript输出: {output}")
            return None
            
    except Exception as e:
        print(f"执行AppleScript时发生错误: {e}")
        return None

    
    except Exception as e:
        print(f"导出Safari书签时出错: {e}")
        return None

# 递归解析Safari书签
def parse_safari_bookmarks(node, path=""):
    results = []
    
    # 跳过特定的系统文件夹
    skip_folders = ['com.apple.ReadingList', 'BookmarksMenu', 'BookmarksBar', 'Menu']
    
    # 处理文件夹
    if 'Children' in node and isinstance(node['Children'], list):
        folder_name = node.get('Title', 'Unnamed Folder')
        
        # 跳过系统文件夹
        if folder_name in skip_folders or node.get('WebBookmarkType') == 'WebBookmarkTypeList':
            current_path = path
        else:
            # 更新路径
            current_path = f"{path}/{folder_name}" if path else folder_name
            
            # 添加文件夹信息
            folder_info = {
                'type': 'folder',
                'name': folder_name,
                'path': current_path,
                'children': []
            }
            
            results.append(folder_info)
        
        # 递归处理子项
        for child in node['Children']:
            child_items = parse_safari_bookmarks(child, current_path)
            
            # 如果当前是文件夹，将子项添加到children中
            if folder_name not in skip_folders and node.get('WebBookmarkType') != 'WebBookmarkTypeList' and child_items:
                for item in results:
                    if item['type'] == 'folder' and item['name'] == folder_name:
                        item['children'].extend(child_items)
                        break
            else:
                results.extend(child_items)
    
    # 处理书签
    elif node.get('WebBookmarkType') == 'WebBookmarkTypeLeaf' and 'URLString' in node:
        # 尝试多种方式获取标题
        title = ''
        if 'URIDictionary' in node and node['URIDictionary'] and 'title' in node['URIDictionary']:
            title = node['URIDictionary']['title']
        elif 'Title' in node:
            title = node['Title']
        
        # 如果没有标题，使用默认名称
        if not title:
            title = 'Unnamed Bookmark'
        
        bookmark_info = {
            'type': 'url',
            'name': title,
            'url': node.get('URLString', ''),
            'path': path if path else "根目录"
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
            print(f"{prefix}- {item['name']}: {item.get('url', '')}")

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
                    'url': item.get('url', ''),
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
        url = bookmark.get('url', '')
        
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
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'step2safaribookmarks')
    
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
    json_file = os.path.join(output_dir, f"safari_bookmarks_{timestamp}.json")
    
    # 保存为JSON格式
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)
    
    print(f"书签已保存到: {json_file}")
    return json_file

# 生成示例书签数据
def generate_sample_bookmarks():
    return [
        {
            'type': 'folder',
            'name': '收藏夹',
            'path': '收藏夹',
            'children': [
                {
                    'type': 'url',
                    'name': '百度',
                    'url': 'https://www.baidu.com',
                    'path': '收藏夹'
                },
                {
                    'type': 'url',
                    'name': '谷歌',
                    'url': 'https://www.google.com',
                    'path': '收藏夹'
                },
                {
                    'type': 'url',
                    'name': '必应',
                    'url': 'https://www.bing.com',
                    'path': '收藏夹'
                },
                {
                    'type': 'url',
                    'name': '搜狗',
                    'url': 'https://www.sogou.com',
                    'path': '收藏夹'
                },
                {
                    'type': 'url',
                    'name': '360搜索',
                    'url': 'https://www.so.com',
                    'path': '收藏夹'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '工作',
            'path': '工作',
            'children': [
                {
                    'type': 'url',
                    'name': 'GitHub',
                    'url': 'https://github.com',
                    'path': '工作'
                },
                {
                    'type': 'url',
                    'name': 'GitLab',
                    'url': 'https://gitlab.com',
                    'path': '工作'
                },
                {
                    'type': 'url',
                    'name': 'Stack Overflow',
                    'url': 'https://stackoverflow.com',
                    'path': '工作'
                },
                {
                    'type': 'url',
                    'name': 'Jira',
                    'url': 'https://www.atlassian.com/software/jira',
                    'path': '工作'
                },
                {
                    'type': 'url',
                    'name': 'Confluence',
                    'url': 'https://www.atlassian.com/software/confluence',
                    'path': '工作'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '学习',
            'path': '学习',
            'children': [
                {
                    'type': 'url',
                    'name': 'Coursera',
                    'url': 'https://www.coursera.org',
                    'path': '学习'
                },
                {
                    'type': 'url',
                    'name': 'edX',
                    'url': 'https://www.edx.org',
                    'path': '学习'
                },
                {
                    'type': 'url',
                    'name': 'Udemy',
                    'url': 'https://www.udemy.com',
                    'path': '学习'
                },
                {
                    'type': 'url',
                    'name': 'Khan Academy',
                    'url': 'https://www.khanacademy.org',
                    'path': '学习'
                },
                {
                    'type': 'url',
                    'name': 'MIT OpenCourseWare',
                    'url': 'https://ocw.mit.edu',
                    'path': '学习'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '娱乐',
            'path': '娱乐',
            'children': [
                {
                    'type': 'url',
                    'name': 'YouTube',
                    'url': 'https://www.youtube.com',
                    'path': '娱乐'
                },
                {
                    'type': 'url',
                    'name': 'Netflix',
                    'url': 'https://www.netflix.com',
                    'path': '娱乐'
                },
                {
                    'type': 'url',
                    'name': 'Spotify',
                    'url': 'https://www.spotify.com',
                    'path': '娱乐'
                },
                {
                    'type': 'url',
                    'name': 'Bilibili',
                    'url': 'https://www.bilibili.com',
                    'path': '娱乐'
                },
                {
                    'type': 'url',
                    'name': '爱奇艺',
                    'url': 'https://www.iqiyi.com',
                    'path': '娱乐'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '新闻',
            'path': '新闻',
            'children': [
                {
                    'type': 'url',
                    'name': 'BBC',
                    'url': 'https://www.bbc.com',
                    'path': '新闻'
                },
                {
                    'type': 'url',
                    'name': 'CNN',
                    'url': 'https://www.cnn.com',
                    'path': '新闻'
                },
                {
                    'type': 'url',
                    'name': '人民网',
                    'url': 'http://www.people.com.cn',
                    'path': '新闻'
                },
                {
                    'type': 'url',
                    'name': '新华网',
                    'url': 'http://www.xinhuanet.com',
                    'path': '新闻'
                },
                {
                    'type': 'url',
                    'name': '环球网',
                    'url': 'https://www.huanqiu.com',
                    'path': '新闻'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '购物',
            'path': '购物',
            'children': [
                {
                    'type': 'url',
                    'name': '淘宝',
                    'url': 'https://www.taobao.com',
                    'path': '购物'
                },
                {
                    'type': 'url',
                    'name': '京东',
                    'url': 'https://www.jd.com',
                    'path': '购物'
                },
                {
                    'type': 'url',
                    'name': '亚马逊',
                    'url': 'https://www.amazon.com',
                    'path': '购物'
                },
                {
                    'type': 'url',
                    'name': '天猫',
                    'url': 'https://www.tmall.com',
                    'path': '购物'
                },
                {
                    'type': 'url',
                    'name': '拼多多',
                    'url': 'https://www.pinduoduo.com',
                    'path': '购物'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '社交',
            'path': '社交',
            'children': [
                {
                    'type': 'url',
                    'name': '微博',
                    'url': 'https://weibo.com',
                    'path': '社交'
                },
                {
                    'type': 'url',
                    'name': 'Twitter',
                    'url': 'https://twitter.com',
                    'path': '社交'
                },
                {
                    'type': 'url',
                    'name': 'Facebook',
                    'url': 'https://www.facebook.com',
                    'path': '社交'
                },
                {
                    'type': 'url',
                    'name': 'LinkedIn',
                    'url': 'https://www.linkedin.com',
                    'path': '社交'
                },
                {
                    'type': 'url',
                    'name': 'Instagram',
                    'url': 'https://www.instagram.com',
                    'path': '社交'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '工具',
            'path': '工具',
            'children': [
                {
                    'type': 'url',
                    'name': 'Google翻译',
                    'url': 'https://translate.google.com',
                    'path': '工具'
                },
                {
                    'type': 'url',
                    'name': '百度翻译',
                    'url': 'https://fanyi.baidu.com',
                    'path': '工具'
                },
                {
                    'type': 'url',
                    'name': 'DeepL翻译',
                    'url': 'https://www.deepl.com/translator',
                    'path': '工具'
                },
                {
                    'type': 'url',
                    'name': '有道翻译',
                    'url': 'https://fanyi.youdao.com',
                    'path': '工具'
                },
                {
                    'type': 'url',
                    'name': 'Google地图',
                    'url': 'https://maps.google.com',
                    'path': '工具'
                }
            ]
        },
        {
            'type': 'folder',
            'name': '旅游',
            'path': '旅游',
            'children': [
                {
                    'type': 'url',
                    'name': '携程',
                    'url': 'https://www.ctrip.com',
                    'path': '旅游'
                },
                {
                    'type': 'url',
                    'name': '去哪儿',
                    'url': 'https://www.qunar.com',
                    'path': '旅游'
                },
                {
                    'type': 'url',
                    'name': '飞猪',
                    'url': 'https://www.fliggy.com',
                    'path': '旅游'
                },
                {
                    'type': 'url',
                    'name': 'Booking.com',
                    'url': 'https://www.booking.com',
                    'path': '旅游'
                },
                {
                    'type': 'url',
                    'name': 'Airbnb',
                    'url': 'https://www.airbnb.com',
                    'path': '旅游'
                }
            ]
        }
    ]

# 主函数
def main():
    # 关闭Safari浏览器以确保书签文件可以被读取
    print("正在关闭Safari浏览器...")
    close_safari()
    
    # 尝试获取锁
    if not acquire_lock():
        print("另一个实例正在运行，退出...")
        return

    print(f"脚本路径: {os.path.abspath(__file__)}")

    bookmarks = None
    
    # 方法1: 尝试直接读取Safari的plist文件
    bookmarks_file = get_bookmarks_path()
    if bookmarks_file and os.path.exists(bookmarks_file):
        print(f"正在读取Safari书签文件: {bookmarks_file}")
        
        try:
            # 读取并解析plist文件
            with open(bookmarks_file, 'rb') as f:
                data = plistlib.load(f)
            
            # Safari书签文件的根结构
            if 'Children' in data:
                print("解析Safari书签文件...")
                bookmarks = parse_safari_bookmarks(data)
        except Exception as e:
            print(f"读取或解析Safari书签文件时出错: {e}")
    else:
        print(f"Safari书签文件不存在或无法访问")
    
    # 方法2: 如果直接读取失败，尝试使用AppleScript导出
    if not bookmarks:
        print("尝试使用AppleScript导出Safari书签...")
        applescript_bookmarks = export_safari_bookmarks()
        
        if applescript_bookmarks:
            # 转换为标准格式
            bookmarks = []
            for bookmark in applescript_bookmarks:
                bookmarks.append({
                    'type': 'url',
                    'name': bookmark['name'],
                    'url': '',  # AppleScript无法获取URL
                    'path': bookmark['path']
                })
    
    # 如果无法获取真实书签，则打印错误信息并退出
    if not bookmarks:
        print("\n无法获取Safari书签，脚本将退出。")
        sys.exit(1) # 退出脚本
    
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

# 全局变量，用于标记脚本是否已经执行过
_SCRIPT_EXECUTED = False

if __name__ == "__main__":
    try:
        # 确保脚本只执行一次
        if not _SCRIPT_EXECUTED:
            _SCRIPT_EXECUTED = True
            main()
    except Exception as e:
        print(f"执行过程中出错: {e}")