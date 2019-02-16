# BOAssembler

### Contents <a id='contents'></a>

* <a href='#subsample'>Subsample</a>  

---

### Subsample a large read alignment <a id='subsample'></a>

For efficiency, BOAssembler is expected to tune parameters based on a small dataset (e.g. alignment) first, and then apply parameters onto large dataset assembly tasks. To prepare sampling a small dataset from a large dataset, you can use our prepared subsample.py. 

**Syntax**

```
python subsample.py -a /path/to/large/source/alignment \
                    -o /path/to/small/destination/alignment \
                    -chroms target_chrom_list \
                    -covs target_coverage_list \
                    -N_per_cov num_region_to_pick_per_coverage \
                    -span per_region_span
```

| Argument      | Description  |
| ------------- |:------------- |
| -a | full path to the large source alignment |
| -o | full path to the small destination alignment |
|-chroms| specify the target chromosomes, connected by comma. For example to extract only chr1 and chr15, try -chroms chr1,chr15. By default, it's -chroms all|
|-covs| specify the target coverage regions. For a region with span S bp, its coverage is defined as num_reads_aligned_in_this_region * read_len / S. For example, to extract only regions with coverage [5x, 10x) and [10x, 15x),  try -covs 5,10,15 . By default, it's -covs all|
|-N_per_cov|Specify for each coverage level, the number of regions to sample. For example, for coverage level [5x,10x), we have regions A, B and for coverage level [10x, 15x), we have regions C, D. If we set -N_per_cov 1, we will pick one region from [5x, 10x) and one region from [10x, 15x) randomly. If a coverage level has less regions, all regions will be picked. Defaut is 10.|
|-span| Specify the length of each region. For example, if -span 100000, each chromosome will be divided into 100000-bp regions.|

**Example 1. Sample one chromosome**

Let's use our prepared input alignment (data/chr1_chr15_cov_5_10_15.bam) which contains read alignments with coverage 5x~15x from chromosome 1 and chromosome 15. We hope to extract only chr15's alignments to store to (data/ex1.bam). We can use:

```
python subsample.py -a data/chr1_chr15_cov_5_10_15.bam \
                    -o data/ex1.bam \
                    -chroms chr15 \
                    -covs all \
                    -N_per_cov 5 \
                    -span 100000
```

**Example 2. Sample multiple chromosoms and multiple coverages**

Let's use our prepared input alignment (data/chr1_chr15_cov_5_10_15.bam) which contains read alignments with coverage 5x~15x from chromosome 1 and chromosome 15. We hope to extract coverage levels [5x,7x) and [7x,12x) (each coverage level at most 3 regions) from chromosome 1 and 15, and store to (data/ex2.bam). We can use:

```
python subsample.py -a data/chr1_chr15_cov_5_10_15.bam \
                    -o data/ex2.bam \
                    -chroms chr1,chr15 \
                    -covs 5,7,12 \
                    -N_per_cov 3 \
                    -span 100000
```


