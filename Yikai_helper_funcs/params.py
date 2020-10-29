# AUTOGENERATED! DO NOT EDIT! File to edit: 03_param_finetune.ipynb (unless otherwise specified).

__all__ = ['XgboostParamGenerator', 'LgbmParamGenerator', 'CatParamGenerator', 'RFParamGenerator']

# Cell
import random
import numpy as np
from fastcore.test import *
import xgboost
from sklearn.ensemble import RandomForestClassifier
from Yikai_helper_funcs import *
from sklearn.datasets import make_classification
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score

# Internal Cell

class HyperparamsGenerator:

    """
    This is the base class for {algo}ParamGenerator
    Kwargs are to passed into the param-greis

    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def params_included(self):
        return self.matrix_generation()

    def matrix_generation(self):

        param_matrix = {
            **self.kwargs
                }
        print('Please make sure to set "int" for certain parameters when you pass them to the model')

        return param_matrix

# Cell
class XgboostParamGenerator(HyperparamsGenerator):

    def matrix_generation(self):

        param_matrix = {
            'n_estimators': (5, 100),
            'max_depth': (3, 12),
            'min_child_weight': (0.01, 0.6),
            'gamma': (0.1, 40),
            'learning_rate': (0.005,0.3),
            'subsample': (0.05,1.0),
            **self.kwargs
                }
        return param_matrix


# Cell
class LgbmParamGenerator(HyperparamsGenerator):

    def matrix_generation(self):
        """
        Generate common param_matric for Lgbm;
        Notice that when the parameter is supposed to be the float type, the parameter bound should also be put as float,
        for example, 0. as the lower bound for "reg_alpha", instead of 0

        """

        param_matrix = {
            #'class_weight': [None, 'balanced'],
            #'boosting_type': ['gbdt', 'goss', 'dart'],
            'num_leaves': (30, 200),
            'learning_rate': (0.005,0.3),
            #'subsample_for_bin': list(range(20000, 300000, 20000)),
            'min_child_samples': (20, 500),
            'reg_alpha': (0., 0.99),
            'reg_lambda': (0., 0.99),
            'colsample_bytree': (0.6, 1),
            **self.kwargs
                }
        return param_matrix

# Cell
class CatParamGenerator(HyperparamsGenerator):

    def matrix_generation(self):

        param_matrix = {
                'iterations':  (10, 1000),
                 'depth': (2, 15),
                 'learning_rate': (0.005,0.3),
                 'bagging_temperature': (0.0, 1.0),
                 'border_count': (1, 255),
                 'l2_leaf_reg': (2, 30),
                 'scale_pos_weight': (0.1, 1),
            **self.kwargs
                }
        return param_matrix

# Cell
class RFParamGenerator(HyperparamsGenerator):

    def matrix_generation(self):

        param_matrix = {
                'n_estimators': (20, 500)
                , 'min_samples_split': (2, 100)
                #, 'max_features': random.randint(1, max(2, n_features))
                , 'max_depth': (20, 105)
                #, 'criterion': random.choice(['gini', 'entropy'])
                , 'ccp_alpha': (0.01, 0.1),
                 **self.kwargs
                }
        return param_matrix