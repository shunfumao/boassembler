import sys
import pdb
sys.path.append("./")

from bayes_opt import BayesianOptimization

import assembler
import config
import evaluator
import util
from argparse import ArgumentParser

def call_and_eval_assembler(assembler_name, 
                            metric_type,
                            paths,
                            param2str=None):

  def _call_and_eval_assembler(**kwargs):

    params = util.kwargs_to_params_dic(kwargs, param2str)
    if params is not None:
      lam = params.get('-lam', 0.5)
      params.pop('-lam', None)
    else:
      lam = 0.5

    assembler.run_assembler(assembler_name,
                            paths['read_alignment'],
                            paths['assembly_gtf'],
                            params)

    evaluator.evaluate(paths['ref_gtf'],
                         paths['assembly_gtf'],
                         paths['eval_res_prefix'])

    metric_stat = evaluator.extract_stat(paths['eval_res_prefix'])    

    #TODO(shunfu): find a good metric for BO
    if metric_stat == {}:
      metric = 0
    else:
      metric = evaluator.calc_metric(metric_stat, metric_type, lam)

    # res logs
    util.logging('assembler:'+assembler_name, paths['log'])
    util.logging('params: default' if params is None else 'params:\n'+str(params), paths['log'])
    util.logging('metric stat is: %s'%str(metric_stat), paths['log'])
    util.logging('metric (%s, lam=%.2f) is %f\n'%(metric_type, lam, metric), paths['log'])

    return metric

  return _call_and_eval_assembler
  
def check_baseline(assembler_name, metric_type, paths):

  print '----- CHECK ASSEMBLY BASELINE -----'

  param_default, param_range, param2str = config.parse_params_bo(paths['param_config_path'])

  fn = call_and_eval_assembler(assembler_name, metric_type, paths)
  metric = fn()

  msg = 'Baseline metric (%s) for %s: %f\n\n'%(metric_type, assembler_name, metric)
  util.logging(msg, paths['log'])
  
  print msg
  return

def check_bo_tune(assembler_name, metric_type, paths):

  print '----- CHECK BO TUNE -----'
  
  param_default, param_range, param2str = config.parse_params_bo(paths['param_config_path'])

  bo = BayesianOptimization(call_and_eval_assembler(assembler_name, metric_type, paths, param2str),
                            param_range)

  gp_params = {'kernel': None, 'alpha': 1e-3}
  bo.maximize(init_points=5, n_iter=20, kappa=5, **gp_params)

  msg = 'BO-tuned metric (%s) for %s:\n'%(metric_type, assembler_name)
  msg += 'bo.res[max]:\n'
  msg += str(bo.res['max'])

  util.logging(msg, paths['log'])

  msg += '\nbo tune done\n'
  msg += '%s written\n'%paths['log']
  print msg

  return

def show_paths(paths):

  print '----- SHOW PATHS -----'

  for k, v in paths.items():
    print k, ':  ', v
  print ''
  return

def main():
  """
  Usage:
  """

  parser = ArgumentParser()

  parser.add_argument(
    '--assembler_name',
    default='stringtie',
    help='assembler whose hyper-parameter to be tuned. stringtie(default) and cufflinks supported')

  parser.add_argument(
    '--param_config',
    default='config/params_stringtie.txt',
    help='hyper-parameter config file. only numeric (int or float) parameters supported. default is config/params_stringtie.txt')

  parser.add_argument(
    '--ref_gtf',
    default='ref/hg19_chr15-UCSC.gtf',
    help='transcriptome annotation to eval assembly performance')

  parser.add_argument(
    '--read_alignment',
    default='data/ex1.bam',
    help='dataset for assembly')

  parser.add_argument(
    '--metric_type',
    default='tr-f1',
    help='the metric score as feedback to BO. default is tr-f1 (F1 score for transcript sensitivity and precision)'
    )

  parser.add_argument(
    '--res_dir',
    help='the folder to store results.'
    )

  args = parser.parse_args()

  res_dir = args.res_dir
  res_temp = '%s/temp/'%(res_dir)
  assembler_name = args.assembler_name
  assembler_config = args.param_config
  read_alignment = args.read_alignment
  assembly_gtf = '%s/assembly.gtf'%(res_temp)
  ref_gtf = args.ref_gtf
  eval_res_prefix = '%s/eval'%(res_temp)
  metric_type = args.metric_type
  bo_log = '%s/bo.log'%(res_dir)

  #----- AUTO ----- 
  util.run_cmd('mkdir -p %s'%res_dir)
  util.run_cmd('mkdir -p %s'%res_temp)

  paths = {}

  paths['res_dir'] = res_dir

  paths['param_config_path'] = assembler_config 

  paths['ref_gtf'] = ref_gtf

  paths['read_alignment']= read_alignment

  paths['assembly_gtf'] = assembly_gtf

  paths['eval_res_prefix'] = eval_res_prefix

  paths['log'] = bo_log

  show_paths(paths)

  # baseline:
  check_baseline(assembler_name, metric_type, paths)

  # bo tune
  check_bo_tune(assembler_name, metric_type, paths)

  return

if __name__ == '__main__':
  main()
