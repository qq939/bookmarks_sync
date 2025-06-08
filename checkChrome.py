import json

data = json.load(
    open(
        "/Users/jimjiang/Downloads/bookmarks_sync/step1chromebookmarks/chrome_bookmarks_20250608_141521.json"
    )
)
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
