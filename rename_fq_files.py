import os
import argparse

def rename_files(meta_file, input_dir):
    """
    根据 meta 文件中的第三列重命名输入目录下的 .html 和 .zip 文件
    """
    # 打开 meta 文件
    with open(meta_file, "r") as f:
        for line in f:
            columns = line.strip().split("\t")  # 分割每行的内容
            
            # 提取 barcode 和新文件名（第三列）
            barcode = columns[0]
            new_name = columns[2]  # 获取第三列的名称
            
            # 构造原文件名和新文件名的路径
            original_html = os.path.join(input_dir, f"{barcode}_fastqc.html")
            new_html = os.path.join(input_dir, f"{new_name}_fastqc.html")
            original_zip = os.path.join(input_dir, f"{barcode}_fastqc.zip")
            new_zip = os.path.join(input_dir, f"{new_name}_fastqc.zip")
            
            # 如果文件存在，进行重命名
            if os.path.exists(original_html):
                os.rename(original_html, new_html)
                print(f"重命名文件: {original_html} -> {new_html}")
            else:
                print(f"文件不存在: {original_html}")
            
            if os.path.exists(original_zip):
                os.rename(original_zip, new_zip)
                print(f"重命名文件: {original_zip} -> {new_zip}")
            else:
                print(f"文件不存在: {original_zip}")

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="根据 meta 文件中的第三列重命名输入文件目录下的 _fastqc.html 和 _fastqc.zip 文件")
    parser.add_argument("-m", "--meta", required=True, help="meta 文件路径")
    parser.add_argument("-d", "--dir", required=True, help="输入文件目录")
    return parser.parse_args()

def main():
    args = parse_args()
    rename_files(args.meta, args.dir)

if __name__ == "__main__":
    main()
