import pysam
import pdb
from util import iterCounter
import numpy as np
import sys
from argparse import ArgumentParser

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

def analyze_alignment(alignment,
                      output_alignment,
                      target_chroms,
                      target_coverage,
                      N_per_cov,
                      span):
  '''
  Input:
    bam format alignment
    output_alignment: subsampled alignment
    target_chroms: all or chr_a,chr_b... the chroms to subsample
    target_coverage: all or a,b,... the coverage regions to subsample
    N_per_cov: number of sub-regions to random sample from each coverage category.
    span: per region span
  Output:
    dic_split2: key - chrom val - {region (stt/inclusive, stp/exclusive): read counts}
      per region share same length
    output_alignment: subsampled alignments will be stored here
  '''
  dic_split = {}

  dic_chrom_len = get_dic_chrom_len(alignment) 

  chrom_list = dic_chrom_len.keys()
  print 'availabe chroms: %s'%str(chrom_list)
  if target_chroms != 'all':
    target_chroms = [c for c in target_chroms.split(',') if c!='']
    chrom_list = [c for c in chrom_list if c in target_chroms]
  print 'used chroms: %s'%str(chrom_list)

  if target_coverage != 'all':
    cov_list1 = [int(c) for c in target_coverage.split(',') if c!='']
    coverage_regions = []
    for i in range(len(cov_list1)-1):
      coverage_regions.append((cov_list1[i], cov_list1[i+1]))
  else:
    coverage_regions=[(0, np.inf)]
  print 'target coverages: %s'%str(coverage_regions)
  #pdb.set_trace()

  for chrom in chrom_list:
    dic_split[chrom] = {}
    chrom_len = dic_chrom_len[chrom]
    N = chrom_len / span + 1
    for i in range(N):
      dic_split[chrom][(i*span, (i+1)*span)]=0

  nlines = sum([1 for l in pysam.AlignmentFile(alignment, 'rb')])
  print 'source alignment has nlines=%d'%nlines
  iterCnt = iterCounter(nlines, 'process alignment (%d lines)'%nlines)
  avg_read_len = 0
  cnt_read = 0
  with pysam.AlignmentFile(alignment, 'rb') as f:
    for rd in f:
      iterCnt.inc()
      if rd.reference_name not in chrom_list:
        continue
      #pdb.set_trace()
      #print 'a:',' cnt_rd:',cnt_read, ' rd len:', rd.query_length, ' avg rd len:', avg_read_len
      avg_read_len = float(cnt_read) / (cnt_read + 1) * avg_read_len + float(rd.query_length) / (cnt_read + 1)
      avg_read_len = int(avg_read_len)
      cnt_read += 1
      #print 'b:', 'avg rd len (new):', avg_read_len, ' cnt rd new:', cnt_read
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
  cov_regions = coverage_regions
  read_len = avg_read_len 
  N_pick = N_per_cov 
  cov_dic = {}
  for chrom in dic_split.keys():
    for reg, cnt in dic_split[chrom].items():
      reg_cov = cnt * read_len / span
      for cov in cov_regions:
        if reg_cov > cov[0] and reg_cov < cov[1]:
          cov_dic.setdefault(cov, []).append((chrom, reg[0], reg[1], cnt))

  print 'cov_dic:'
  for k in cov_dic.keys():
    print k
    for kk in cov_dic[k]:
      print '  ', kk 

  dic_split2 = {} #key chrom val dic key region idx val cnt
  print 'sample idx, cov category, sample idx per cov, actual idx per cov, chrom, region stt, regio stp, read cnts'
  sample_idx = 0
  for cov in cov_dic.keys():
    list_chrom_reg0_reg1_cnt = cov_dic[cov]
    perm_idx_list = np.random.permutation(len(list_chrom_reg0_reg1_cnt))
    for i in range(min(N_pick, len(perm_idx_list))):
      idx = perm_idx_list[i]
      chrom, reg0, reg1, cnt = list_chrom_reg0_reg1_cnt[idx]
      sample_idx += 1
      print sample_idx, cov, i, idx, chrom, reg0, reg1, cnt
      dic_split2.setdefault(chrom, {}).setdefault(reg0/span,cnt)
      
  fi = pysam.AlignmentFile(alignment, 'rb')
  fo = pysam.AlignmentFile(output_alignment, 'wb', header=fi.header)
  cnt = 0
  iterCnt = iterCounter(nlines, 'write output alignment %d'%nlines)
  for rd in fi:
    iterCnt.inc()
    chrom = rd.reference_name
    reg_i = rd.pos/span
    if chrom in dic_split2 and reg_i in dic_split2[chrom]:
      fo.write(rd)
      cnt += 1
  print '\n%s (%d reads)  written'%(output_alignment, cnt)
  iterCnt.finish()
  fi.close()
  fo.close()
  return dic_split2

def main():

  parser = ArgumentParser()
  
  parser.add_argument(
    '-a', help='source alignment path') #args[args.index('-a')+1]
  parser.add_argument(
    '-o', help='destination alignment path') #args[args.index('-o')+1]
  parser.add_argument(
    '-chroms', default='all',
    help='target chroms to extract. e.g. chr1,chr5,... default is all') #args[args.index('-c')+1]
  parser.add_argument(
    '-covs', default='all',
    help='target coverage to extract. e.g. 2,5,10,15 refer to cov [2x,5x),[5x,10x),[10x,15x) default is all')
  parser.add_argument(
    '-N_per_cov', type=int, default=10,
    help='number of sub-regions to sample from each coverage category. default is 10')
  parser.add_argument(
    '-span', type=int, default=10000,
    help='specify the span of the region per chrom is divided by')
  
  args = parser.parse_args()

  dic_split = analyze_alignment(args.a, #source_alignment,
                                args.o, #dest_alignment,
                                args.chroms, #target_chroms,
                                args.covs, #target_coverage,
                                args.N_per_cov,
                                args.span)

  return

if __name__ == '__main__':
  main()
