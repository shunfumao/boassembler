import util, pdb

def parse_params_bo(param_config_path):
  """parse params configs for bo.py

  The expected format: 
  - param type default range
  - skip # as comments
  - e.g. -f float 0.1 (0.0,1.0) # bla bla bla

  Args:
    param_config_path: absolute path of param config file.

  Returns:
    a dic w/ key as param str (e.g. f) and val as [default_val]
    a dic w/ key as param str (e.g. f) and val as (range_min, range_max)
    a dic w/ key as param str (e.g. f) and val as [aug param str (e.g. -f), tp]

    Note: these are mained to be used by BO framework

  """

  def convert(v, tp):
    if tp=='float':
      return float(v)
    elif tp=='int':
      return int(v)
    else:
      util.logging('unknown type: '+tp)
      return None

  res_default = {}
  res_range = {}
  res_param2str = {}

  with open(param_config_path, 'r') as fi:

    for line in fi:
      if line[0]=='#': continue
      tokens = [t for t in line.split() if t != '']
      if len(tokens)<4: continue
      if tokens[0][0]=='-':
        param_str = tokens[0]
        #TODO(shunfu) init '-' is not asc-ii
        #if param_str=='-min-frags-per-transfrag':
        #  pdb.set_trace()
        #param = param_str.split('-')[-1]
        param = param_str[1:]
        tp = tokens[1]

        res_param2str[param] = [param_str, tp]        

        val_default = convert(tokens[2], tp)
        val_range = tokens[3][1:-1].split(',')
        val_min = convert(val_range[0], tp)
        val_max = convert(val_range[1], tp)

        res_default[param] = [val_default]
        res_range[param] = tuple([val_min, val_max])
	
    util.logging('%s parsed as:'%param_config_path)
    util.logging('default:')
    util.logging(str(res_default))
    util.logging('range:')
    util.logging(str(res_range))
    util.logging('param2str:')
    util.logging(str(res_param2str))

  return res_default, res_range, res_param2str

def parse_params_old(param_config_path):
  """parse params configs.

  The expected format: 
  - param type default range
  - skip # as comments
  - e.g. -f float 0.1 (0.0,1.0) # bla bla bla

  Args:
    param_config_path: absolute path of param config file.

  Returns:
    a dic w/ key as param str (e.g. f) and val as [default_val]
    a dic w/ key as param str (e.g. f) and val as (range_min, range_max)
    a dic w/ key as param str (e.g. f) and val as [aug param str (e.g. -f), tp]

    Note: these are mained to be used by BO framework

  """

  def convert(v, tp):
    if tp=='float':
      return float(v)
    elif tp=='int':
      return int(v)
    else:
      util.logging('unknown type: '+tp)
      return None

  res_default = {}
  res_range = {}
  res_param2str = {}
  res_range_lis=[]
  param_str_list = []

  with open(param_config_path, 'r') as fi:

    for line in fi:
      if line[0]=='#': continue
      tokens = [t for t in line.split() if t != '']
      if len(tokens)<4: continue
      if tokens[0][0]=='-':
        param_str = tokens[0]
        #TODO(shunfu) init '-' is not asc-ii
        #if param_str=='-min-frags-per-transfrag':
        #  pdb.set_trace()
        #param = param_str.split('-')[-1]
        param = param_str[1:]
        tp = tokens[1]

        res_param2str[param] = [param_str, tp]        

        val_default = convert(tokens[2], tp)
        val_range = tokens[3][1:-1].split(',')
        val_min = convert(val_range[0], tp)
        val_max = convert(val_range[1], tp)

        res_default[param] = [val_default]
	if tp=='float':
          res_range[param] = tuple([val_min, val_max])
	else:
	  res_range[param] = tuple([i for i in range(val_min, val_max+1)])

	# Creating a list of dicts; a dict per parameter
	res_range_lis.append({'name':str(param), 'type':str('continuous' if tp=='float' else 'discrete'), 'domain':tuple([val_min, val_max])})
        param_str_list.append(param_str)
	
    util.logging('%s parsed as:'%param_config_path)
    util.logging('default:')
    util.logging(str(res_default))
    util.logging('range:')
    util.logging(str(res_range))
    util.logging('param2str:')
    util.logging(str(res_param2str))

  #return res_default, res_range, res_param2str
  #pdb.set_trace()
  return res_range_lis, res_param2str, param_str_list, res_default, res_range

def parse_params2(param_config_path):
  '''
  used by test_extAssembler.py
  '''
  res_range_lis, res_param2str, param_str_list, res_default, res_range = parse_params_old(param_config_path)

  params = {}
  for k, v in res_default.items():
    param_str = res_param2str[k][0]
    v = v[0]
    params[param_str] = v

  print '----- parse_params2 -----'
  print params
  return res_default, res_range, res_param2str, params

def parse_params(param_config_path):
  '''
  used for gpyopt
  '''
  res_range_lis, res_param2str, param_str_list, _, _ = parse_params_old(param_config_path)
  return res_range_lis, res_param2str, param_str_list
