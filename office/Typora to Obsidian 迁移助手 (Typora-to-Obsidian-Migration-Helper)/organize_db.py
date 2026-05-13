import os
import sys
import shutil

def organize_database_folders(root_folder):
    """
    1.  将所有 'Database' 子文件夹内的文件统一移动到 'DatabaseNew'。
    2.  重名文件则移动到 'Database重复文件手动处理'。
    3.  删除所有变为空的 'Database' 文件夹。
    4.  报告未能删除的非空 'Database' 文件夹。
    你可以进行替换Database为你要操作的文件夹!
    """
    # 3. 在目标文件夹下自动新建用于存放文件的文件夹
    consolidate_dir = os.path.join(root_folder, "DatabaseNew")
    duplicate_dir = os.path.join(root_folder, "Database重复文件手动处理")

    try:
        os.makedirs(consolidate_dir, exist_ok=True)
        os.makedirs(duplicate_dir, exist_ok=True)
        print(f"✔️ 目标文件夹创建/确认成功:\n  - {consolidate_dir}\n  - {duplicate_dir}")
    except OSError as e:
        print(f"❌ 错误: 无法创建目标文件夹，请检查权限。 {e}", file=sys.stderr)
        return

    moved_count = 0
    duplicate_count = 0
    
    # --- 阶段 1: 文件聚合 ---
    print("\n--- 开始阶段 1: 移动文件 ---")
    
    # 2. 扫描文件夹及文件
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # 我们只关心名为 'Database' 的文件夹
        if os.path.basename(dirpath) == "Database":
            print(f"\n正在处理文件夹: {dirpath}")
            for filename in filenames:
                source_path = os.path.join(dirpath, filename)
                dest_path_consolidate = os.path.join(consolidate_dir, filename)

                # 4. 检查 'DatabaseNew' 中是否已存在同名文件
                if not os.path.exists(dest_path_consolidate):
                    # 不存在重名，移动到 'DatabaseNew'
                    try:
                        shutil.move(source_path, dest_path_consolidate)
                        print(f"  -> 移动到 'DatabaseNew': {filename}")
                        moved_count += 1
                    except Exception as e:
                        print(f"  ❌ 移动失败 (权限问题?): {filename} - {e}")
                else:
                    # 存在重名，移动到 'Database重复文件手动处理'
                    dest_path_duplicate = os.path.join(duplicate_dir, filename)
                    try:
                        shutil.move(source_path, dest_path_duplicate)
                        print(f"  ⚠️ 发现重复, 移动到 '重复文件' 文件夹: {filename}")
                        duplicate_count += 1
                    except Exception as e:
                        print(f"  ❌ 移动重复文件失败: {filename} - {e}")

    # --- 阶段 2: 清理空文件夹 ---
    print("\n--- 开始阶段 2: 清理空的 'Database' 文件夹 ---")
    deleted_folders_count = 0
    non_empty_folders = []

    # 使用 topdown=False, 从子文件夹向上遍历，这样才能成功删除空目录
    for dirpath, _, _ in os.walk(root_folder, topdown=False):
        # 5. 检查目标文件夹(含子文件夹），删除所有空的“Database”文件夹
        if os.path.basename(dirpath) == "Database":
            try:
                # os.listdir() 会列出所有文件和子文件夹
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    print(f"  🗑️ 删除空文件夹: {dirpath}")
                    deleted_folders_count += 1
                else:
                    # 如果文件夹移动后仍不为空，记录下来
                    non_empty_folders.append(dirpath)
            except OSError as e:
                print(f"  ❌ 删除文件夹失败: {dirpath} - {e}")
                non_empty_folders.append(dirpath)

    # --- 最终报告 ---
    print("\n--- 操作摘要 ---")
    print(f"移动到 'DatabaseNew' 的文件总数: {moved_count}")
    print(f"因重名而移动到 'Database重复文件手动处理' 的文件总数: {duplicate_count}")
    print(f"成功删除的空 'Database' 文件夹数量: {deleted_folders_count}")

    if non_empty_folders:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! 警告: 以下 'Database' 文件夹未能清空或删除，请手动检查。")
        print("!!! 原因可能是权限不足，或文件夹内含有无法处理的隐藏文件/子文件夹。")
        for path in non_empty_folders:
            print(f"  - {path}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print("\n所有 'Database' 文件夹均已成功处理并清理。")


# --- 主程序入口 ---
if __name__ == "__main__":
    target_folder = input("请输入要整理的根文件夹绝对路径并按 Enter: ")
    target_folder = target_folder.strip().strip('"')

    if os.path.isdir(target_folder):
        print("-" * 60)
        print(f"目标文件夹: {target_folder}")
        print("此操作将执行以下任务:")
        print("  1. 聚合所有 'Database' 文件夹内的文件到 'DatabaseNew'。")
        print("  2. 隔离重名文件到 'Database重复文件手动处理'。")
        print("  3. 删除所有清理完毕的空 'Database' 文件夹。")
        print("\n警告: 文件移动是不可逆操作，建议在继续前备份您的文件夹。")
        print("-" * 60)
        
        confirm = input("确认要开始整理吗? (y/n): ")
        if confirm.lower() == 'y':
            organize_database_folders(target_folder)
            print("\n所有操作已执行完毕。")
        else:
            print("操作已由用户取消。")
    else:
        print(f"错误: 您输入的路径 '{target_folder}' 不是一个有效的文件夹。", file=sys.stderr)