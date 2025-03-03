import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def add_file_id_page(file_id):
    """
    创建一个包含文件ID的临时PDF页面，文件ID放在页面的正中间
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # 获取页面的宽度和高度
    width, height = letter
    
    # 设置字体和字体大小
    c.setFont("Helvetica-Bold", 24)  # 设置字体为Helvetica，字号为24
    
    # 居中绘制文件ID
    c.drawCentredString(width / 2, height / 2, f"File ID: {file_id}")  # 将文本放置在页面的正中间
    
    c.save()
    
    # 将生成的页面返回为一个PDF文件
    packet.seek(0)
    reader = PdfReader(packet)
    return reader.pages[0]

def merge_pdfs(input_folder, output_file):
    """
    合并文件夹内的所有PDF，并且为每个PDF添加ID页
    """
    pdf_writer = PdfWriter()
    
    # 遍历文件夹内的所有PDF文件
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.pdf'):
            file_path = os.path.join(input_folder, filename)
            
            # 为当前PDF文件创建一个文件ID页
            file_id = filename.split('.')[0]  # 使用文件名作为ID
            file_id_page = add_file_id_page(file_id)
            
            # 添加文件ID页
            pdf_writer.add_page(file_id_page)
            
            # 读取并合并当前PDF文件
            reader = PdfReader(file_path)
            for page in reader.pages:
                pdf_writer.add_page(page)
    
    # 输出合并后的PDF
    with open(output_file, "wb") as output_pdf:
        pdf_writer.write(output_pdf)
    print(f"合并后的PDF文件已保存至: {output_file}")

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="合并多个PDF文件并为每个文件添加ID页")
    parser.add_argument("-i", "--input_dir", required=True, help="存放PDF文件的文件夹路径")
    parser.add_argument("-o", "--output_file", required=True, help="合并后PDF的输出路径和文件名")
    return parser.parse_args()

def main():
    # 解析命令行参数
    args = parse_args()
    
    # 调用合并PDF函数
    merge_pdfs(args.input_dir, args.output_file)

if __name__ == "__main__":
    main()
