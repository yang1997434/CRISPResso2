# 使用您的数据和参考基因组
#python barcode_analyzer.py -i test.tsv -o results.tsv -r /src_data01/Library/Human/refdata-GRCh38-2.1.0/fasta/genome.fa

#python barcode_analyzer_opt_v2.py -i raw_meta.tsv -o meta.tsv -r /src_data01/Library/Human/refdata-GRCh38-2.1.0/fasta/genome.fa -j 80

#python barcode_analyzer_opt_v2.py -i test.tsv -o result1.tsv -r /src_data01/Library/Human/refdata-GRCh38-2.1.0/fasta/genome.fa 

cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250220-amplicon-test-huada/1/fx/copy_fq_files.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250220-amplicon-test-huada/1/fx/sgrna_analyzer_script.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250220-amplicon-test-huada/1/fx/extract_fastp_qc.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250220-amplicon-test-huada/1/fx/rename_fq_files.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250220-amplicon-test-huada/1/fx/merge_pdfs.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250301-amplicon-fx/ABE/sgrna_analyzer_script_ABE.py ./
cp /src_data02/FA_BI_Noncoding/Personalized_analysis/20250301-amplicon-fx/ABE/summarize_results.py ./

mkdir -p rawdata ; python copy_fq_files.py -b group.txt -s /src_data02/FA_BI_Noncoding/Personalized_analysis/20250301-amplicon-fx/L01/ -d ./rawdata

mkdir -p cleandata ; cat group.txt | xargs -n 2 -P 40 -I {} sh -c 'set -- {};time cutadapt -a "$2" -o ./cleandata/"$1".fq.gz ./rawdata/A1220809068_L01_"$1".fq.gz '

mkdir -p fastqc ;cat group.txt | xargs -n 1 -P 10 -I {} sh -c 'set -- {}; time fastqc ./cleandata/"$1".fq.gz -o ./fastqc '

python rename_fq_files.py -m group.txt -d ./fastqc

mkdir -p fastp ;cat group.txt | xargs -n 3 -P 4 -I {} sh -c 'set -- {}; time fastp --thread 16 -i ./cleandata/"$1".fq.gz -h ./fastp/"$3"_report.html -j ./fastp/"$3"_report.json --disable_adapter_trimming --disable_quality_filtering --disable_length_filtering '

mkdir -p multiqc_report;  multiqc ./fastqc ./fastp  -o ./multiqc_report

python extract_fastp_qc.py -i ./fastp -o ./fastp_summary.csv

mkdir -p result ; cd  ./result  ; cat ../group.txt | xargs -n 5 -P 10 -I {} sh -c 'set -- {};time CRISPResso --fastq_r1 ../cleandata/"$1".fq.gz --amplicon_seq "$5"   --guide_seq "$4" --name  "$3" --min_frequency_alleles_around_cut_to_plot 0 --base_editor_output ' 

# 包括隐藏文件和文件夹
python folder_file_counter.py -d ./result -o stats.csv --include-hidden

cd .. 
##合并PDF
mkdir -p PDF ;  cat ./group.txt | xargs -n 5 -P 40 -I {} sh -c 'set -- {}; cp ./result/CRISPResso_on_"$3"/9.Alleles_frequency_table_around_sgRNA_"$4".pdf ./PDF/"$3".pdf '

python merge_pdfs.py -i ./PDF -o ./All_sample.pdf
##计算效率
mkdir -p summary ;  cat ./group.txt | xargs -n 5 -P 10 -I {} sh -c 'set -- {}; cp ./result/CRISPResso_on_"$3"/Alleles_frequency_table_around_sgRNA_"$4".txt ./summary/"$3".txt '

mkdir -p ABE;cd ABE
##cell 环境
cat ./meta.txt | xargs -n 3 -P 10 -I {} sh -c 'set -- {}; python sgrna_analyzer_script_ABE.py  ../summary/"$1".txt  ./"$1"_results.txt --strand "$3"  --sgrna "$2" --region 3-9 '   
python summarize_results.py -d ./  -o ../ABE_summary.txt
 

