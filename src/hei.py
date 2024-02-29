import pandas as pd
from IPython.display import display
from src.logConfig import init_logger
logger = init_logger('hei.log')
logger.info('Started')


# Dictionaries of the HEI criteria for each food group
# 2010,2015,2020

hei_2010 = {
    'fruit_total': {'name': 'Total Fruit', 'goal': 0.8, 'total': 5},
    'fruit_whole': {'name': 'Whole Fruit', 'goal': 0.4, 'total': 5},
    'veg': {'name': 'Vegetables', 'goal': 1.1, 'total': 5},
    'grn_bean': {'name': 'Greens and Beans', 'goal': 0.2, 'total': 5},
    'whl_grn': {'name': 'Whole Grains', 'goal': 1.5, 'total': 10},
    'dairy': {'name': 'Dairy', 'goal': 1.3, 'total': 10},
    'prot': {'name': 'Total Protein', 'goal': 2.5, 'total': 5},
    'sf_plant': {'name': 'Seafood and plant protein', 'goal': 0.3, 'total': 5},
    # minimum <= 1.2
    'fa': {'name': 'MUFA+PUFA / SFA ratio', 'goal': 2.5, 'max': 1.2, 'total': 10},
    # excess = >4.3
    'rf_grn': {'name': 'Refined Grains', 'goal': 1.8, 'max': 4.3, 'total': 10},
    # excess = >2.0
    'sodium': {'name': 'sodium', 'goal': 1.1, 'max': 2, 'total': 10},
    # excess = >.5
    'empty_cal': {'name': 'empty calories (saturated fats, added sugars, alcohol)', 'goal': .19, 'total': 20}
}


class HEI:
    def __init__(self, df, cals, hei_dict):
        self.data = df.copy()
        self.df = df.copy()
        self.calories = cals
        self.hei_dict = hei_dict
        self.categories = list(hei_dict.keys())
        self.hei_df = pd.DataFrame()
        self.check_for_columns()
        self.hei_scores = pd.DataFrame()
        self.energy_adjust(cals)

    def check_for_columns(self):
        '''
        Checks the dataframe for the columns needed to calculate the HEI
        '''
        found = []
        for key in self.categories:
            if key in self.df.columns:
                self.hei_df[key] = self.df[key]
                found.append(key)
        logger.info(f'Found columns: {found}')

    def energy_adjust(self, cat):
        """Adjust the FFQ data to account for energy intake"""
        self.df['KCAL_NORM'] = self.data['DT_KCAL'] / 1000
        self.hei_df['KCAL_NORM'] = self.df['KCAL_NORM']

    def hei_cols(self, name, cats=[]):
        '''
        Takes a list of columns corresponding to an HEI category
        and sums them to create a new column for scoring
        '''
        if name not in self.categories:
            logger.info(
                f'{name} not in hei index. call instructions() to see available categories')
            return
        if name == 'fa':
            logger.info(
                f'{name} is a ratio and should be calculated with hei_fa()')
            return
        if name == 'empty_cal':
            logger.info(
                f'{name} is multiplied by type and should be calculated with hei_sofaa()')
            return

        self.hei_df[name] = self.df[cats].sum(axis=1)
        logger.info(f'Created column {name} with columns {cats}')

    def hei_fa(self, mufa, pufa, sfa):
        '''
        Takes the Fatty acids and calculates the ratio of MUFA+PUFA / SFA
        '''
        self.hei_df['fa'] = (
            self.data[mufa] + self.data[pufa]) / self.data[sfa]
        logger.info('Created column for fa')

    def hei_sofaa(self, sug, fat, al, norm=True):
        '''
        Takes the Fatty acids and calculates the ratio of MUFA+PUFA / SFA
        '''
        alc = self.df[al]/self.df['KCAL_NORM']
        sug = self.df[sug]/self.df['KCAL_NORM']
        fat = self.df[fat]/self.df['KCAL_NORM']

        alc = alc.apply(lambda x: 0 if x < 13 else x-13)
        self.hei_df['empty_cal'] = ((sug * 4) + (fat * 9) + (alc * 7))
        logger.info('Created column for sugars. sugars assumed to be in grams.')

    def hei_score(self):
        # score = np.zeros(self.df.shape[0])
        self.hei_scores = pd.DataFrame()

        for col in self.categories:
            if col == 'empty_cal':
                goal = self.hei_dict[col]['goal']
                total = self.hei_dict[col]['total']
                # score += self.hei_calc_sofaa(col, total)
                self.hei_scores.loc[:, f'hei_{
                    col}'] = self.hei_calc_sofaa(col, total)
                continue
            if col in ['rf_grn', 'sodium']:
                goal = self.hei_dict[col]['goal']
                total = self.hei_dict[col]['total']
                max = self.hei_dict[col]['max']
                # score += self.hei_calc_min(col,goal, total, max)
                self.hei_scores.loc[:, f'hei_{col}'] = self.hei_calc_min(
                    col, goal, total, max)
                continue

            if col == 'fa':
                goal = self.hei_dict[col]['goal']
                total = self.hei_dict[col]['total']
                self.hei_scores.loc[:, f'hei_{col}'] = self.hei_calc_fa(
                    col, goal, total)
                continue

            goal = self.hei_dict[col]['goal']
            total = self.hei_dict[col]['total']
            self.hei_scores.loc[:, f'hei_{col}'] = self.hei_calc(
                col, goal, total)

        self.hei_scores['hei_score'] = self.hei_scores.sum(axis=1)

    def instructions(self):
        '''
        Prints the instructions HEI category names
        '''
        for key, value in self.hei_dict.items():
            print(f'{key}: {value.name}')

    def hei_protein(self, cats):

        self.hei_scores.loc[:, f'hei_{'prot'}'] = self.hei_calc('prot', 2.5, 5)
        self.hei_df['NEED_MEAT'] = 5 - self.hei_df['prot']
        self.hei_df['EXCESS_MEAT'] = 2.5 * \
            (self.hei_df['prot']/self.hei_df['KCAL_NORM'])

        self.hei_df['meat'] = self.df['prot']-self.df['LEG_MEAT']
        self.hei_df

    def hei_calc(self, cat, goal, total):
        df = self.hei_df
        hei_val = (df[cat]/df['KCAL_NORM']).copy()
        hei_val = (hei_val/goal) * total
        hei_s = hei_val.apply(lambda x: total if x >= total else x)
        return hei_s

    def hei_calc_fa(self, cat, goal, total):
        df = self.hei_df
        hei_val = df[cat].copy()
        min = 1.2

        hei_val = hei_val.apply(
            lambda x: total if x >= goal else 0 if x <= min else
            total * ((x - min)/(goal-min)))
        return hei_val

    def hei_calc_min(self, cat, goal, total, min):
        df = self.hei_df
        hei_val = (df[cat]/df['KCAL_NORM']).copy()

        hei_val = hei_val.apply(
            lambda x: total if x <= goal else 0 if x >= min else
            (total * ((x - min)/(goal-min))))
        return hei_val

    def hei_calc_sofaa(self, cat, total):
        df = self.hei_df
        hei_val = (df[cat]/1000).copy()

        hei_val = hei_val.apply(
            lambda x: total if x <= .190 else 0 if x >= .5 else 20 * ((x - .5)/-.31))
        return hei_val
