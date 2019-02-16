# BOAssembler

### Contents <a id='contents'></a>

* <a href='#intro'>Introduction</a>
* <a href='#pub'>Publication</a>
* <a href='#pre_req'>Installation</a>
* <a href='#use_bo'>Use BOAssembler</a>  
* <a href='#extend'>Extend BOAssembler</a>
* <a href='#subsample'>Subsample</a>  

---

### Introduction <a id='intro'></a>

BOAssembler is a framework that enables end-to-end automatic tuning of RNASeq assemblers, based on Bayesian Optimization principles.

### Publication <a id='pub'></a>

If you find BOAssembler is helpful, we appreciate your citation of its intial [version](https://arxiv.org/abs/1902.05235) first (a more comprehensive version is under preparation):


    Shunfu Mao, Yihan Jiang, Edwin Basil Mathew, Sreeram Kannan. BOAssembler: a Bayesian Optimization Framework to Improve RNA-Seq Assembly Performance. arXiv:1902.05235

### Pre-requisites <a id='pre_req'></a>

The BOAssembler framework has dependencies on:

* Python (v2.7)
* Stringtie [link](https://ccb.jhu.edu/software/stringtie)
  * You may also use Cufflinks [link](http://cole-trapnell-lab.github.io/cufflinks/), could be slower
* gffcompare [link](https://ccb.jhu.edu/software/stringtie/gff.shtml)
* bayesian-optimization [link](https://github.com/fmfn/BayesianOptimization)
  * Future version will include GPyOpt, performance looks similar
* pysam [link](https://pysam.readthedocs.io/en/latest/api.html)

### Use BOAssembler <a id='use_bo'></a>

BOAssembler is used to tune hyper-parameters of reference-based RNA-Seq assembly tasks. Currently it mainly supports assembler of Stringtie and Cufflinks, but extend it to other reference-based RNA-Seq assemblers is easy.

**Syntax**

```
python bo.py --assembler_name <assembler_name> \
             --param_config <param_config> \
             --ref_gtf <ref_gtf> \
             --read_alignment <read_alignment> \
             --metric_type <metric_type> \
             --res_dir <res_dir>
```
| Argument      | Description  |
| ------------- |:------------- |
| --assembler_name| assembler whose hyper-parameter to be tuned. stringtie(default) and cufflinks supported |
|--param_config| hyper-parameter config file. only numeric (int or float) parameters supported. default is config/params_stringtie.txt |
|--ref_gtf| transcriptome annotation to eval assembly performance. an example is in ref/hg19_chr15-UCSC.gtf|
|--read_alignment| dataset for assembly in bam format. we recommend a small dataset, which can be prepared by sampling from a large alignment using our subsample.py|
|--metric_type| the metric score as feedback to BO. default is tr-f1 (F1 score for transcript sensitivity and precision)|
|--res_dir| the folder to store results. In particular, assembly results and its evaluation is stored at <res_dir>/temp/, the files are overwritten as BO iteration goes. BO tuned history stored at <res_dir>/bo.log, where you can find for each BO iteration, what are the parameters used and what is the assembly performance. |

**Example**

Let's use our prepared input alignment (data/ex1.bam) which contains read alignments from chromosome 15. We want to use Stringtie to assemble transcripts from ex1.bam. To find best parameters for this assembly task (evaluated internally by gffcompare based on ref/hg19_chr15-UCSC.gtf) by BOAssembler, we can under BOAssember project folder, use (see run_bo.sh):

```
python bo.py --assembler_name stringtie \
             --param_config config/params_stringtie.txt \
             --ref_gtf ref/hg19_chr15-UCSC.gtf \
             --read_alignment data/ex1.bam \
             --metric_type tr-f1 \
             --res_dir ex1_res
```

You will see BO iterations from the screen. Once BOAssembler is finished after around 50 iterations, you can check ex1_res/bo.log to find its recommended results at the end of log.

In this example, since ex1.bam is very small and almost no transcripts assembled, a metric_score of 0 will constantly appear.

### Extend BOAssembler <a id='extend'></a>

To extend BOAssember to use additional reference-based RNA-Seq assembler, you need:

* make sure your assembler is callable under unix shell script (Mac OS should also work)
  * the assembler should take read alignment in sam/bam format and output assembly results in gtf format  
* in assembler.py --> get_default_cmds, add a calling function based on Stringtie or Cufflinks example
* follow the config/params_stringtie.txt, make a copy for the new assembler, and modify its parameters (param name, int/float type, default val and range)

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

Let's use our prepared input alignment (data/chr1_chr15_cov_5_10_15.bam) which contains read alignments with coverage 5x~15x from chromosome 1 and chromosome 15. We hope to extract only chr15's alignments to store to (data/ex1.bam). We can use (see run_subsample_ex1.sh):

```
python subsample.py -a data/chr1_chr15_cov_5_10_15.bam \
                    -o data/ex1.bam \
                    -chroms chr15 \
                    -covs all \
                    -N_per_cov 5 \
                    -span 100000
```

**Example 2. Sample multiple chromosoms and multiple coverages**

Let's use our prepared input alignment (data/chr1_chr15_cov_5_10_15.bam) which contains read alignments with coverage 5x~15x from chromosome 1 and chromosome 15. We hope to extract coverage levels [5x,7x) and [7x,12x) (each coverage level at most 3 regions) from chromosome 1 and 15, and store to (data/ex2.bam). We can use (see run_subsample_ex2.sh):

```
python subsample.py -a data/chr1_chr15_cov_5_10_15.bam \
                    -o data/ex2.bam \
                    -chroms chr1,chr15 \
                    -covs 5,7,12 \
                    -N_per_cov 3 \
                    -span 100000
```


