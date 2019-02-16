assembler_name="stringtie"
param_config="config/params_stringtie.txt"
ref_gtf="ref/hg19_chr15-UCSC.gtf"
read_alignment="data/ex1.bam"
metric_type="tr-f1"
res_dir="res/"

python bo.py --assembler_name $assembler_name \
             --param_config $param_config \
             --ref_gtf $ref_gtf \
             --read_alignment $read_alignment \
             --metric_type $metric_type \
             --res_dir $res_dir
