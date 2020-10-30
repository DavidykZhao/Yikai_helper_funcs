# AUTOGENERATED! DO NOT EDIT! File to edit: 04_model_zoo.ipynb (unless otherwise specified).

__all__ = ['ModelIterator']

# Internal Cell
import random
import numpy as np
import pandas as pd
from fastcore.test import *
from sklearn.ensemble import RandomForestClassifier
from Yikai_helper_funcs import *
from sklearn.datasets import make_classification
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_multilabel_classification, make_regression
from sklearn.metrics import make_scorer, roc_auc_score
from fastai.data.transforms import get_files
from pathlib import Path

# from fastcore.basics import store_attr  # has bugs currently

from .params import *

# Cell
def _compile_results(root_dir):

    '''
    This is the function to conpile results from different models that are stored in a root dirctory.
    Results were stored in .json file where each .json file corresponds to one call of an optinizer.

    Params:
        root_dir (str or Path ): The root directory where all the .json files were stored
    '''
    if len(get_files(root_dir, extensions= ".json")) == 1:
        file = get_files(root_dir, extensions= ".json")[0]
        model_name = str(Path(file).parent).split("/")[-1]
        df_init = pd.read_json(file, lines=True)
        df_init['model'] = [model_name] * df_init.shape[0]
        return df_init

    else:
        for i, file in enumerate(get_files(root_dir, extensions= ".json")):
            #print(file)
            model_name = str(Path(file).parent).split("/")[-1]
            #print(model_name)
            if not i:
                df_init = pd.read_json(file, lines=True)
                df_init['model'] = [model_name] * df_init.shape[0]
            else:
                df = pd.read_json(file, lines=True)
                df['model'] = [model_name] * df.shape[0]
                df_final = pd.concat([df_init, df], ignore_index = True).sort_values('target', ascending= False)

        return df_final


# Cell
class ModelIterator:

    def __init__(self, x, y, *, rf_params = None, xgboost_params = None,
                 lightgbm_params = None, log_path = Path("./bayes_opt_logs"),
                rf_init_points = 10, rf_n_iter = 5,
                xgboost_init_points = 10, xgboost_n_iter = 5,
                lightgbm_init_points = 10, lightgbm_n_iter = 5):


        self.log_path = Path(log_path)
        if not rf_params: self.rf_params = {}
        if not lightgbm_params: self.lightgbm_params = {}
        if not xgboost_params: self.xgboost_params = {} # These are passed in the fit_predict method
        self.rf_init_points = rf_init_points
        self.rf_n_iter = rf_n_iter
        self.xgboost_init_points = xgboost_init_points
        self.xgboost_n_iter = xgboost_n_iter
        self.lightgbm_init_points = lightgbm_init_points
        self.lightgbm_n_iter = lightgbm_n_iter
        self.x = x
        self.y = y


    # TODO: Change hardcoded init_points & n_iter
    # TODO: Add try except blocks
    def _run_rf(self, x, y, **kwargs_model ):
        """  run RF and log tehm at self.log_path

        Params:
            kwargs_model: the range for hyperparameters that you want to overwrite the default generated from
                        RFParamGenerator().matrix_generation()

        """
        params_forest = RFParamGenerator(**kwargs_model).matrix_generation()
        @optimize_bayes_param(X=x, y=y)
        def optimize_forest(n_estimators, min_samples_split, max_depth , ccp_alpha):
            return RandomForestClassifier(n_estimators=int(n_estimators), min_samples_split=int(min_samples_split),
                                          max_depth = int(max_depth), ccp_alpha = float(ccp_alpha), n_jobs=-1)
        best_rf = optimize_forest(init_points=self.rf_init_points, n_iter=self.rf_n_iter, pbounds=params_forest, log_dir= self.log_path/"forest")
        return best_rf


    def _run_xgboost(self, x, y, **kwargs_model ):
        """  run Xgboost and log tehm at self.log_path

        Params:
            kwargs_model: the range for hyperparameters that you want to overwrite the default generated from
                        XgboostParamGenerator().matrix_generation()

        """
        params_xgboost = XgboostParamGenerator(**kwargs_model).matrix_generation()

        @optimize_bayes_param(X=x, y=y)
        def optimize_xgboost(n_estimators, max_depth, min_child_weight, gamma,learning_rate, subsample):
            return XGBClassifier(n_estimators= int(n_estimators), max_depth = int(max_depth),
            min_child_weight = min_child_weight , gamma = gamma, learning_rate = learning_rate,
            subsample = subsample,
            n_jobs=-1)

        best_xgboost = optimize_xgboost(init_points=self.xgboost_init_points, n_iter=self.xgboost_n_iter, pbounds=params_xgboost, log_dir=self.log_path/"xgboost")
        return best_xgboost

    def _run_lightgbm(self, x, y, **kwargs_model):

        """  run Lightgbm and log tehm at self.log_path

        Params:
            kwargs_model: the range for hyperparameters that you want to overwrite the default generated from
                        LgbmParamGenerator().matrix_generation()
            """

        params_lgbm = LgbmParamGenerator(**kwargs_model).matrix_generation()

        @optimize_bayes_param(X=x, y=y)
        def optimize_lgbm(num_leaves: int,learning_rate:float, min_child_samples, reg_alpha, reg_lambda, colsample_bytree):
            return LGBMClassifier(
                **{
                "num_leaves" : int(num_leaves),
                "learning_rate" : float(learning_rate),
               "min_child_samples" : int(min_child_samples),
                "reg_alpha" : float(reg_alpha),
                "reg_lambda" : float(reg_lambda),
               'colsample_bytree': float(colsample_bytree)
            })

        best_lightgbm = optimize_lgbm(init_points=5, n_iter=10, pbounds= params_lgbm, log_dir= self.log_path/"lgbm")
        return best_lightgbm

    def fit_predict(self, compile_results = True):

        best_rf = self._run_rf(self.x, self.y, **self.rf_params)
        best_xgboost = self._run_xgboost(self.x, self.y, **self.xgboost_params)
       # best_lightgbm = self._run_lightgbm(x, y, **self.lightgbm_params)

        print("""
        ----------------------------------------------------
        Returned best_rf, best_xgboost

        """)
        return best_rf, best_xgboost #, best_lightgbm

    def __call__(self):
        return self.fit_predict()

    def compile_results(self):
        return _compile_results(self.log_path)
