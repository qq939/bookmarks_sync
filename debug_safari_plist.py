import plistlib
import os

path = os.path.expanduser('~/Library/Safari/Bookmarks.plist')
data = plistlib.load(open(path, 'rb'))

print('Plist结构:')
print(f'根键: {list(data.keys())}')

children = data.get('Children', [])
print(f'Children数量: {len(children)}')

if children:
    print('\n所有顶级项目:')
    for i, item in enumerate(children):
        print(f'  项目{i}: {item.get("WebBookmarkType")}, 标题: {item.get("Title")}')
    
    # 查找书签栏
    bookmarks_bar = None
    for item in children:
        if item.get('Title') == 'BookmarksBar' or item.get('WebBookmarkType') == 'WebBookmarkTypeList':
            bookmarks_bar = item
            break
    
    if bookmarks_bar:
        print(f'\n找到书签栏: {bookmarks_bar.get("Title")}')
        if bookmarks_bar.get('Children'):
            print(f'书签栏子项数量: {len(bookmarks_bar["Children"])}')
            
            # 查找第一个书签
            first_bookmark = None
            for child in bookmarks_bar['Children']:
                if child.get('WebBookmarkType') == 'WebBookmarkTypeLeaf':
                    first_bookmark = child
                    break
            
            if first_bookmark:
                print('\n第一个书签结构:')
                for key, value in first_bookmark.items():
                    print(f'  {key}: {value}')
            else:
                print('\n书签栏中未找到书签类型的项目')
                # 显示前几个子项的类型
                for i, child in enumerate(bookmarks_bar['Children'][:3]):
                    print(f'  子项{i}: {child.get("WebBookmarkType")}, 标题: {child.get("Title")}')
    else:
        print('\n未找到书签栏')