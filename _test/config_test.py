import config,pdb

def test_parse_params():
  #param_config_path = '/home/shunfu/boassembler/config/params_stringtie.txt'
  param_config_path = '/home/shunfu/boassembler/config/params_cufflinks.txt'
  #param_config_path = '/home/shunfu/boassembler/config/params_shannon.txt'
  param_default, param_range, param2str = config.parse_params(param_config_path)
  #param_lis=config.parse_params(param_config_path)
  pdb.set_trace()
  return

if __name__ == '__main__':
  test_parse_params()


