import subprocess, pdb, sys, time

def parent_dir(dir_path):
  if dir_path[0]=='/':
    isRelative = False
  else:
    isRelative = True
  dir_path = dir_path.split('/')
  dir_path = [itm for itm in dir_path if itm != '']

  if isRelative==False:
    return '/'+'/'.join(dir_path[:-1])+'/', dir_path[-1]
  else:
    if len(dir_path)==1:
      return '', dir_path[-1]
    else:
      return '/'.join(dir_path[:-1])+'/', dir_path[-1]

def run_cmd(cmd, shell=True, show_cmd=True):
  if show_cmd:
    logging('run_cmd:'+cmd)
  subprocess.call(cmd, shell=shell)

def params_dic2str(params_dic):
  """Convert a params_dic to string.
  
  For example,
    params_dic={'-a', 1} returns '-a 1'
    params_dic={'-b', 0.1} returns '-b 0.1'
  Currently only support int/float params.

  Args:
    params_dic: a dic of params
  Returns:
    params_str: a str representing params_dic
  """
 
  params_str = ''

  for k, v in params_dic.items():
    params_str += str(k) + ' ' + str(v) + ' '

  return params_str

def kwargs_to_params_dic(kwargs_dic, param2str):
  """Convert kwargs to params_dic.

  For example,
    kwargs = {'a':1, 'b':2.0}
    params2str = {'a':['-a', 'int'], 'b':['--b', 'float']}

  Returns
    res = {'-a': 1, '--b': 2.0}
      if kwargs_dic or param2str has no cotent, return None

  The main motivation to do this is: kwargs is passed
    from BO package, and res is to be used for assembler cmd
  """

  if (param2str is not None and len(param2str)>0) and \
     (kwargs_dic is not None and len(kwargs_dic)>0):
    
    params = {}

    for k, v in kwargs_dic.items():
      logging('k=%s, v=%s'%(k, str(v)))

      param_str = param2str[k][0]
      tp = param2str[k][1]

      if tp=='int':
        v = int(v)
      elif tp=='float':
        v = float(v)
      else:
        logging('invalid type')
	# Is it OK below for val??
        val = None
      params[param_str] = v

  else:

    params = None

  return params

def args_to_params_dic(argsa, param_str_list):

  if (param_str_list is not None and len(param_str_list)>0) and \
     (argsa is not None and len(argsa)>0):
    #pdb.set_trace()
    return dict(zip(param_str_list, argsa))
  else:
    return None


def logging(msg, log=None):
  """logging msg to screen (e.g. verbose) or to file (e.g. dump_path)."""

  if True: # True:  # verbose
    if len(msg)>2000:
      print '%s...%s'%(msg[:100], msg[-100:])
    else:
      print(msg)

  if log is not None:
    with open(log, 'a') as fo:
      fo.write(msg+'\n')

  return


'''
used to show progress on screen
''' 
class iterCounter:

    def __init__(self, N, msg):

        self.N = N
        self.msg = msg
        self.T = N/100
        self.p = 0
        self.q = 0

        return

    def finish(self):

        print('')#print an empty line for display purpose

        return

    def inc(self):

        if self.N<100:
            self.p += 1
            sys.stdout.write('\r');
            sys.stdout.write('[%s] %s: %.2f %%'%(str(time.asctime()), self.msg, float(self.p)*100.0/self.N));
            sys.stdout.flush()

        else:
            self.p += 1
            if self.p >= self.T:
                self.p = 0
                self.q += 1
                sys.stdout.write('\r');
                sys.stdout.write('[%s] %s: %d %%'%(str(time.asctime()), self.msg, self.q));
                sys.stdout.flush()

        return       
