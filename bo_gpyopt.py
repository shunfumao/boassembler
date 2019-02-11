import sys
import pdb
sys.path.append("./")

#from bayes_opt import BayesianOptimization

# Using GPyOpt instead of bayes_opt
import GPyOpt
import assembler
import config
import evaluator
import util, time

def call_and_eval_assembler(assembler_name, 
                            metric_type,
                            paths,
                            param2str=None,
                            param_str_list=None):
  start=time.clock()
  def _call_and_eval_assembler(ipt):
    #TODO(assembly time starts)


    if ipt is not None:
      '''
      ipt to be used for GPyOpt purpose
      pdb.set_trace()
      ipt = ipt[0]
      params = {}
      assert len(ipt) == len(param_str_list)
      for i in range(len(ipt)):
        params[param_str_list[i]]=ipt[i]
      pdb.set_trace()
      '''
      params = util.args_to_params_dic(ipt.tolist()[0],param_str_list)
    else:
      '''
      for baseline, we do not need params
      '''
      params = None

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

    #TODO(assembly time ends)
    return metric

  return _call_and_eval_assembler
  print('Time taken by assembler: '+str(time.clock() - start))
  
def check_baseline(assembler_name, metric_type, paths):

  print '----- check baseline -----'

  #param_default, param_range, param2str = config.parse_params(paths['param_config_path'])

  fn = call_and_eval_assembler(assembler_name, metric_type, paths)
  metric=fn(ipt=None) #ipt to be passed from GPyOpt. For default, it's None

  util.logging('Baseline metric (%s) for %s: %f\n\n'%(metric_type, assembler_name, metric),
               paths['log'])

  return

def check_bo_tune(assembler_name, metric_type, paths):
  
  #param_default, param_range, param2str = config.parse_params(paths['param_config_path'])
  """Reading the range of the parameters"""
  param_range, param2str, param_str_list =config.parse_params(paths['param_config_path'])
  

  """
  Possible values for kernel in bo object can be Exponential, OU, Matern32, Matern52, ExpQuad, RatQuad, Cosine
  With LCB and LCB_MCMC, use acquisition_weight
  With other acquisition_type values, use acquisition_jitter
  """

  bo = GPyOpt.methods.BayesianOptimization(call_and_eval_assembler(assembler_name, metric_type, paths, param2str, param_str_list), domain=param_range, verbosity=True, verbosity_model=True, initial_design_numdata=2, maximize=True, acquisition_jitter=0.2, kernel='Matern52', batch_size=10)
  
  
  #gp_params = {'kernel': None, 'alpha': 1e-3}
  #bo.maximize(init_points=2, n_iter=10, kappa=5, **gp_params)
  # bo.maximize(n_iter=20, acq='ei', **gp_params)
  bo.run_optimization(max_iter=10, verbosity=True)
  
  util.logging('FINAL RESULTS', paths['log'])
  util.logging('Kernel: '+bo.kwargs.get('kernel', 'Matern52'), paths['log'])
  util.logging('Model type: '+bo.model_type, paths['log'])
  util.logging('Acquisition type: '+bo.acquisition_type, paths['log'])
  if bo.acquisition_type in ('LCB', 'LCB_MCMC'):
    util.logging('Acquisition weight: '+str(bo.problem_config.kwargs.get('acquisition_weight', 2)), paths['log'])
  else:
    util.logging('Acquisition jitter: '+str(bo.problem_config.kwargs.get('acquisition_jitter', 0.01)), paths['log'])
  
  util.logging('Acquisition optimizer type: '+str(bo.acquisition_optimizer_type), paths['log'])
  util.logging('Initial design type: '+str(bo.initial_design_type), paths['log'])
  util.logging('Initial points: '+str(bo.initial_design_numdata), paths['log'])
  util.logging('Training batch size: '+str(bo.model_update_interval), paths['log'])
  util.logging('Test batch size: '+str(bo.batch_size), paths['log'])
  util.logging('Evaluator type: '+str(bo.evaluator_type), paths['log'])

  util.logging('BO-tuned metric (%s) for %s:'%(metric_type, assembler_name),
               paths['log'])
  util.logging('bo.res[max]:', paths['log'])
  util.logging(str(param_str_list)+" : "+str(bo.x_opt), paths['log'])
  
  util.logging('bo.f1[max]', paths['log'])
  util.logging(str(bo.fx_opt), paths['log'])
  util.logging('The log results stored at '+paths['log']+'\n')

  return

