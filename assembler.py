import util, pdb

def get_default_cmds(assembler_name, read_alignment, res_gtf):
  """default commands for a particular assembler"""

  if assembler_name == 'stringtie':
    cmd = 'stringtie %s -o %s -p 25 '%(read_alignment, res_gtf)
  elif assembler_name == 'scallop':
    cmd = 'scallop -i %s -o %s --verbose 0'%(read_alignment, res_gtf)
  elif assembler_name == 'cufflinks':
    res_dir, _ = util.parent_dir(res_gtf)
    cmd = 'cufflinks -o %s %s'%(res_dir, read_alignment)
    pdb.set_trace()
  elif assembler_name == 'shannon':
    #TODO(shunfu): change the naming of read_alignment and res_gtf for de novo usage
    reads = read_alignment
    res_dir = res_gtf
    cmd = 'Shannon_RNASeq_Cpp shannon -l 101 -s %s -o %s -t 16 -m 100G -u 4 '%(reads, res_dir)
  else:
    util.logging('unknown assembler: %s'%assembler_name)
    cmd = None

  return cmd

def run_assembler(assembler_name,
                  read_alignment,
                  res_gtf,
                  params=None):
  """This function calls assembler (e.g. stringtie etc).

  Args:
    assembler_name: which assembler to use
    read_alignment: absolute path of read alignment file
    res_gtf: absolute path to store assembly res
    params: a dictionary of key as param string (e.g. -h etc)
      and val as the param value. Default is None.
  Returns:
    assembler output in gtf format stored in res_gtf
  """

  cmd = get_default_cmds(assembler_name, read_alignment, res_gtf)

  if params is not None:
    cmd = cmd + util.params_dic2str(params) 

  # pdb.set_trace()
  util.run_cmd(cmd)

  util.logging('%s written'%(res_gtf))

  return res_gtf
