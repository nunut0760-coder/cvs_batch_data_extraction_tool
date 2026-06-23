hello all！

welcome to using this

cvs_batch_data_extraction_tool

==============================

一、软件功能

本工具用于批量提取多个CSV文件中的指定字段（列），并自动汇总生成Excel或CSV结果文件。

适用于：

* 测试数据整理
* 设备数据统计
* 批量CSV数据分析
* 多文件数据汇总

支持：

√ 自动扫描文件夹中的CSV文件

√ 文件型号筛选（包含/排除）

√ 字段（列）筛选（包含/排除）

√ 批量提取指定字段

√ Excel输出

√ CSV输出

√ 汇总输出

√ 分文件夹输出

√ 自动生成处理进度

√ 自动跳过历史Result结果文件夹

==============================

二、结果文件说明

处理完成后，程序会自动生成结果目录。

例如：
Result1
Result2
Result3

每次运行都会自动创建新的结果目录，不会覆盖历史结果。

目录示例：

Result3

├─ Merged_Result.xlsx

├─ FolderA_Result.xlsx

├─ FolderB_Result.xlsx

└─ failed_files.txt

==============================

三、注意事项

1. 建议处理前关闭正在打开的CSV文件。

2. CSV文件列名尽量保持一致。

3. 程序会自动跳过：
   Result
   Result1
   Result2
   Result3
   等历史结果目录。

4. 输出文件默认保存到当前选择文件夹下的Result目录中。

5. 首次启动速度较慢属于正常现象。

==============================

Version Information

cvs_batch_data_extraction_tool_v1.6.0

Author：lyshao

Last Updated：2026.06.22
