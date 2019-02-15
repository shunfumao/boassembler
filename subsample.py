import pysam
import pdb
from util import iterCounter
import numpy as np

def get_dic_chrom_len(alignment):
  '''
  Input:
    alignment
  Output:
    dic with key as chrom val as chrom len
  '''
  dic_chrom_len = {}
  hd = pysam.AlignmentFile(alignment, 'rb').header #hd['SQ'] is a list of dics w/ keys 'LN' and 'SN' and vals chrom_len and chrom_name respectively
  for i in range(len(hd['SQ'])):
    chrom = hd['SQ'][i]['SN']
    chrom_len = hd['SQ'][i]['LN']
    dic_chrom_len[chrom] = chrom_len
    
  return dic_chrom_len

def analyze_alignment(alignment, output_alignment, span=100000):
  '''
  Input:
    bam format alignment
    span: per region span
  Output:
    dic_split: key - chrom val - {region (stt/inclusive, stp/exclusive): read counts}
      per region share same length
  '''
  dic_split = {}

  dic_chrom_len = get_dic_chrom_len(alignment) 

  for chrom in dic_chrom_len.keys():
    dic_split[chrom] = {}
    chrom_len = dic_chrom_len[chrom]
    N = chrom_len / span + 1
    for i in range(N):
      dic_split[chrom][(i*span, (i+1)*span)]=0

  nlines = sum([1 for l in pysam.AlignmentFile(alignment, 'rb')])
  print 'nlines=%d'%nlines
  iterCnt = iterCounter(nlines, 'process alignment (%d lines)'%nlines)
  with pysam.AlignmentFile(alignment, 'rb') as f:
    for rd in f:
      iterCnt.inc()
      reg_i = rd.pos / span
      reg = (reg_i*span, (reg_i+1)*span)
      dic_split[rd.reference_name][reg]+=1
    iterCnt.finish()
  '''
  region_size_list = []
  for chrom in dic_split.keys():
    for reg in dic_split[chrom].keys():
      region_size_list.append(dic_split[chrom][reg])
  hist, bins = np.histogram(region_size_list, bins=20)
  pdb.set_trace()
  '''
  #TODO(shunfu) fix cov_regions, read len and N_pick
  cov_regions = [(5,10)]
  for i in range(10):
    cov_regions.append(((i+1)*10, (i+2)*10))
  read_len = 100
  N_pick = 15 
  cov_dic = {}
  for chrom in dic_split.keys():
    for reg, cnt in dic_split[chrom].items():
      reg_cov = cnt * read_len / span
      for cov in cov_regions:
        if reg_cov >= cov[0] and reg_cov < cov[1]:
          cov_dic.setdefault(cov, []).append((chrom, reg[0], reg[1], cnt))

  dic_split2 = {} #key chrom val dic key region idx val cnt
  #N_pick = 50 #each cov_regions pick at most 10 at random
  for cov in cov_dic.keys():
    list_chrom_reg0_reg1_cnt = cov_dic[cov]
    perm_idx_list = np.random.permutation(len(list_chrom_reg0_reg1_cnt))
    for i in range(min(N_pick, len(perm_idx_list))):
      idx = perm_idx_list[i]
      chrom, reg0, reg1, cnt = list_chrom_reg0_reg1_cnt[idx]
      print cov, i, idx, chrom, reg0, reg1, cnt
      dic_split2.setdefault(chrom, {}).setdefault(reg0/span,cnt)
      
  fi = pysam.AlignmentFile(alignment, 'rb')
  #output_alignment = alignment + '.dmp'
  fo = pysam.AlignmentFile(output_alignment, 'wb', header=fi.header)
  cnt = 0
  iterCnt = iterCounter(nlines, 'dump %d'%nlines)
  for rd in fi:
    iterCnt.inc()
    chrom = rd.reference_name
    reg_i = rd.pos/span
    if chrom in dic_split2 and reg_i in dic_split2[chrom]:
      fo.write(rd)
      cnt += 1
  print '%s (%d reads)  written'%(output_alignment, cnt)
  iterCnt.finish()
  fi.close()
  fo.close()
  return dic_split2

if __name__ == '__main__':
  alignment_in_regions='/data1/shunfu1/ref_shannon_modi/data/sgRefShannon/snyderSim_1018a/hits.sorted.regions.bam'
  #to /data1/shunfu1/ref_shannon_modi/data/sgRefShannon/snyderSim_1018a/hits.sorted.regions.subsample.bam (119M)

  #alignment_in_regions='/data1/shunfu1/ref_shannon_modi/data/sgRefShannon/wwSim_1122a/hits.sorted.bam'

  #alignment_in_regions='/data1/shunfu/boassembler/alignments/snyder_small/hits.sorted.bam'
  #alignment_in_regions='small.bam'
  

  output_alignment = alignment_in_regions + '.dump.20190212.snyder.npick15'

  dic_split = analyze_alignment(alignment_in_regions, output_alignment)
  
