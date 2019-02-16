source_alignment="data/chr1_chr15_cov_5_10_15.bam"
destination_alignment="data/ex2.bam"
target_chroms="chr1,chr15"
target_coverage="5,7,12"
n_per_cov=3
span=10000

python subsample.py -a $source_alignment \
                    -o $destination_alignment \
                    -chroms $target_chroms \
                    -covs $target_coverage \
                    -N_per_cov $n_per_cov \
                    -span $span


