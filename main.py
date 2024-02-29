from src.hei import HEI, hei_2010
import pandas as pd


outcomes = pd.read_csv('data/numom_outcomes.tsv', sep='\t')
ffq = pd.read_csv('data/numom_ffq.tsv', sep='\t')

data = pd.merge(outcomes, ffq, on='StudyID', how='right')
print(data.shape)
data['ADD_SUG'] = data['ADD_SUG'] * 4
data['LEG_MEAT'] = data['LEGUMES'] * 4
data['SOY_MEAT'] = data['M_SOY'] * 4
data['SODIUM'] = data['DT_SODI'] / 1000

hei = HEI(data, 'DT_KCAL', hei_2010)

hei.hei_cols('fruit_total', ['F_TOT'])
hei.hei_cols('fruit_whole', ['F_SOLID'])
hei.hei_cols('veg', ['V_TOT'])
hei.hei_cols('grn_bean', ['V_DRKGR', 'LEGUMES'])
hei.hei_cols('whl_grn', ['G_WHL'])
hei.hei_cols('dairy', ['D_TOT'])
hei.hei_cols('prot', ['M_MPF', 'M_EGG', 'M_NUTSD', 'M_SOY', 'LEG_MEAT'])
hei.hei_cols('sf_plant', ['M_FISH_HI', 'M_FISH_LO',
             'M_SOY', 'LEGUMES', 'M_NUTSD'])
hei.hei_cols('rf_grn', ['G_NWHL'])
hei.hei_cols('sodium', ['SODIUM'])

hei.hei_fa('DT_MFAT', 'DT_PFAT', 'DT_SFAT')
hei.hei_sofaa('ADD_SUG', 'DFAT_SOL', 'DT_ALCO')

hei.hei_score()
print(hei.hei_scores)
