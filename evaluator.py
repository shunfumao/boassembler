import util, pdb

def evaluate(ref_gtf, assembly_gtf, eval_res_prefix):

  """The function generate eval statistics for assembly results.

  Args:
    ref_gtf: a ref assembly in gtf format
    assembly_gtf: assembly res in gtf format
    eval_res_prefix: the prefix for a set of files that store eval metrics

  Returns:
    a set of files that store eval metrics
  """

  cmd = 'gffcompare -R -r %s -o %s %s'%(ref_gtf, eval_res_prefix, assembly_gtf)
  util.run_cmd(cmd)

  # util.logging('eval res stored at:')
  # util.run_cmd('ls %s*'%eval_res_prefix, show_cmd=False)

  return

def evaluate_shannon(ref_fa, assembly_fa, eval_res_dir):

  """The function generate eval statistics for Shannon's assembly results.

  Args:
    ref_fa: a ref assembly in fa format
    assembly_fa: assembly res in fa format
    eval_res_dir: the dir for a set of files that store eval metrics

  Returns:
    a set of eval files that store in eval_res_dir
  """

  #TODO(bowen): integrate analysis into Shannon_RNASeq_Cpp
  cmd = 'Shannon_RNASeq_Cpp ref-align --input %s --ref %s --output_dir %s'%(assembly_fa, ref_fa, eval_res_dir)
  # pdb.set_trace()
  util.run_cmd(cmd)

def extract_stat(eval_res_prefix):

  """Extract stat from eval_res_prefix.stats file.

  Args:
    eval_res_prefix: prefix of a set of files generated from evaluate()
  Returns:
    a dic w/ key as metric (e.g. Intron) and val as [sens, precision]
      possible keys: Base, Exon, Intron, Transcript etc
  """

  stat_path = eval_res_prefix + '.stats'

  stat = {}  # key: metric val: [sens, prec]

  with open(stat_path, 'r') as fi:

    for line in fi:
      if line[0]=='#': continue
      tokens = [t for t in line.split() if t != '']
      if len(tokens)<5: continue
      if tokens[1]=='level:':
        stat[tokens[0]]=[float(tokens[2]), float(tokens[4])]

  util.logging('extracted stats:')
  util.logging(stat)

  return stat
 
def extract_stat_shannon(eval_res_dir):

  """Extract stat from eval_res_dir/summary.log file.

  Args:
    eval_res_dir: dir of a set of files generated from evaluate_shannon()
  Returns:
    a dic w/ key as metric (e.g. aligned, detected, ref) and val int
  """

  #TODO(bowen): better summary log
  stat_path = eval_res_dir + '/summary.log'

  stat = {}

  with open(stat_path, 'r') as fi:

    for line in fi:
      if line[0]=='#': continue
      tokens = [t for t in line.split() if t != '']
      if len(tokens)==0: continue

      if tokens[0]=='total' and tokens[1]=='seq':
        stat['aligned'] = int(tokens[2])
        stat['detected'] = int(tokens[4])

      elif tokens[0]=='num_reference_seq':
        stat['ref'] = int(tokens[1])

  util.logging('extracted stats:')
  util.logging(stat)

  return stat

def calc_metric(stat_dic, metric_type):
  """Calibrated metric.

  Args:
    stat_dic: a dic w/ key as e.g. Intron etc and val as [sens, precision]
      obtained from extract_stat
    metric_type: indicates the way to calculated the metric.
      possible types:
        'tr-sum' 
        'tr-f1'
  Returns:
    a fload of metric
  """

  if metric_type == 'tr-sum':
    sens, prec = stat_dic['Transcript']
    return float(sens+prec)
  elif metric_type == 'tr-f1':
    sens, prec = stat_dic['Transcript']
    return float(2*sens*prec/float(sens+prec))
  else:
    util.logging('unknown metric_type; None to be returned.')
    return None

def calc_metric_shannon(stat_dic, metric_type):
  """Calibrated metric.

  Args:
    stat_dic: a dic w/ key as aligned, detected and ref
    metric_type: indicates the way to calculated the metric.
      possible types:
        'tr-sum' 
        'tr-f1'
  Returns:
    a fload of metric
  """

  sens = float(stat_dic['aligned'])/stat_dic['ref']
  prec = float(stat_dic['aligned'])/stat_dic['detected']

  if metric_type == 'tr-sum':
    return float(sens+prec)
  elif metric_type == 'tr-f1':
    return float(2*sens*prec/float(sens+prec))
  else:
    util.logging('unknown metric_type; None to be returned.')
    return None