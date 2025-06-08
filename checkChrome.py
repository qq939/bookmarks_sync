import json
import glob
import os

# 模糊搜索chrome书签文件
chrome_files = glob.glob("/Users/jimjiang/Downloads/bookmarks_sync/step1chromebookmarks/chrome_bookmarks_*.json")
if not chrome_files:
    print("未找到Chrome书签文件")
    exit(1)

# 使用最新的文件
chrome_file = max(chrome_files, key=os.path.getctime)
print(f"使用文件: {chrome_file}")

data = json.load(open(chrome_file))
folders = [item for item in data if item["type"] == "folder"]
print("Chrome书签分类统计:")
[
    print(
        f"{folder['name']}: {len([child for child in folder['children'] if child['type']=='url'])} 个书签"
    )
    for folder in folders
]
total_bookmarks = sum(
    len([child for child in folder["children"] if child["type"] == "url"])
    for folder in folders
)
print(f"Chrome总计: {total_bookmarks} 个书签")
