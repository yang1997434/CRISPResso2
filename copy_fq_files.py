#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import shutil

def read_barcodes(barcode_file):
    """
    从输入文件中读取第一列的barcode，返回一个列表。
    假设文件为制表符分隔，每行第一列为 barcode。
    """
    barcodes = []
    with open(barcode_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            # 取第一列
            barcode = parts[0]
            barcodes.append(barcode)
    return barcodes

def copy_files_by_barcode(source_dir, dest_dir, barcodes):
    """
    在 source_dir 中查找文件名包含任一 barcode 且以 .fq.gz 结尾的文件，
    复制到 dest_dir 中。
    返回复制的文件列表。
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    copied_files = []
    # 遍历源目录下所有文件（仅考虑文件，不递归子目录）
    for filename in os.listdir(source_dir):
        if not filename.endswith(".fq.gz"):
            continue
        for barcode in barcodes:
            if barcode in filename:
                src_path = os.path.join(source_dir, filename)
                dst_path = os.path.join(dest_dir, filename)
                shutil.copy(src_path, dst_path)
                copied_files.append(filename)
                # 如果一个文件可能匹配多个barcode，则可以 break
                break
    return copied_files

def main():
    parser = argparse.ArgumentParser(
        description="根据输入文件中第一列的barcode，从指定源目录中复制包含该barcode的fq.gz文件到目标目录"
    )
    parser.add_argument("-b", "--barcode_file", required=True,
                        help="包含barcode的文本文件，每行第一列为barcode")
    parser.add_argument("-s", "--source", required=True,
                        help="源目录，存放fq.gz文件")
    parser.add_argument("-d", "--dest", required=True,
                        help="目标目录，将复制的文件存放于此")
    args = parser.parse_args()

    barcodes = read_barcodes(args.barcode_file)
    if not barcodes:
        print("未读取到任何barcode，请检查文件格式。")
        return

    copied = copy_files_by_barcode(args.source, args.dest, barcodes)
    print("共复制 {} 个文件到目录 {}".format(len(copied), args.dest))
    if copied:
        print("复制的文件如下：")
        for f in copied:
            print(f)

if __name__ == "__main__":
    main()
