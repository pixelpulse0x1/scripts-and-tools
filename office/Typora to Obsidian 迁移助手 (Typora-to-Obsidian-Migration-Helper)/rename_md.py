import os
import sys
import datetime
import re

def batch_rename_md_files(root_folder):
    """
    递归地为指定文件夹及其子文件夹下的所有 .md 文件名添加其“最后修改日期”前缀。
    格式: '笔记.md' -> '20251001-笔记.md'
    """
    print(f"\n开始扫描文件夹: '{root_folder}'")
    renamed_count = 0
    scanned_count = 0

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.md'):
                scanned_count += 1
                
                if re.match(r'^\d{8}-', filename):
                    print(f"-> 跳过 (已是目标格式): {filename}")
                    continue

                old_filepath = os.path.join(dirpath, filename)

                try:
                    # --- 主要修改点 ---
                    # 4. 读取文件的“最后修改日期” (mtime) 而不是“创建日期” (ctime)
                    modification_timestamp = os.path.getmtime(old_filepath)
                    modification_date = datetime.datetime.fromtimestamp(modification_timestamp)
                    # --- 修改结束 ---

                    # 5. 生成 'YYYYMMDD-' 格式的日期前缀
                    date_prefix = modification_date.strftime('%Y%m%d')

                    # 6. 构建新文件名并执行重命名
                    new_filename = f"{date_prefix}-{filename}"
                    new_filepath = os.path.join(dirpath, new_filename)

                    os.rename(old_filepath, new_filepath)
                    print(f"✅ 重命名: '{filename}' -> '{new_filename}'")
                    renamed_count += 1

                except Exception as e:
                    print(f"❌ 处理 '{filename}' 时发生错误: {e}")

    print("\n--- 操作摘要 ---")
    print(f"共扫描到 {scanned_count} 个 .md 文件。")
    print(f"成功重命名 {renamed_count} 个文件。")

# --- 主程序入口 (与上一版相同) ---
if __name__ == "__main__":
    target_folder = input("请输入目标文件夹的绝对路径并按 Enter: ")
    target_folder = target_folder.strip().strip('"')

    if os.path.isdir(target_folder):
        print("-" * 60)
        print(f"目标文件夹: {target_folder}")
        print("将使用文件的【修改日期】进行重命名。")
        print("警告: 文件重命名是不可逆操作，建议在继续前备份您的文件夹。")
        print("-" * 60)
        
        confirm = input("确认要开始处理吗? (y/n): ")
        if confirm.lower() == 'y':
            batch_rename_md_files(target_folder)
            print("\n所有操作已执行完毕。")
        else:
            print("操作已由用户取消。")
    else:
        print(f"错误: 您输入的路径 '{target_folder}' 不是一个有效的文件夹。", file=sys.stderr)