def get_dataset(dataset_description):
  if dataset_description=='wwSimChr15':
    alignment = '/data1/boassembler/data/dataset_wwSim_Chr15/alignment/hits.sorted.bam'
    ref_gtf = '/data1/boassembler/data/refRes/hg19_chr15-UCSC.gtf'
  elif dataset_description=='snyderSimChr15':
    alignment = '/data1/boassembler/data/dataset_snyderSim_Chr15/alignment/hits.sorted.bam'
    ref_gtf = '/data1/boassembler/data/refRes/hg19_chr15-UCSC.gtf'
  elif dataset_description=='kidneySimChr15':
    alignment = '/data1/boassembler/data/dataset_kidneySim_Chr15/alignment/hits.sorted.bam'
    ref_gtf = '/data1/boassembler/data/refRes/hg19_chr15-UCSC.gtf'
  else:
    print 'unknown dataset_description: %s'%dataset_description
    pdb.set_trace()
  return alignment, ref_gtf

if __name__ == '__main__':
  """
  Usage:
  [1] run [assembler_name], 
      compare baseline and bo-tuned res in terms of [metric_type],
      store outputs (e.g. assembly res, metric stat) under [res_dir]/[case_id] folder
      and [res_dir]/[case_id]_[assembler_name].log

    python bo_gpyopt.py --assembler_name [assembler_name]
                        --dataset [dataset]
                        --metric_type [metric_type]
                        --case_id [case_id]  # e.g. 20181002-1                 
                        [--res_root_dir [res_root_dir]] #e.g. /data1/boassembler/res/

  Note:
    dataset: wwSimChr15 snyderSimChr15 or kidneySimChr15
  """
  
  args = sys.argv

  #TODO(shunfu): add more assemblers
  # assembler_name = 'stringtie'
  assembler_name = args[args.index('--assembler_name')+1]

  # metric_type = 'tr-f1'
  metric_type = args[args.index('--metric_type')+1]

  # dataset
  alignment, ref_gtf = get_dataset(args[args.index('--dataset')+1]) 

  # case_id = '20190114_1_stringtie'
  case_id = args[args.index('--case_id')+1]

  # res dir
  if '--res_root_dir' in args:
    res_root_dir = args[args.index('--res_root_dir')+1]
  else:
    res_root_dir = '/data1/boassembler/res/'
  res_dir = '%s/%s'%(res_root_dir, case_id)
  util.run_cmd('mkdir -p %s'%res_dir)

  #TODO(shunfu): paths via namespace
  paths = {}

  paths['res_dir'] = res_dir

  paths['param_config_path'] = '/home/shunfu/boassembler/config/params_%s.txt'%(assembler_name)

  if assembler_name=='shannon':
    #TODO(de novo)

    paths['ref_gtf'] = '/data1/bowen/Shannon_C_seq/reference_data/medium_SE_reference.fasta'

    paths['read_alignment']='/data1/bowen/Shannon_C_seq/test_data/medium.fasta'

    paths['assembly_gtf']='%s/reconstructed_seq.fasta'%(res_dir)
    paths['eval_res_prefix'] = '%s/%s_res/'%(res_dir, assembler_name)

  else:
  
    paths['ref_gtf'] = ref_gtf
    paths['read_alignment']= alignment
    paths['assembly_gtf']='%s/%s.gtf'%(res_dir, assembler_name)
    paths['eval_res_prefix'] = '%s/%s_res'%(res_dir, assembler_name)

  #TODO(shunfu): clear existing log
  paths['log']='%s/%s_%s.log'%(res_root_dir, case_id, assembler_name) 

  # baseline:
  check_baseline(assembler_name, metric_type, paths)
  pdb.set_trace()
  
  # bo tune
  #pdb.set_trace()
  #check_bo_tune(assembler_name, metric_type, paths)
