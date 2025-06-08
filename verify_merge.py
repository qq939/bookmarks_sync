import json

# 读取合并后的书签文件
with open('/Users/jimjiang/Downloads/bookmarks_sync/step3merged/merged_bookmarks_20250607_181129.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def check_all_bookmarks(items):
    """递归检查所有书签的path和depth"""
    for item in items:
        if item.get('path') != 'Bookmarks Bar':
            return False, f"发现path不是'Bookmarks Bar'的书签: {item.get('name', 'Unknown')}, path: {item.get('path')}"
        if item.get('depth') != 0:
            return False, f"发现depth不是0的书签: {item.get('name', 'Unknown')}, depth: {item.get('depth')}"
        
        # 如果是文件夹，递归检查子项
        if item['type'] == 'folder' and 'children' in item:
            result, msg = check_all_bookmarks(item['children'])
            if not result:
                return False, msg
    
    return True, "所有书签都符合要求"

# 检查结果
result, message = check_all_bookmarks(data)

print(f"验证结果: {message}")
print(f"总书签数: {len(data)}")
print(f"\n前5个书签的信息:")
for i, item in enumerate(data[:5]):
    print(f"  {i+1}. 名称: {item.get('name', 'Unknown')}")
    print(f"     类型: {item.get('type')}")
    print(f"     路径: {item.get('path')}")
    print(f"     深度: {item.get('depth')}")
    print(f"     来源: {item.get('source')}")
    print()