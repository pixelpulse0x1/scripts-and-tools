import os
import sys
import datetime
import re
import shutil
from enum import Enum, auto

# --- 状态定义 ---
class State(Enum):
    """定义程序的所有可能状态"""
    WAITING_FOR_BACKUP_CONFIRMATION = auto()
    GETTING_PATHS = auto()
    PROCESSING_RENAME = auto()
    PROCESSING_CONVERSION = auto()
    PROCESSING_ORGANIZATION = auto()
    FINALIZED = auto()
    ABORTED = auto()

class MigrationAssistant:
    """
    一个采用状态机模式的、交互式的 Typora 到 Obsidian 迁移工具。
    整合了文件名重命名、链接转换和附件整理三大功能。
    """
    def __init__(self):
        """初始化状态机"""
        self.state = State.WAITING_FOR_BACKUP_CONFIRMATION
        self.target_folder_path = None
        self.asset_source_folder_name = "Database" # 默认附件文件夹名
        # --- 新增: 用于最终统计 ---
        self.renamed_files_count = 0
        self.converted_links_count = 0
        self.moved_files_count = 0
        self.duplicate_files_count = 0

    def run(self):
        """启动并运行状态机"""
        while True:
            if self.state == State.WAITING_FOR_BACKUP_CONFIRMATION:
                self._handle_backup_confirmation()
            elif self.state == State.GETTING_PATHS:
                self._handle_getting_paths()
            elif self.state == State.PROCESSING_RENAME:
                self._handle_rename()
            elif self.state == State.PROCESSING_CONVERSION:
                self._handle_conversion()
            elif self.state == State.PROCESSING_ORGANIZATION:
                self._handle_organization()
            elif self.state == State.FINALIZED:
                self._display_final_summary()
                print("\n✅ 所有迁移任务已成功完成！程序退出。")
                break
            elif self.state == State.ABORTED:
                print("\n❌ 操作已由用户终止。程序退出。")
                break

    def _wait_for_user_confirmation(self, prompt):
        """
        暂停程序，打印提示信息，并等待用户确认。
        返回 True 表示继续，返回 False 表示中止。
        """
        response = input(f"\n{prompt} ")
        if response.lower() == 'n':
            return False
        return True

    def _display_final_summary(self):
        """在程序结束前打印最终的操作总览。"""
        print("\n" + "=" * 70)
        print("🎉 全部流程执行完毕 - 操作总览 🎉")
        print("=" * 70)
        print(f"📄 文件名重命名:   成功重命名 {self.renamed_files_count} 个 .md 文件。")
        print(f"🔗 图片链接转换:   成功转换 {self.converted_links_count} 个链接。")
        print(f"🗂️ 附件库整理:")
        print(f"  - 成功移动 {self.moved_files_count} 个附件到新的库中。")
        print(f"  - 发现 {self.duplicate_files_count} 个重复附件，已隔离处理。")
        print("=" * 70)

    # --- 状态处理逻辑 ---

    def _handle_backup_confirmation(self):
        """处理备份确认状态"""
        print("=" * 70)
        print("欢迎使用 Typora 到 Obsidian 迁移助手")
        print("警告: 此工具将直接修改您的文件，操作不可逆。")
        print("在开始前，请务必手动完整备份您的整个笔记库文件夹！")
        print("=" * 70)
        confirm = input("我确认已经手动备份了我的笔记库文件夹 (y/n): ")
        if confirm.lower() == 'y':
            self.state = State.GETTING_PATHS
        else:
            self.state = State.ABORTED

    def _handle_getting_paths(self):
        """处理路径获取状态"""
        while True:
            path = input("请输入您的笔记库文件夹的绝对路径并按 Enter: ")
            cleaned_path = path.strip().strip('"')
            if os.path.isdir(cleaned_path):
                self.target_folder_path = cleaned_path
                print(f"✔️ 目标文件夹已确认为: {self.target_folder_path}")
                self.state = State.PROCESSING_RENAME
                break
            else:
                print(f"错误: 您输入的路径 '{cleaned_path}' 不是一个有效的文件夹，请重新输入。")

    def _handle_rename(self):
        """处理文件名重命名状态"""
        print("\n" + "=" * 70)
        print("🚀 步骤 1/3: [文件名重命名]")
        print("将为所有 .md 文件名添加 '最后修改日期' 前缀 (格式: YYYYMMDD-文件名.md)")
        print("=" * 70)
        self.renamed_files_count = self._batch_rename_md_files(self.target_folder_path)
        
        print("\n" + "-" * 70)
        print("下一步将执行:")
        print("🚀 步骤 2/3: [图片链接转换]")
        print("将 Typora 格式的图片链接 (如 `![](folder/image.png)`) 转换为 Obsidian 格式 (`![[image.png]]`)")
        print("-" * 70)

        if self._wait_for_user_confirmation("检查以上日志，按 Enter 键继续，或输入 'n' 退出。"):
            self.state = State.PROCESSING_CONVERSION
        else:
            self.state = State.ABORTED

    def _handle_conversion(self):
        """处理链接转换状态"""
        print("\n" + "=" * 70)
        print("🚀 步骤 2/3: [图片链接转换]")
        print("将 Typora 格式的图片链接 (如 `![](folder/image.png)`) 转换为 Obsidian 格式 (`![[image.png]]`)")
        print("=" * 70)
        self.converted_links_count = self._convert_image_links(self.target_folder_path)
        
        print("\n" + "-" * 70)
        print("下一步将执行:")
        print("🚀 步骤 3/3: [附件库整理]")
        print("将散落在各处的附件文件夹内容统一整理到一个新的附件库中。")
        print("-" * 70)
        
        if self._wait_for_user_confirmation("检查以上日志，按 Enter 键继续，或输入 'n' 退出。"):
            self.state = State.PROCESSING_ORGANIZATION
        else:
            self.state = State.ABORTED
            
    def _handle_organization(self):
        """处理附件整理状态"""
        print("\n" + "=" * 70)
        print("🚀 步骤 3/3: [附件库整理]")
        print("将散落在各处的附件文件夹内容统一整理到一个新的附件库中。")
        print("=" * 70)

        prompt = f"默认的源附件文件夹名为 '{self.asset_source_folder_name}'，是否需要更改？(直接按 Enter 使用默认值，或输入新名称): "
        new_name = input(prompt)
        if new_name.strip():
            self.asset_source_folder_name = new_name.strip()
            print(f"✔️ 源附件文件夹名已更新为: '{self.asset_source_folder_name}'")

        moved, duplicates = self._organize_database_folders(self.target_folder_path, self.asset_source_folder_name)
        self.moved_files_count = moved
        self.duplicate_files_count = duplicates
        
        if self._wait_for_user_confirmation("检查以上日志，按 Enter 键完成全部流程。"):
            self.state = State.FINALIZED
        else:
            self.state = State.ABORTED

    # --- 核心功能逻辑 (从原脚本整合) ---

    def _batch_rename_md_files(self, root_folder):
        """(源自 rename_md.py)"""
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
                        modification_timestamp = os.path.getmtime(old_filepath)
                        modification_date = datetime.datetime.fromtimestamp(modification_timestamp)
                        date_prefix = modification_date.strftime('%Y%m%d')
                        new_filename = f"{date_prefix}-{filename}"
                        new_filepath = os.path.join(dirpath, new_filename)
                        os.rename(old_filepath, new_filepath)
                        print(f"✅ 重命名: '{filename}' -> '{new_filename}'")
                        renamed_count += 1
                    except Exception as e:
                        print(f"❌ 处理 '{filename}' 时发生错误: {e}")

        print("\n--- [文件名重命名] 操作摘要 ---")
        print(f"共扫描到 {scanned_count} 个 .md 文件。")
        print(f"成功重命名 {renamed_count} 个文件。")
        return renamed_count

    def _convert_image_links(self, directory):
        """(源自 typora_to_obsidian.py)"""
        image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp']
        pattern_str = r'!\[.*?\]\((?:.*/)?(.*?\.({}))\)'.format('|'.join(image_extensions))
        image_pattern = re.compile(pattern_str, re.IGNORECASE)
        total_replacements = 0
        print(f"\n开始扫描文件夹: '{directory}'")

        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.md'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        new_content, num_replacements = image_pattern.subn(r'![[\1]]', content)
                        if num_replacements > 0:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"处理文件: {file_path}")
                            print(f"  -> 成功转换 {num_replacements} 个链接。")
                            total_replacements += num_replacements
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错: {e}", file=sys.stderr)
        
        print("\n--- [图片链接转换] 操作摘要 ---")
        if total_replacements > 0:
            print(f"总共成功转换了 {total_replacements} 个链接。")
        else:
            print("未在任何文件中发现需要转换的 Typora 格式图片链接。")
        return total_replacements

    def _organize_database_folders(self, root_folder, source_folder_name):
        """(源自 organize_db.py)"""
        consolidate_dir = os.path.join(root_folder, f"{source_folder_name}迁移后文件夹")
        duplicate_dir = os.path.join(root_folder, f"{source_folder_name}有重复文件需要手动处理")

        try:
            os.makedirs(consolidate_dir, exist_ok=True)
            os.makedirs(duplicate_dir, exist_ok=True)
            print(f"✔️ 目标文件夹创建/确认成功:\n  - {consolidate_dir}\n  - {duplicate_dir}")
        except OSError as e:
            print(f"❌ 错误: 无法创建目标文件夹，请检查权限。 {e}", file=sys.stderr)
            return 0, 0

        moved_count = 0
        duplicate_count = 0
        
        print(f"\n--- 开始阶段 1: 移动文件 (源文件夹: '{source_folder_name}') ---")
        for dirpath, _, filenames in os.walk(root_folder):
            if os.path.basename(dirpath) == source_folder_name:
                print(f"\n正在处理文件夹: {dirpath}")
                for filename in filenames:
                    source_path = os.path.join(dirpath, filename)
                    dest_path_consolidate = os.path.join(consolidate_dir, filename)
                    if not os.path.exists(dest_path_consolidate):
                        try:
                            shutil.move(source_path, dest_path_consolidate)
                            print(f"  -> 移动到 '{os.path.basename(consolidate_dir)}': {filename}")
                            moved_count += 1
                        except Exception as e:
                            print(f"  ❌ 移动失败 (权限问题?): {filename} - {e}")
                    else:
                        dest_path_duplicate = os.path.join(duplicate_dir, filename)
                        try:
                            shutil.move(source_path, dest_path_duplicate)
                            print(f"  ⚠️ 发现重复, 移动到 '{os.path.basename(duplicate_dir)}' 文件夹: {filename}")
                            duplicate_count += 1
                        except Exception as e:
                            print(f"  ❌ 移动重复文件失败: {filename} - {e}")

        print(f"\n--- 开始阶段 2: 清理空的 '{source_folder_name}' 文件夹 ---")
        deleted_folders_count = 0
        non_empty_folders = []
        for dirpath, _, _ in os.walk(root_folder, topdown=False):
            if os.path.basename(dirpath) == source_folder_name:
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        print(f"  🗑️ 删除空文件夹: {dirpath}")
                        deleted_folders_count += 1
                    else:
                        non_empty_folders.append(dirpath)
                except OSError as e:
                    print(f"  ❌ 删除文件夹失败: {dirpath} - {e}")
                    non_empty_folders.append(dirpath)

        print("\n--- [附件库整理] 操作摘要 ---")
        print(f"移动到 '{os.path.basename(consolidate_dir)}' 的文件总数: {moved_count}")
        print(f"因重名而移动到 '{os.path.basename(duplicate_dir)}' 的文件总数: {duplicate_count}")
        print(f"成功删除的空 '{source_folder_name}' 文件夹数量: {deleted_folders_count}")

        if duplicate_count == 0:
            try:
                if not os.listdir(duplicate_dir):
                    os.rmdir(duplicate_dir)
                    print(f"\n✔️ 因没有重复文件，已自动删除空的 '{os.path.basename(duplicate_dir)}' 文件夹。")
            except OSError as e:
                print(f"  ❌ 尝试自动删除空的重复文件夹失败: {e}")

        if non_empty_folders:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"!!! 警告: 以下 '{source_folder_name}' 文件夹未能清空或删除，请手动检查。")
            for path in non_empty_folders:
                print(f"  - {path}")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            print(f"\n所有 '{source_folder_name}' 文件夹均已成功处理并清理。")
        
        return moved_count, duplicate_count


if __name__ == "__main__":
    app = MigrationAssistant()
    app.run()

