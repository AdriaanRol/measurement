convlist=[
		('DAC(', 'P2_DAC(DAC_MODULE,'),
		('CNT_ENABLE(', 'P2_CNT_ENABLE(CTR_MODULE,'),
		('CNT_MODE(','P2_CNT_MODE(CTR_MODULE,'),
		('CONF_DIO(','P2_Digprog(DIO_MODULE,'),
		('DIGOUT(','P2_DIGOUT(DIO_MODULE,'),
		('CNT_CLEAR(','P2_CNT_CLEAR(CTR_MODULE,'),
		('CNT_READ(','P2_CNT_READ(CTR_MODULE,'),
		('DIGIN(','(P2_DIGIN_LONG(DIO_MODULE) AND '),
	]


def convert(fn_in,fn_out,conversion=(0,1)):

	with open(fn_out, 'w') as fout:
		with open(fn_in, 'r') as fin:
			i=0
			for line in fin:
				i=i+1
				if '#INCLUDE ADwinGoldII.inc' in line:
					line='#INCLUDE ADwinPro_All.inc\n#INCLUDE configuration.inc'
				if  ('#INCLUDE configuration.inc' in line) and conversion==(1,0)):
					line=''
				if 'DIGIN' in line:
					print 'WARNING: DIGIN found in line',i,'check output'
				for conv in convlist:
					line = line.replace(conv[conversion[0]],conv[conversion[1]])
				fout.write(line)

	            
if __name__ == '__main__':
	#conversion (source,target), 0 = gold, 1 = pro 
	#--> (0,1) = gold to pro
	#--> (1,0) = pro to gold
	convert('adwin_ssro_sp_pro.txt','adwin_ssro_sp_gold_conv.txt', conversion=(1,0))