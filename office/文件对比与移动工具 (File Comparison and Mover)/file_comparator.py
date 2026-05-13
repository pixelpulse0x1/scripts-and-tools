# -*- coding: utf-8 -*-
"""
一个用于对比两个文件夹中文件并进行分类移动的 Python 脚本。

功能：
1. 遍历源文件夹（要处理的文件夹）中的所有文件。
2. 与目标文件夹（参考文件夹）中的文件进行对比。
3. 根据对比结果，将源文件移动到三个不同的输出文件夹中：
   - './疑似完全相同': 源文件与目标文件夹（参考文件夹）中某个文件同名且大小相同。
   - './名称相同大小不同': 源文件与目标文件夹（参考文件夹）中某个文件同名但大小不同。
   - './疑似完全不同': 在目标文件夹（参考文件夹）中找不到与源文件同名的文件。
4. 自动创建所需的输出文件夹。
5. 在移动文件时打印操作日志。
"""
import os
import shutil

# --- 用户配置区域 ---
# 脚本将以交互方式请求路径，此处不再需要硬编码
# --- 配置结束 ---

# 定义输出文件夹的名称
# 规则 A-1: 存在同名文件且大小相同
IDENTICAL_FOLDER = "./疑似完全相同"
# 规则 A-2: 存在同名文件但大小不同
DIFF_SIZE_FOLDER = "./名称相同大小不同"
# 规则 B: 不存在同名文件
UNIQUE_FOLDER = "./疑似完全不同"


def get_user_paths():
    """
    通过交互式提示获取并验证用户输入的源文件夹（要处理的文件夹）和目标文件夹（参考文件夹）路径。
    """
    while True:
        source_path = input("请输入源文件夹（要处理的文件夹）路径 (Source Folder): ").strip()
        # strip() 用于移除用户可能意外输入的前后空格
        if not os.path.isdir(source_path):
            print(f"错误：源文件夹（要处理的文件夹）路径 '{source_path}' 无效或不存在。请重新输入。")
            continue

        target_path = input("请输入目标文件夹（参考文件夹）路径 (Target Folder): ").strip()
        if not os.path.isdir(target_path):
            print(f"错误：目标文件夹（参考文件夹）路径 '{target_path}' 无效或不存在。请重新输入。")
            continue

        print("\n" + "="*40)
        print("请您二次核对路径：")
        print(f"  - 源文件夹（要处理的文件夹）: {source_path}")
        print(f"  - 目标文件夹（参考文件夹）: {target_path}")
        print("\n脚本将执行以下操作：")
        print(f"1. 对比 '{os.path.basename(source_path)}' 和 '{os.path.basename(target_path)}' 文件夹中的文件。")
        print(f"2. 将 '{os.path.basename(source_path)}' 中的文件移动到以下三个文件夹中：")
        print(f"   - '{IDENTICAL_FOLDER}'")
        print(f"   - '{DIFF_SIZE_FOLDER}'")
        print(f"   - '{UNIQUE_FOLDER}'")
        print("="*40 + "\n")

        confirm = input("确认无误并开始执行吗？(y/n): ").strip().lower()
        if confirm == 'y':
            return source_path, target_path
        elif confirm == 'n':
            print("操作已取消。")
            return None, None
        else:
            print("无效输入，请输入 'y' 或 'n' 后按回车键。")


def compare_and_move_files(source_folder_path, target_folder_path):
    """
    主函数，执行文件夹对比和文件移动操作。
    """
    # 1. 自动创建输出文件夹，如果它们不存在的话
    output_folders = [IDENTICAL_FOLDER, DIFF_SIZE_FOLDER, UNIQUE_FOLDER]
    for folder in output_folders:
        # exist_ok=True 表示如果文件夹已存在，则不会抛出错误
        os.makedirs(folder, exist_ok=True)
    print("输出文件夹检查/创建完毕。")
    print("-" * 30)

    # 2. 为了提高查找效率，先获取目标文件夹（参考文件夹）中所有文件的名称，并存入一个集合(set)
    try:
        target_filenames = {
            f for f in os.listdir(target_folder_path)
            if os.path.isfile(os.path.join(target_folder_path, f))
        }
    except OSError as e:
        print(f"错误：无法读取目标文件夹（参考文件夹） '{target_folder_path}' 的内容: {e}")
        return

    # 3. 遍历源文件夹（要处理的文件夹）中的所有项目
    try:
        source_items = os.listdir(source_folder_path)
    except OSError as e:
        print(f"错误：无法读取源文件夹（要处理的文件夹） '{source_folder_path}' 的内容: {e}")
        return

    print("开始处理文件...")
    moved_count = 0
    skipped_count = 0

    if not source_items:
        print("源文件夹（要处理的文件夹）为空，无需处理。")

    for filename in source_items:
        source_file_path = os.path.join(source_folder_path, filename)

        # 需求：仅处理文件，所以需要判断并跳过子文件夹
        if not os.path.isfile(source_file_path):
            print(f"[跳过] '{filename}' 是一个文件夹，不处理。")
            skipped_count += 1
            continue

        destination_folder = ""

        # 核心对比逻辑
        if filename in target_filenames:
            # 规则 A: 在目标文件夹（参考文件夹）中存在同名文件
            target_file_path = os.path.join(target_folder_path, filename)
            try:
                source_file_size = os.path.getsize(source_file_path)
                target_file_size = os.path.getsize(target_file_path)

                if source_file_size == target_file_size:
                    # 规则 A-1: 文件大小相同
                    destination_folder = IDENTICAL_FOLDER
                else:
                    # 规则 A-2: 文件大小不同
                    destination_folder = DIFF_SIZE_FOLDER
            except OSError as e:
                print(f"警告：无法获取文件 '{filename}' 的大小。将跳过此文件。错误: {e}")
                continue
        else:
            # 规则 B: 在目标文件夹（参考文件夹）中不存在同名文件
            destination_folder = UNIQUE_FOLDER

        # 执行移动操作并打印日志
        try:
            shutil.move(source_file_path, destination_folder)
            # 为了输出格式统一，使用 os.path.join 构建目标路径
            final_dest_path = os.path.join(destination_folder, '')
            print(f"[移动] {filename} -> {final_dest_path}")
            moved_count += 1
        except (shutil.Error, OSError) as e:
            print(f"错误：移动文件 '{filename}' 失败。错误: {e}")

    print("-" * 30)
    print("处理完成。")
    print(f"总计移动了 {moved_count} 个文件。")
    if skipped_count > 0:
        print(f"跳过了 {skipped_count} 个项目（因为它们是子文件夹）。")


if __name__ == "__main__":
    # 首先调用函数获取用户确认的路径
    source_path, target_path = get_user_paths()
    
    # 只有当用户确认后（返回了有效路径），才执行对比和移动操作
    if source_path and target_path:
        compare_and_move_files(source_path, target_path)

