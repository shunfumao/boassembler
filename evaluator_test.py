import evaluator
import util

def test_evaluate():

  ref_gtf = '/home/shunfu/boassembler/data/resRef/hg19_chr15-UCSC.gtf'
  assembly_gtf = '/home/shunfu/boassembler/res/stringtie.gtf'
  eval_res_prefix = '/home/shunfu/boassembler/res/stringtie_res'

  evaluator.evaluate(ref_gtf, assembly_gtf, eval_res_prefix)

  return

def test_evaluate_shannon():

  ref_fa = '/data1/bowen/Shannon_C_seq/reference_data/medium_SE_reference.fasta'
  assembly_fa = '/home/shunfu/boassembler/res/reconstructed_seq.fasta'
  eval_res_dir = '/home/shunfu/boassembler/res/analysis/'

  evaluator.evaluate_shannon(ref_fa, assembly_fa, eval_res_dir)

  return
  

def test_extract_stat():
  eval_res_prefix = '/home/shunfu/boassembler/res/stringtie_res'
  evaluator.extract_stat(eval_res_prefix)
  return

def test_extract_stat_shannon():
  eval_res_dir = '/home/shunfu/boassembler/res/analysis/'
  evaluator.extract_stat_shannon(eval_res_dir)
  return

def test_calc_metric():
  stat_dic = {'Transcript':[0.3, 0.4]}
  metric_types = ['tr-sum', 'tr-f1']
  for metric_type in metric_types:
    util.logging(str(metric_type))
    util.logging(str(evaluator.calc_metric(stat_dic, metric_type)))

def test_calc_metric_shannon():
  stat_dic = {'aligned':2429, 'detected':10713, 'ref':7703}
  metric_types = ['tr-sum', 'tr-f1']
  for metric_type in metric_types:
    util.logging(str(metric_type))
    util.logging(str(evaluator.calc_metric_shannon(stat_dic, metric_type)))

if __name__ == '__main__':

  # test_evaluate()
  # test_extract_stat()
  # test_calc_metric()

  # test_evaluate_shannon()
  # test_extract_stat_shannon()
  test_calc_metric_shannon()

