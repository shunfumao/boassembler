import util

def test_run_cmd():
  cmd = 'echo hello_world!'
  util.run_cmd(cmd, show_cmd=True)
  return

def test_params_dic2str():
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
  params_dic = {'-a':1, '-b':0.1}
  params_str = util.params_dic2str(params_dic)
  util.logging('params_dic:')
  util.logging(params_dic)
  util.logging('params_str:')
  util.logging(params_str)

  return

def test_kwargs_to_params_dic():

  kwargs_dic = {'a':1, 'b':2.0}
  param2str = {'a':['-a', 'int'], 'b':['--b', 'float']}  
  util.logging(util.kwargs_to_params_dic(kwargs_dic, param2str))

def test_logging():
  
  msg = 'hello world!'
  util.logging(msg, log='tmp.txt')

if __name__ == '__main__':
  # test_run_cmd()
  # test_params_dic2str()
  # test_kwargs_to_params_dic()
  test_logging()
