import sys
import pdb
sys.path.append("./")

from bayes_opt import BayesianOptimization

import assembler
import config
import evaluator
import util

def call_and_eval_assembler(assembler_name, 
                            metric_type,
                            paths,
                            param2str=None):

  def _call_and_eval_assembler(**kwargs):

    params = util.kwargs_to_params_dic(kwargs, param2str)

    if assembler_name != 'shannon':
      assembler.run_assembler(assembler_name,
                            paths['read_alignment'],
                            paths['assembly_gtf'],
                            params)

      evaluator.evaluate(paths['ref_gtf'],
                         paths['assembly_gtf'],
                         paths['eval_res_prefix'])

      metric_stat = evaluator.extract_stat(paths['eval_res_prefix'])    

      #TODO(shunfu): find a good metric for BO
      metric = evaluator.calc_metric(metric_stat, metric_type)

    else:
      #pdb.set_trace()
      util.run_cmd('rm -r %s/*'%paths['res_dir'])  # clear for every iterations

      assembler.run_assembler(assembler_name,
                              paths['read_alignment'],
                              paths['res_dir'],
                              params)

      evaluator.evaluate_shannon(paths['ref_gtf'],
                         paths['assembly_gtf'],
                         paths['eval_res_prefix'])

      metric_stat = evaluator.extract_stat_shannon(paths['eval_res_prefix'])    

      #TODO(shunfu): find a good metric for BO
      metric = evaluator.calc_metric_shannon(metric_stat, metric_type)
    # res logs
    util.logging('assembler:'+assembler_name, paths['log'])
    util.logging('params: default' if params is None else 'params:\n'+str(params), paths['log'])
    util.logging('metric stat is: %s'%str(metric_stat), paths['log'])
    util.logging('metric (%s) is %f\n'%(metric_type, metric), paths['log'])

    return metric

  return _call_and_eval_assembler
  
def check_baseline(assembler_name, metric_type, paths):

  param_default, param_range, param2str = config.parse_params_bo(paths['param_config_path'])

  fn = call_and_eval_assembler(assembler_name, metric_type, paths)
  metric = fn()

  util.logging('Baseline metric (%s) for %s: %f\n\n'%(metric_type, assembler_name, metric),
               paths['log'])

  return

def check_bo_tune(assembler_name, metric_type, paths):
  
  param_default, param_range, param2str = config.parse_params_bo(paths['param_config_path'])

  bo = BayesianOptimization(call_and_eval_assembler(assembler_name, metric_type, paths, param2str),
                            param_range)

  gp_params = {'kernel': None, 'alpha': 1e-3}
  bo.maximize(init_points=5, n_iter=50, kappa=5, **gp_params)
  # bo.maximize(n_iter=20, acq='ei', **gp_params)

  util.logging('BO-tuned metric (%s) for %s:'%(metric_type, assembler_name),
               paths['log'])

  util.logging('bo.res[max]:', paths['log'])
  util.logging(str(bo.res['max']), paths['log'])
  return

if __name__ == '__main__':
  """
  Usage:
  [1] run [assembler_name], compare baseline and bo-tuned res in terms of [metric_type,
      store outputs (e.g. assembly res, metric stat) under .../[case_id] folder
      and .../[case_id]_[assembler_name].log

    python bo.py --assembler_name [assembler_name]
                 --metric_type [metric_type]
                 --case_id [case_id]  # e.g. 20181002-1                 
  """

  args = sys.argv

  #TODO(shunfu): add more assemblers
  # assembler_name = 'stringtie'
  assembler_name = args[args.index('--assembler_name')+1]

  # metric_type = 'tr-f1'
  metric_type = args[args.index('--metric_type')+1]

  case_id = args[args.index('--case_id')+1]
  #pdb.set_trace()
  res_dir = '/home/shunfu/boassembler/res/%s'%case_id
  util.run_cmd('mkdir -p %s'%res_dir)

  #TODO(shunfu): paths via namespace
  paths = {}

  paths['res_dir'] = res_dir

  paths['param_config_path'] = '/home/shunfu/boassembler/config/params_%s.txt'%(assembler_name)

  if assembler_name=='shannon':

    paths['ref_gtf'] = '/data1/bowen/Shannon_C_seq/reference_data/medium_SE_reference.fasta'

    paths['read_alignment']='/data1/bowen/Shannon_C_seq/test_data/medium.fasta'

    paths['assembly_gtf']='%s/reconstructed_seq.fasta'%(res_dir)
    paths['eval_res_prefix'] = '%s/%s_res/'%(res_dir, assembler_name)

  else:
  
    paths['ref_gtf'] = '/home/shunfu/boassembler/data/resRef/hg19_chr15-UCSC.gtf'

    paths['read_alignment']='/home/shunfu/boassembler/data/alignment/hits.sorted.bam'

    paths['assembly_gtf']='%s/%s.gtf'%(res_dir, assembler_name)
    paths['eval_res_prefix'] = '%s/%s_res'%(res_dir, assembler_name)

  #TODO(shunfu): clear existing log
  paths['log']='/home/shunfu/boassembler/res/%s_%s.log'%(case_id, assembler_name) 

  # baseline:
  #pdb.set_trace()
  #check_baseline(assembler_name, metric_type, paths)

  # bo tune
  for k, v in paths.items():
    print k, v
  pdb.set_trace()
  check_bo_tune(assembler_name, metric_type, paths)
