#!/bin/bash

# 书签同步汇总脚本
# 此脚本自动执行step1到step6的所有步骤，实现完整的书签同步流程

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}===== 书签同步工具 =====${NC}"
echo -e "${YELLOW}开始执行完整的书签同步流程...${NC}"

# 步骤1：从Chrome导出书签
echo -e "\n${BLUE}[步骤1] 从Chrome导出书签${NC}"
python3 step1_chrome_bookmarks_viewer_fixed.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}步骤1失败，请检查Chrome书签文件路径是否正确${NC}"
    exit 1
fi
echo -e "${GREEN}步骤1完成：Chrome书签已导出到step1chromebookmarks目录${NC}"

# 步骤2：从Safari导出书签
echo -e "\n${BLUE}[步骤2] 从Safari导出书签${NC}"
python3 step2_safari_bookmarks_viewer.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}步骤2失败，请检查Safari书签文件路径是否正确${NC}"
    exit 1
fi
echo -e "${GREEN}步骤2完成：Safari书签已导出到step2safaribookmarks目录${NC}"

# 步骤3：合并Chrome和Safari的书签
echo -e "\n${BLUE}[步骤3] 合并Chrome和Safari的书签${NC}"
python3 step3_merge_bookmarks.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}步骤3失败，请检查合并脚本是否正确${NC}"
    exit 1
fi
echo -e "${GREEN}步骤3完成：合并后的书签已保存到step3merged目录${NC}"

# 步骤4：将合并后的书签同步回Chrome
echo -e "\n${BLUE}[步骤4] 将合并后的书签同步回Chrome${NC}"
python3 step4_sync_to_chrome.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}步骤4失败，请检查同步脚本是否正确${NC}"
    exit 1
fi
echo -e "${GREEN}步骤4完成：合并后的书签已同步到Chrome（文件保存在step4sync2chrome目录）${NC}"

# 步骤5：将合并后的书签同步到Safari
echo -e "\n${BLUE}[步骤5] 将合并后的书签同步到Safari${NC}"
python3 step5_sync_to_safari.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}步骤5失败，请检查同步脚本是否正确${NC}"
    exit 1
fi
echo -e "${GREEN}步骤5完成：合并后的书签已转换为Safari格式（文件保存在step5sync2safari目录）${NC}"

# 步骤6：自动将HTML书签文件导入到Safari
echo -e "\n${BLUE}[步骤6] 自动将HTML书签文件导入到Safari${NC}"
echo -e "${YELLOW}注意：此步骤需要用户确认，将弹出确认对话框${NC}"
osascript "$SCRIPT_DIR/step6_automator.applescript"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}步骤6完成：书签已成功导入到Safari${NC}"
else
    echo -e "${YELLOW}步骤6可能未完成，请手动检查Safari书签是否已更新${NC}"
fi

echo -e "\n${GREEN}===== 书签同步完成 =====${NC}"
echo -e "${BLUE}Chrome书签文件：${NC}step4sync2chrome目录"
echo -e "${BLUE}Safari书签文件：${NC}step5sync2safari目录"
echo -e "${YELLOW}如需手动导入书签，请参考step5sync2safari目录中的导入说明文件${NC}"