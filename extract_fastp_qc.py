import os
import json
import pandas as pd
import argparse

def extract_fastp_info(json_file):
    """
    从 fastp 的 JSON 文件中提取相关的 QC 数据
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            before_filtering = data.get("summary", {}).get("before_filtering", {})
            
            # 提取所需的信息
            info = {
                "total_reads": before_filtering.get("total_reads", None),
                "total_bases": before_filtering.get("total_bases", None),
                "q20_rate": before_filtering.get("q20_rate", None),
                "q30_rate": before_filtering.get("q30_rate", None),
                "read1_mean_length": before_filtering.get("read1_mean_length", None),
                "gc_content": before_filtering.get("gc_content", None)
            }
            return info
    except Exception as e:
        print(f"无法读取文件 {json_file}: {e}")
        return None

def process_fastp_reports(input_dir):
    """
    遍历指定目录，提取所有 fastp JSON 文件的信息并存储在一个 DataFrame 中
    """
    all_data = []
    
    # 遍历文件夹中的所有 JSON 文件
    for file_name in os.listdir(input_dir):
        if file_name.endswith("_report.json"):
            json_file_path = os.path.join(input_dir, file_name)
            file_id = file_name.split("_report.json")[0]  # 提取文件 ID（去掉 "_report.json" 后缀）
            
            # 提取文件信息
            file_info = extract_fastp_info(json_file_path)
            if file_info:
                file_info["file_id"] = file_id  # 添加文件ID作为一列
                all_data.append(file_info)
    
    # 将数据转换为 DataFrame 格式
    df = pd.DataFrame(all_data)
    df.set_index("file_id", inplace=True)  # 将文件ID设置为 DataFrame 的索引

    return df

def save_to_csv(df, output_file):
    """
    将结果保存到 CSV 文件
    """
    df.to_csv(output_file)
    print(f"结果已保存到 {output_file}")

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="提取 fastp JSON 报告中的 QC 信息并生成表格")
    parser.add_argument("-i", "--input_dir", required=True, help="存放 fastp JSON 文件的目标文件夹路径")
    parser.add_argument("-o", "--output_file", required=True, help="输出 CSV 文件的路径")
    return parser.parse_args()

def main():
    # 解析命令行参数
    args = parse_args()
    
    # 处理 fastp 报告并生成 DataFrame
    df = process_fastp_reports(args.input_dir)

    # 保存 DataFrame 到 CSV 文件
    save_to_csv(df, args.output_file)

if __name__ == "__main__":
    main()
