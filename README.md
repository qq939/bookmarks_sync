# 书签同步工具

## 简介

这是一个用于在Chrome和Safari之间同步书签的工具。它可以导出两个浏览器的书签，合并它们，然后将合并后的书签同步回两个浏览器。

## 使用方法

只需运行以下命令即可执行完整的书签同步流程：

```bash
./run_all_steps.sh
```

这个脚本将自动执行以下六个步骤：

1. 从Chrome导出书签并保存到step1chromebookmarks目录
2. 从Safari导出书签并保存到step2safaribookmarks目录
3. 合并Chrome和Safari的书签并保存到step3merged目录
4. 将合并后的书签同步回Chrome并保存到step4sync2chrome目录
5. 将合并后的书签同步到Safari并保存到step5sync2safari目录
6. 自动将HTML书签文件导入到Safari（需要用户确认）

## 注意事项

1. 如果脚本没有执行权限，请先运行以下命令：

```bash
chmod +x run_all_steps.sh
```

2. 在步骤6中，脚本会弹出确认对话框，请点击"继续"以完成自动导入。如果自动导入失败，脚本会提供手动导入指南并将文件路径复制到剪贴板。

3. 所有步骤的输出文件都保存在相应的目录中，您可以随时查看和使用这些文件。