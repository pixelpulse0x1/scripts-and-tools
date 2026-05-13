import os
import re
import sys

def convert_image_links(directory):
    """
    遍历指定目录下的所有 Markdown 文件，并将 Typora 格式的图片链接转换为 Obsidian 格式。

    Typora 格式 1: ![](./some_folder/image.png)
    Typora 格式 2: ![alt-text](./some_folder/image.png)
    Obsidian 格式: ![[image.png]]
    """
    # 支持常见的图片文件扩展名，已添加 webp
    image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp']
    # 构建正则表达式，用于匹配 Typora 的图片链接
    # 解释:
    # !\[.*?\]\(   : 匹配 "!["，然后是任意数量的字符 (alt text)，然后是 "]("
    # (?:.*/)?    : 匹配并忽略路径部分 (e.g., "./Database/")。
    #              (?:...) 是一个非捕获组。
    #              .* 表示任意字符，/ 是路径分隔符。? 表示路径是可选的。
    # (.*?)        : 捕获图片文件名 (非贪婪模式)。这是我们需要的核心内容。
    # \.           : 匹配文件名和扩展名之间的点。
    # ({})         : 将支持的图片扩展名插入正则表达式。
    # \)           : 匹配最后的 ")"
    pattern_str = r'!\[.*?\]\((?:.*/)?(.*?\.({}))\)'.format('|'.join(image_extensions))
    # 添加 re.IGNORECASE 标志以忽略扩展名的大小写
    image_pattern = re.compile(pattern_str, re.IGNORECASE)

    # 遍历指定目录
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 使用正则表达式查找并替换所有匹配的链接
                    # sub 函数的第二个参数 r'![[\1]]' 中的 \1 代表正则表达式中第一个捕获组的内容，
                    # 也就是我们需要的图片文件名 (e.g., "image-20250726104501340.png")
                    new_content, num_replacements = image_pattern.subn(r'![[\1]]', content)

                    if num_replacements > 0:
                        # 如果发生了替换，则将新内容写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"处理文件: {file_path}")
                        print(f"  -> 成功转换 {num_replacements} 个链接。")

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}", file=sys.stderr)

    print("\n所有文件处理完毕！")

if __name__ == '__main__':
    # 提示用户输入要处理的文件夹路径
    # 在 Windows 上，你可以直接复制文件夹路径，例如: C:\Users\YourName\Documents\MyNotes
    # 在 macOS 或 Linux 上，路径类似: /Users/YourName/Documents/MyNotes
    target_directory = input("请输入您的笔记库文件夹的绝对路径: ")

    if os.path.isdir(target_directory):
        convert_image_links(target_directory)
    else:
        print("错误: 您输入的不是一个有效的文件夹路径。", file=sys.stderr)

