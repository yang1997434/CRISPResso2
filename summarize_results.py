#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sgRNA编辑效率结果汇总脚本
将所有*_results.txt文件整合成一个汇总表格
"""

import os
import re
import sys
import glob

def extract_data_from_result_file(file_path):
    """
    从结果文件中提取所需数据
    
    参数:
    file_path (str): 结果文件路径
    
    返回:
    tuple: (文件ID, 总读数, 区间内有编辑的读数, 区间编辑效率)
    """
    # 从文件名中提取ID
    file_name = os.path.basename(file_path)
    file_id = file_name.replace('_results.txt', '')
    
    # 初始化数据
    total_reads = 0
    edited_reads = 0
    editing_efficiency = 0.0
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # 使用正则表达式提取数据
            total_reads_match = re.search(r'总读数: (\d+)', content)
            edited_reads_match = re.search(r'区间内有编辑的读数: (\d+)', content)
            efficiency_match = re.search(r'区间编辑效率: (\d+\.\d+)', content)
            
            if total_reads_match:
                total_reads = int(total_reads_match.group(1))
            if edited_reads_match:
                edited_reads = int(edited_reads_match.group(1))
            if efficiency_match:
                editing_efficiency = float(efficiency_match.group(1))
                
    except Exception as e:
        sys.stderr.write(f"处理文件 {file_path} 时出错: {str(e)}\n")
        return file_id, 0, 0, 0.0
    
    return file_id, total_reads, edited_reads, editing_efficiency

def summarize_results(results_dir, output_file):
    """
    汇总所有结果文件到一个文件
    
    参数:
    results_dir (str): 包含结果文件的目录
    output_file (str): 输出汇总文件的路径
    """
    # 查找所有结果文件
    result_files = glob.glob(os.path.join(results_dir, '*_results.txt'))
    
    if not result_files:
        sys.stderr.write(f"错误: 未在 {results_dir} 目录下找到任何 *_results.txt 文件\n")
        sys.exit(1)
    
    print(f"找到 {len(result_files)} 个结果文件")
    
    # 提取每个文件的数据
    data = []
    for file_path in result_files:
        file_id, total_reads, edited_reads, efficiency = extract_data_from_result_file(file_path)
        data.append((file_id, total_reads, edited_reads, efficiency))
    
    # 将数据写入输出文件
    try:
        with open(output_file, 'w') as f:
            # 写入表头
            f.write("样本ID\t总读数\t编辑读数\t编辑效率(%)\n")
            
            # 写入每个样本的数据
            for file_id, total_reads, edited_reads, efficiency in data:
                f.write(f"{file_id}\t{total_reads}\t{edited_reads}\t{efficiency}\n")
                
        print(f"汇总完成。结果已保存到 {output_file}")
        
    except Exception as e:
        sys.stderr.write(f"写入输出文件 {output_file} 时出错: {str(e)}\n")
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='sgRNA编辑效率结果汇总工具')
    parser.add_argument('--dir', '-d', default='.',
                       help='包含结果文件的目录 [默认: 当前目录]')
    parser.add_argument('--output', '-o', default='summary_results.txt',
                       help='输出汇总文件的路径 [默认: summary_results.txt]')
    
    args = parser.parse_args()
    
    summarize_results(args.dir, args.output)

if __name__ == "__main__":
    main()
