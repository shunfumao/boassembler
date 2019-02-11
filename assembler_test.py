import assembler
import util

def test_run_stringtie():
  assembler_name = 'stringtie'
  read_alignment='/home/shunfu/boassembler/data/alignment/hits.sorted.bam'
  res_gtf='/home/shunfu/boassembler/res/stringtie.gtf'
  _test_run_assembler(assembler_name, read_alignment, res_gtf)

def test_run_scallop():
  assembler_name = 'scallop'
  read_alignment='/home/shunfu/boassembler/data/alignment/hits.sorted.bam'
  res_gtf='/home/shunfu/boassembler/res/scallop.gtf'
  _test_run_assembler(assembler_name, read_alignment, res_gtf)

def test_run_cufflinks():
  assembler_name = 'cufflinks'
  read_alignment='/home/shunfu/boassembler/data/alignment/hits.sorted.bam'
  res_gtf='/home/shunfu/boassembler/res/cufflinks.gtf'
  _test_run_assembler(assembler_name, read_alignment, res_gtf)

def test_run_shannon():
  assembler_name = 'shannon'
  #TODO(shunfu): unify data storage
  reads = '/data1/bowen/Shannon_C_seq/test_data/medium.fasta'
  assembly_res = '/home/shunfu/boassembler/res/'
  _test_run_assembler(assembler_name, reads, assembly_res)

def _test_run_assembler(assembler_name, read_alignment, res_gtf):
  assembler.run_assembler(assembler_name, read_alignment, res_gtf)
  util.logging(res_gtf + ' written')
  return

if __name__ == '__main__':
  # test_run_stringtie()
  # test_run_scallop()
  test_run_cufflinks()
  # test_run_shannon()

