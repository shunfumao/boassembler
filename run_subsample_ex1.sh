source_alignment="data/chr1_chr15_cov_5_10_15.bam"
destination_alignment="data/ex1.bam"
target_chroms="chr15"
target_coverage="all"
n_per_cov=5
span=10000

python subsample.py -a $source_alignment \
                    -o $destination_alignment \
                    -chroms $target_chroms \
                    -covs $target_coverage \
                    -N_per_cov $n_per_cov \
                    -span $span
