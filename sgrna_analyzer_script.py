#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sgRNA区间编辑效率分析脚本(简化版)
计算目标区间内符合条件的总体编辑比率
直接在命令行中运行: python3 sgrna_analyzer_simple.py 输入文件 输出文件 [选项]
"""

import argparse
import pandas as pd
import re
import sys
import os

def analyze_sgrna_editing(input_file, output_file, strand='forward', 
                         sgrna_seq="TCCCCATGCTTCCCCCAAACGCA", 
                         target_region=(3, 9)):
    """
    分析sgRNA编辑效率，计算目标区间内符合条件的总体编辑比率。
    
    参数:
    input_file (str): 包含比对序列的输入文件路径
    output_file (str): 保存结果的输出文件路径
    strand (str): 链方向，可以是'forward'（正链）或'reverse'（负链）
    sgrna_seq (str): 要定位的sgRNA序列
    target_region (tuple): 要分析的目标区域（包含起始和结束位置），采用1-基索引
    
    返回:
    float: 区间内的编辑效率百分比
    """
    # 转换为0-基索引
    target_start = target_region[0] - 1
    target_end = target_region[1] - 1
    
    # 加载数据
    try:
        df = pd.read_csv(input_file, sep='\t')
    except:
        try:
            # 如果制表符分隔符不起作用，尝试使用空格
            df = pd.read_csv(input_file, delim_whitespace=True)
        except Exception as e:
            sys.stderr.write(f"错误: 无法读取输入文件 {input_file}\n")
            sys.stderr.write(f"详细错误: {str(e)}\n")
            sys.exit(1)
    
    # 检查数据格式
    required_columns = ['Aligned_Sequence', 'Reference_Sequence', '#Reads']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        sys.stderr.write(f"错误: 输入文件缺少必要的列: {', '.join(missing_columns)}\n")
        sys.exit(1)
    
    # 总读数
    total_reads = df['#Reads'].sum()
    
    # 初始化编辑计数和总目标位点计数
    edited_reads = 0  # 区间内有编辑的读数总和
    total_target_bases = 0  # 区间内可能被编辑的碱基总数
    
    if strand == 'forward':
        # 正链：检查C到T的转换
        original_base = 'C'
        edited_base = 'T'
        
        # 处理每个比对序列
        for idx, row in df.iterrows():
            aligned_seq = row['Aligned_Sequence']
            ref_seq = row['Reference_Sequence']
            reads = row['#Reads']
            
            # 在参考序列中找到sgRNA的起始位置
            match = re.search(sgrna_seq, ref_seq)
            if match:
                sgrna_start = match.start()
                
                # 检查目标区域内是否有任何C->T编辑
                has_edit = False
                target_c_count = 0  # 目标区域内C的数量
                
                for i in range(target_start, target_end + 1):
                    ref_pos = sgrna_start + i
                    
                    # 检查此位置是否在两个序列的范围内
                    if ref_pos < len(ref_seq) and ref_pos < len(aligned_seq):
                        # 如果参考序列在此位置有C
                        if ref_seq[ref_pos] == original_base:
                            target_c_count += 1  # 增加目标C计数
                            
                            # 检查比对序列在此位置是否有T（C->T编辑）
                            if aligned_seq[ref_pos] == edited_base:
                                has_edit = True  # 标记为有编辑
                
                # 如果目标区域内有C->T编辑，增加编辑读数
                if has_edit:
                    edited_reads += reads
                
                # 增加目标区域内C的总数（考虑读数）
                total_target_bases += target_c_count * reads
    
    else:  # 负链
        # 负链：检查G到A的转换
        original_base = 'G'
        edited_base = 'A'
        
        # 处理每个比对序列
        for idx, row in df.iterrows():
            aligned_seq = row['Aligned_Sequence']
            ref_seq = row['Reference_Sequence']
            reads = row['#Reads']
            
            # 对于负链，我们需要找到sgRNA的反向互补
            # 将sgRNA转换为其反向互补
            complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
            rev_comp_sgrna = ''.join(complement.get(base, base) for base in reversed(sgrna_seq))
            
            # 在参考序列中找到反向互补sgRNA的起始位置
            match = re.search(rev_comp_sgrna, ref_seq)
            if match:
                sgrna_start = match.start()
                
                # 从右端计算位置（反向）
                rev_target_start = len(rev_comp_sgrna) - 1 - target_end
                rev_target_end = len(rev_comp_sgrna) - 1 - target_start
                
                # 检查目标区域内是否有任何G->A编辑
                has_edit = False
                target_g_count = 0  # 目标区域内G的数量
                
                for i in range(rev_target_start, rev_target_end + 1):
                    ref_pos = sgrna_start + i
                    
                    # 检查此位置是否在两个序列的范围内
                    if ref_pos < len(ref_seq) and ref_pos < len(aligned_seq):
                        # 如果参考序列在此位置有G
                        if ref_seq[ref_pos] == original_base:
                            target_g_count += 1  # 增加目标G计数
                            
                            # 检查比对序列在此位置是否有A（G->A编辑）
                            if aligned_seq[ref_pos] == edited_base:
                                has_edit = True  # 标记为有编辑
                
                # 如果目标区域内有G->A编辑，增加编辑读数
                if has_edit:
                    edited_reads += reads
                
                # 增加目标区域内G的总数（考虑读数）
                total_target_bases += target_g_count * reads
    
    # 计算编辑效率
    if total_target_bases > 0:
        editing_efficiency = (edited_reads / total_reads) * 100
    else:
        editing_efficiency = 0
        sys.stderr.write(f"警告: 目标区域内未找到可编辑的碱基 ({original_base})\n")
    
    # 将结果保存到文件
    try:
        with open(output_file, 'w') as f:
            f.write(f"sgRNA区间编辑效率分析\n")
            f.write(f"链: {strand}\n")
            f.write(f"目标碱基变化: {original_base} 到 {edited_base}\n")
            f.write(f"sgRNA序列: {sgrna_seq}\n")
            f.write(f"目标区域: {target_region[0]}-{target_region[1]}\n")
            f.write(f"总读数: {total_reads}\n")
            f.write(f"区间内有编辑的读数: {edited_reads}\n")
            f.write(f"区间内可编辑碱基总数: {total_target_bases}\n\n")
            
            f.write(f"区间编辑效率: {editing_efficiency:.4f}%\n")
    except Exception as e:
        sys.stderr.write(f"错误: 无法写入输出文件 {output_file}\n")
        sys.stderr.write(f"详细错误: {str(e)}\n")
        sys.exit(1)
    
    print(f"区间编辑效率: {editing_efficiency:.4f}%")
    return editing_efficiency

def parse_region(region_str):
    """解析区域字符串为元组，例如'3-9'变为(3,9)"""
    try:
        start, end = map(int, region_str.split('-'))
        return (start, end)
    except:
        sys.stderr.write(f"错误: 无效的区域格式 '{region_str}'，应为 'start-end'，例如 '3-9'\n")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='sgRNA区间编辑效率分析工具（简化版）')
    
    parser.add_argument('input_file', help='包含比对序列的输入文件')
    parser.add_argument('output_file', help='保存结果的输出文件')
    parser.add_argument('--strand', '-s', choices=['forward', 'reverse', '+', '-'], default='forward',
                       help='链方向（forward/+或reverse/-）[默认: forward]')
    parser.add_argument('--sgrna', '-g', default="TCCCCATGCTTCCCCCAAACGCA",
                       help='sgRNA序列 [默认: TCCCCATGCTTCCCCCAAACGCA]')
    parser.add_argument('--region', '-r', default="3-9",
                       help='目标区域，格式为"起始-结束"，例如"3-9" [默认: 3-9]')
    parser.add_argument('--version', '-v', action='version', 
                       version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    # 解析区域参数
    target_region = parse_region(args.region)
    
    # 转换链方向参数
    strand_param = args.strand
    if strand_param == '+':
        strand_param = 'forward'
    elif strand_param == '-':
        strand_param = 'reverse'
    
    # 执行分析
    try:
        print(f"正在分析 {args.input_file}...")
        analyze_sgrna_editing(
            args.input_file, 
            args.output_file, 
            strand_param, 
            args.sgrna, 
            target_region
        )
        print(f"分析完成。结果已保存到 {args.output_file}")
    except Exception as e:
        sys.stderr.write(f"错误: 分析过程中出现问题\n")
        sys.stderr.write(f"详细错误: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
