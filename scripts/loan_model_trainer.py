import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE
import lightgbm as lgb
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class LoanApprovalModel:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
        self.PINCODE_MAP = {
            # Andhra Pradesh
            500001: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 1'},
            500002: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 1'},
            500003: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 1'},
            500004: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 1'},
            500005: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 1'},
            517001: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            517002: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            530001: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            530002: {'State': 'Andhra Pradesh', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            
            # Telangana
            502110: {'State': 'Telangana', 'State_Avg_Salary': 45000, 'Final_Tier': 'Tier 2'},
            502111: {'State': 'Telangana', 'State_Avg_Salary': 45000, 'Final_Tier': 'Tier 2'},
            502112: {'State': 'Telangana', 'State_Avg_Salary': 45000, 'Final_Tier': 'Tier 2'},
            502113: {'State': 'Telangana', 'State_Avg_Salary': 45000, 'Final_Tier': 'Tier 2'},
            502114: {'State': 'Telangana', 'State_Avg_Salary': 45000, 'Final_Tier': 'Tier 2'},
            
            # Karnataka - Bangalore
            560001: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560002: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560003: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560004: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560005: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560006: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560007: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560008: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560009: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560010: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560011: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560012: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560013: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560014: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560015: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560016: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560017: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560018: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560019: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560020: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560021: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560022: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560023: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560024: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560025: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560026: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560027: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560028: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560029: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560030: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560031: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560032: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560033: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560034: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560035: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560036: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560037: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560038: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560039: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560040: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560041: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560042: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560043: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560044: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560045: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560046: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560047: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560048: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560049: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560050: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560051: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560052: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560053: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560054: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560055: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560056: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560057: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560058: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560059: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560060: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560061: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560062: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560063: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560064: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560065: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560066: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560067: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560068: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560069: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560070: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560071: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560072: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560073: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560074: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560075: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560076: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560077: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560078: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560079: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560080: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560081: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560082: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560083: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560084: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560085: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560086: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560087: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560088: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560089: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560090: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560091: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560092: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560093: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560094: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560095: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560096: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560097: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560098: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560099: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            560100: {'State': 'Karnataka', 'State_Avg_Salary': 52000, 'Final_Tier': 'Tier 1'},
            
            # Maharashtra - Mumbai
            400001: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400002: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400003: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400004: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400005: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400006: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400007: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400008: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400009: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400010: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400011: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400012: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400013: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400014: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400015: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400016: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400017: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400018: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400019: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400020: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400021: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400022: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400023: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400024: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400025: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400026: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400027: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400028: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400029: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400030: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400031: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400032: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400033: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400034: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400035: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400036: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400037: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400038: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400039: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400040: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400041: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400042: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400043: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400044: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400045: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400046: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400047: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400048: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400049: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400050: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400051: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400052: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400053: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400054: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400055: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400056: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400057: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400058: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400059: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400060: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400061: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400062: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400063: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400064: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400065: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400066: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400067: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400068: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400069: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400070: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400071: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400072: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400073: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400074: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400075: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400076: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400077: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400078: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400079: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400080: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400081: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400082: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400083: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400084: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400085: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400086: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400087: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400088: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400089: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400090: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400091: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400092: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400093: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400094: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400095: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400096: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400097: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400098: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400099: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            400100: {'State': 'Maharashtra', 'State_Avg_Salary': 58000, 'Final_Tier': 'Tier 1'},
            # Pune
            411001: {'State': 'Maharashtra', 'State_Avg_Salary': 50000, 'Final_Tier': 'Tier 2'},
            411002: {'State': 'Maharashtra', 'State_Avg_Salary': 50000, 'Final_Tier': 'Tier 2'},
            411003: {'State': 'Maharashtra', 'State_Avg_Salary': 50000, 'Final_Tier': 'Tier 2'},
            411004: {'State': 'Maharashtra', 'State_Avg_Salary': 50000, 'Final_Tier': 'Tier 2'},
            411005: {'State': 'Maharashtra', 'State_Avg_Salary': 50000, 'Final_Tier': 'Tier 2'},
            
            # Delhi
            110001: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110002: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110003: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110004: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110005: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110006: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110007: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110008: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110009: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110010: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110011: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110012: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110013: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110014: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110015: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110016: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110017: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110018: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110019: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110020: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110021: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110022: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110023: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110024: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110025: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110026: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110027: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110028: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110029: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110030: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110031: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110032: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110033: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110034: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110035: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110036: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110037: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110038: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110039: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110040: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110041: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110042: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110043: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110044: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110045: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110046: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110047: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110048: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110049: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110050: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110051: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110052: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110053: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110054: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110055: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110056: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110057: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110058: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110059: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110060: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110061: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110062: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110063: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110064: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110065: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110066: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110067: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110068: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110069: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110070: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110071: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110072: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110073: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110074: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110075: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110076: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110077: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110078: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110079: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110080: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110081: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110082: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110083: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110084: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110085: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110086: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110087: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110088: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110089: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110090: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110091: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110092: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110093: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110094: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110095: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110096: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110097: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110098: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110099: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            110100: {'State': 'Delhi', 'State_Avg_Salary': 55000, 'Final_Tier': 'Tier 1'},
            
            # Tamil Nadu - Chennai
            600001: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600002: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600003: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600004: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600005: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600006: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600007: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600008: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600009: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600010: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600011: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600012: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600013: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600014: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600015: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600016: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600017: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600018: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600019: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600020: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600021: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600022: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600023: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600024: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600025: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600026: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600027: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600028: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600029: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600030: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600031: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600032: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600033: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600034: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600035: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600036: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600037: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600038: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600039: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600040: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600041: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600042: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600043: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600044: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600045: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600046: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600047: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600048: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600049: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600050: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600051: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600052: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600053: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600054: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600055: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600056: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600057: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600058: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600059: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600060: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600061: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600062: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600063: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600064: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600065: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600066: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600067: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600068: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600069: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600070: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600071: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600072: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600073: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600074: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600075: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600076: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600077: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600078: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600079: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600080: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600081: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600082: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600083: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600084: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600085: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600086: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600087: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600088: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600089: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600090: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600091: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600092: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600093: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600094: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600095: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600096: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600097: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600098: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600099: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            600100: {'State': 'Tamil Nadu', 'State_Avg_Salary': 48000, 'Final_Tier': 'Tier 1'},
            
            # West Bengal - Kolkata
            700001: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700002: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700003: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700004: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700005: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700006: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700007: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700008: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700009: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700010: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700011: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700012: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700013: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700014: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700015: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700016: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700017: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700018: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700019: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700020: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700021: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700022: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700023: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700024: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700025: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700026: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700027: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700028: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700029: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700030: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700031: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700032: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700033: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700034: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700035: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700036: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700037: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700038: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700039: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700040: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700041: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700042: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700043: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700044: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700045: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700046: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700047: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700048: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700049: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700050: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700051: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700052: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700053: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700054: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700055: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700056: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700057: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700058: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700059: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700060: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700061: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700062: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700063: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700064: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700065: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700066: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700067: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700068: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700069: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700070: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700071: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700072: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700073: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700074: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700075: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700076: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700077: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700078: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700079: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700080: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700081: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700082: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700083: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700084: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700085: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700086: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700087: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700088: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700089: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700090: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700091: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700092: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700093: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700094: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700095: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700096: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700097: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700098: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700099: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            700100: {'State': 'West Bengal', 'State_Avg_Salary': 42000, 'Final_Tier': 'Tier 2'},
            
            # Gujarat - Ahmedabad
            380001: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380002: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380003: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380004: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380005: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380006: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380007: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380008: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380009: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380010: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380011: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380012: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380013: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380014: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380015: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380016: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380017: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380018: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380019: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380020: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380021: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380022: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380023: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380024: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380025: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380026: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380027: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380028: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380029: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380030: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380031: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380032: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380033: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380034: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380035: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380036: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380037: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380038: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380039: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380040: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380041: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380042: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380043: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380044: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380045: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380046: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380047: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380048: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380049: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380050: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380051: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380052: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380053: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380054: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380055: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380056: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380057: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380058: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380059: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380060: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380061: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380062: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380063: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380064: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380065: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380066: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380067: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380068: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380069: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380070: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380071: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380072: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380073: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380074: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380075: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380076: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380077: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380078: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380079: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380080: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380081: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380082: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380083: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380084: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380085: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380086: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380087: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380088: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380089: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380090: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380091: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380092: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380093: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380094: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380095: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380096: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380097: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380098: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380099: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            380100: {'State': 'Gujarat', 'State_Avg_Salary': 46000, 'Final_Tier': 'Tier 2'},
            
            # Rajasthan - Jaipur
            302001: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302002: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302003: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302004: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302005: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302006: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302007: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302008: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302009: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302010: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302011: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302012: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302013: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302014: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302015: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302016: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302017: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302018: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302019: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302020: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302021: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302022: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302023: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302024: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302025: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302026: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302027: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302028: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302029: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302030: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302031: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302032: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302033: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302034: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302035: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302036: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302037: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302038: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302039: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302040: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302041: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302042: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302043: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302044: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302045: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302046: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302047: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302048: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302049: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302050: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302051: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302052: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302053: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302054: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302055: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302056: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302057: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302058: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302059: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302060: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302061: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302062: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302063: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302064: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302065: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302066: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302067: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302068: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302069: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302070: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302071: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302072: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302073: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302074: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302075: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302076: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302077: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302078: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302079: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302080: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302081: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302082: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302083: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302084: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302085: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302086: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302087: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302088: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302089: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302090: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302091: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302092: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302093: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302094: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302095: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302096: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302097: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302098: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302099: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            302100: {'State': 'Rajasthan', 'State_Avg_Salary': 38000, 'Final_Tier': 'Tier 2'},
            
            # Additional states with representative pincodes
            # Uttar Pradesh
            201001: {'State': 'Uttar Pradesh', 'State_Avg_Salary': 35000, 'Final_Tier': 'Tier 2'},
            201002: {'State': 'Uttar Pradesh', 'State_Avg_Salary': 35000, 'Final_Tier': 'Tier 2'},
            201003: {'State': 'Uttar Pradesh', 'State_Avg_Salary': 35000, 'Final_Tier': 'Tier 2'},
            201004: {'State': 'Uttar Pradesh', 'State_Avg_Salary': 35000, 'Final_Tier': 'Tier 2'},
            201005: {'State': 'Uttar Pradesh', 'State_Avg_Salary': 35000, 'Final_Tier': 'Tier 2'},
            
            # Punjab
            141001: {'State': 'Punjab', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            141002: {'State': 'Punjab', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            141003: {'State': 'Punjab', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            141004: {'State': 'Punjab', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            141005: {'State': 'Punjab', 'State_Avg_Salary': 40000, 'Final_Tier': 'Tier 2'},
            
            # Haryana
            122001: {'State': 'Haryana', 'State_Avg_Salary': 43000, 'Final_Tier': 'Tier 2'},
            122002: {'State': 'Haryana', 'State_Avg_Salary': 43000, 'Final_Tier': 'Tier 2'},
            122003: {'State': 'Haryana', 'State_Avg_Salary': 43000, 'Final_Tier': 'Tier 2'},
            122004: {'State': 'Haryana', 'State_Avg_Salary': 43000, 'Final_Tier': 'Tier 2'},
            122005: {'State': 'Haryana', 'State_Avg_Salary': 43000, 'Final_Tier': 'Tier 2'},
            
            # Madhya Pradesh
            462001: {'State': 'Madhya Pradesh', 'State_Avg_Salary': 36000, 'Final_Tier': 'Tier 2'},
            462002: {'State': 'Madhya Pradesh', 'State_Avg_Salary': 36000, 'Final_Tier': 'Tier 2'},
            462003: {'State': 'Madhya Pradesh', 'State_Avg_Salary': 36000, 'Final_Tier': 'Tier 2'},
            462004: {'State': 'Madhya Pradesh', 'State_Avg_Salary': 36000, 'Final_Tier': 'Tier 2'},
            462005: {'State': 'Madhya Pradesh', 'State_Avg_Salary': 36000, 'Final_Tier': 'Tier 2'},
            
            # Odisha
            751001: {'State': 'Odisha', 'State_Avg_Salary': 34000, 'Final_Tier': 'Tier 2'},
            751002: {'State': 'Odisha', 'State_Avg_Salary': 34000, 'Final_Tier': 'Tier 2'},
            751003: {'State': 'Odisha', 'State_Avg_Salary': 34000, 'Final_Tier': 'Tier 2'},
            751004: {'State': 'Odisha', 'State_Avg_Salary': 34000, 'Final_Tier': 'Tier 2'},
            751005: {'State': 'Odisha', 'State_Avg_Salary': 34000, 'Final_Tier': 'Tier 2'},
            
            # Kerala
            682001: {'State': 'Kerala', 'State_Avg_Salary': 44000, 'Final_Tier': 'Tier 2'},
            682002: {'State': 'Kerala', 'State_Avg_Salary': 44000, 'Final_Tier': 'Tier 2'},
            682003: {'State': 'Kerala', 'State_Avg_Salary': 44000, 'Final_Tier': 'Tier 2'},
            682004: {'State': 'Kerala', 'State_Avg_Salary': 44000, 'Final_Tier': 'Tier 2'},
            682005: {'State': 'Kerala', 'State_Avg_Salary': 44000, 'Final_Tier': 'Tier 2'},
            
            # Assam
            781001: {'State': 'Assam', 'State_Avg_Salary': 32000, 'Final_Tier': 'Tier 3'},
            781002: {'State': 'Assam', 'State_Avg_Salary': 32000, 'Final_Tier': 'Tier 3'},
            781003: {'State': 'Assam', 'State_Avg_Salary': 32000, 'Final_Tier': 'Tier 3'},
            781004: {'State': 'Assam', 'State_Avg_Salary': 32000, 'Final_Tier': 'Tier 3'},
            781005: {'State': 'Assam', 'State_Avg_Salary': 32000, 'Final_Tier': 'Tier 3'},
            
            # Bihar
            800001: {'State': 'Bihar', 'State_Avg_Salary': 28000, 'Final_Tier': 'Tier 3'},
            800002: {'State': 'Bihar', 'State_Avg_Salary': 28000, 'Final_Tier': 'Tier 3'},
            800003: {'State': 'Bihar', 'State_Avg_Salary': 28000, 'Final_Tier': 'Tier 3'},
            800004: {'State': 'Bihar', 'State_Avg_Salary': 28000, 'Final_Tier': 'Tier 3'},
            800005: {'State': 'Bihar', 'State_Avg_Salary': 28000, 'Final_Tier': 'Tier 3'},
            
            # Jharkhand
            834001: {'State': 'Jharkhand', 'State_Avg_Salary': 30000, 'Final_Tier': 'Tier 3'},
            834002: {'State': 'Jharkhand', 'State_Avg_Salary': 30000, 'Final_Tier': 'Tier 3'},
            834003: {'State': 'Jharkhand', 'State_Avg_Salary': 30000, 'Final_Tier': 'Tier 3'},
            834004: {'State': 'Jharkhand', 'State_Avg_Salary': 30000, 'Final_Tier': 'Tier 3'},
            834005: {'State': 'Jharkhand', 'State_Avg_Salary': 30000, 'Final_Tier': 'Tier 3'},
            
            # Chhattisgarh
            492001: {'State': 'Chhattisgarh', 'State_Avg_Salary': 31000, 'Final_Tier': 'Tier 3'},
            492002: {'State': 'Chhattisgarh', 'State_Avg_Salary': 31000, 'Final_Tier': 'Tier 3'},
            492003: {'State': 'Chhattisgarh', 'State_Avg_Salary': 31000, 'Final_Tier': 'Tier 3'},
            492004: {'State': 'Chhattisgarh', 'State_Avg_Salary': 31000, 'Final_Tier': 'Tier 3'},
            492005: {'State': 'Chhattisgarh', 'State_Avg_Salary': 31000, 'Final_Tier': 'Tier 3'},
        }
        
        self.MAKE_CODE_MAP = {
            'APACHE': [
                {'Model_Description': 'Apache RTR 160', 'Product_Code': 'AP160', 'Avg_Model_Price': 120000},
                {'Model_Description': 'Apache RTR 180', 'Product_Code': 'AP180', 'Avg_Model_Price': 135000},
                {'Model_Description': 'Apache RTR 200 4V', 'Product_Code': 'AP200', 'Avg_Model_Price': 150000},
                {'Model_Description': 'Apache RTR 310', 'Product_Code': 'AP310', 'Avg_Model_Price': 280000},
                {'Model_Description': 'Apache RR 310', 'Product_Code': 'APRR310', 'Avg_Model_Price': 290000},
                {'Model_Description': 'Apache RTR 160 2V', 'Product_Code': 'AP160_2V', 'Avg_Model_Price': 115000},
                {'Model_Description': 'Apache RTR 160 4V', 'Product_Code': 'AP160_4V', 'Avg_Model_Price': 125000},
                {'Model_Description': 'Apache RTR 200', 'Product_Code': 'AP200_STD', 'Avg_Model_Price': 145000},
            ],
            'JUPITER': [
                {'Model_Description': 'Jupiter Classic', 'Product_Code': 'JUP125', 'Avg_Model_Price': 80000},
                {'Model_Description': 'Jupiter Grande', 'Product_Code': 'JUPG', 'Avg_Model_Price': 90000},
                {'Model_Description': 'Jupiter ZX', 'Product_Code': 'JUPZX', 'Avg_Model_Price': 85000},
                {'Model_Description': 'Jupiter 125', 'Product_Code': 'JUP125_NEW', 'Avg_Model_Price': 82000},
                {'Model_Description': 'Jupiter Millionaire', 'Product_Code': 'JUPMIL', 'Avg_Model_Price': 88000},
                {'Model_Description': 'Jupiter Classic 110', 'Product_Code': 'JUP110', 'Avg_Model_Price': 75000},
                {'Model_Description': 'Jupiter Grande Special Edition', 'Product_Code': 'JUPGSE', 'Avg_Model_Price': 95000},
            ],
            'MOPEDS': [
                {'Model_Description': 'XL Super', 'Product_Code': 'XLS', 'Avg_Model_Price': 60000},
                {'Model_Description': 'Sport', 'Product_Code': 'SPT', 'Avg_Model_Price': 65000},
                {'Model_Description': 'XL 100', 'Product_Code': 'XL100', 'Avg_Model_Price': 58000},
                {'Model_Description': 'Heavy Duty', 'Product_Code': 'HD', 'Avg_Model_Price': 70000},
                {'Model_Description': 'XL Super Heavy Duty', 'Product_Code': 'XLSHD', 'Avg_Model_Price': 72000},
                {'Model_Description': 'Sport Special', 'Product_Code': 'SPTSP', 'Avg_Model_Price': 68000},
            ],
            'NTORQ': [
                {'Model_Description': 'Ntorq 125', 'Product_Code': 'NT125', 'Avg_Model_Price': 95000},
                {'Model_Description': 'Ntorq 125 Race Edition', 'Product_Code': 'NT125RE', 'Avg_Model_Price': 105000},
                {'Model_Description': 'Ntorq 125 SuperSquad Edition', 'Product_Code': 'NT125SS', 'Avg_Model_Price': 100000},
                {'Model_Description': 'Ntorq 125 Drum', 'Product_Code': 'NT125D', 'Avg_Model_Price': 92000},
                {'Model_Description': 'Ntorq 125 Disc', 'Product_Code': 'NT125DC', 'Avg_Model_Price': 98000},
            ],
            'RADEON': [
                {'Model_Description': 'Radeon 110', 'Product_Code': 'RAD110', 'Avg_Model_Price': 70000},
                {'Model_Description': 'Radeon 110 Drum', 'Product_Code': 'RAD110D', 'Avg_Model_Price': 68000},
                {'Model_Description': 'Radeon 110 Disc', 'Product_Code': 'RAD110DC', 'Avg_Model_Price': 72000},
                {'Model_Description': 'Radeon 110 Special Edition', 'Product_Code': 'RAD110SE', 'Avg_Model_Price': 75000},
            ],
            'STAR_CITY': [
                {'Model_Description': 'Star City Plus', 'Product_Code': 'SCP', 'Avg_Model_Price': 78000},
                {'Model_Description': 'Star City Plus Dual Tone', 'Product_Code': 'SCPDT', 'Avg_Model_Price': 80000},
                {'Model_Description': 'Star City Plus Special Edition', 'Product_Code': 'SCPSE', 'Avg_Model_Price': 82000},
            ],
            'VICTOR': [
                {'Model_Description': 'Victor 110', 'Product_Code': 'VIC110', 'Avg_Model_Price': 65000},
                {'Model_Description': 'Victor GLX', 'Product_Code': 'VICGLX', 'Avg_Model_Price': 68000},
                {'Model_Description': 'Victor Premium', 'Product_Code': 'VICPREM', 'Avg_Model_Price': 70000},
            ],
            'ZEST': [
                {'Model_Description': 'Zest 110', 'Product_Code': 'ZST110', 'Avg_Model_Price': 63000},
                {'Model_Description': 'Zest 110 Drum', 'Product_Code': 'ZST110D', 'Avg_Model_Price': 61000},
                {'Model_Description': 'Zest 110 Disc', 'Product_Code': 'ZST110DC', 'Avg_Model_Price': 65000},
            ],
            'SCOOTY': [
                {'Model_Description': 'Scooty Pep Plus', 'Product_Code': 'SPP', 'Avg_Model_Price': 55000},
                {'Model_Description': 'Scooty Zest', 'Product_Code': 'SZ', 'Avg_Model_Price': 58000},
                {'Model_Description': 'Scooty Streak', 'Product_Code': 'SS', 'Avg_Model_Price': 60000},
            ],
            'IQUBE': [
                {'Model_Description': 'iQube Electric', 'Product_Code': 'IQE', 'Avg_Model_Price': 150000},
                {'Model_Description': 'iQube Electric S', 'Product_Code': 'IQES', 'Avg_Model_Price': 165000},
                {'Model_Description': 'iQube Electric ST', 'Product_Code': 'IQEST', 'Avg_Model_Price': 180000},
            ],
            'CREON': [
                {'Model_Description': 'Creon Electric', 'Product_Code': 'CRE', 'Avg_Model_Price': 130000},
                {'Model_Description': 'Creon Electric Plus', 'Product_Code': 'CREP', 'Avg_Model_Price': 145000},
            ],
            'RONIN': [
                {'Model_Description': 'Ronin 225', 'Product_Code': 'RON225', 'Avg_Model_Price': 200000},
                {'Model_Description': 'Ronin 225 Special Edition', 'Product_Code': 'RON225SE', 'Avg_Model_Price': 220000},
            ],
            'DRAKEN': [
                {'Model_Description': 'Draken X21', 'Product_Code': 'DRX21', 'Avg_Model_Price': 250000},
                {'Model_Description': 'Draken X21 Racing Edition', 'Product_Code': 'DRX21RE', 'Avg_Model_Price': 275000},
            ],
        }

        self.BINS_AGE = [17, 25, 35, 45, 65, 70]
        self.LABELS_AGE = ['18-25', '26-35', '36-45', '46-65', '66-69']
        
        # Calculate LTV bins from original code
        self.BINS_LTV = [0, 33.33, 66.66, 100]
        self.LABELS_LTV = ['LTV_Low', 'LTV_Medium', 'LTV_High']
        
        # Calculate salary bins from original code
        self.BINS_SALARY = [0, 25000, 50000, 75000, 100000]
        self.LABELS_SALARY = ['Low', 'Medium', 'High', 'Very_High']
        
        # Calculate loan amount bins from original code
        self.BINS_LOAN = [0, 75000, 125000, 200000, 500000]
        self.LABELS_LOAN = ['Low', 'Medium', 'High', 'Very_High']

    def generate_synthetic_data(self, n_samples=10000):
        """Generate synthetic loan data for training based on original Python code logic"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Generate realistic loan application data
            age = np.random.randint(18, 61)
            
            # Generate employment type
            employment_type = np.random.choice(['AGR', 'SAL', 'NREGI', 'SEP', 'STU', 'PEN', 'BUS', 'OTHERS', 'GOVT', 'N_A', 'Nonearnmem'], 
                                            p=[0.1, 0.4, 0.1, 0.05, 0.1, 0.05, 0.1, 0.05, 0.03, 0.01, 0.01])
            
            # Generate net salary based on employment type
            if employment_type in ['STU', 'N_A', 'Nonearnmem']:
                net_salary = np.random.choice([0, np.random.uniform(15000, 50000)], p=[0.7, 0.3])
            elif employment_type == 'PEN':
                net_salary = np.random.uniform(10000, 40000)
            elif employment_type == 'SAL':
                net_salary = np.random.uniform(20000, 100000)
            elif employment_type == 'GOVT':
                net_salary = np.random.uniform(25000, 80000)
            else:
                net_salary = np.random.uniform(15000, 75000)
            
            # Generate gender
            gender = np.random.choice(['Male', 'Female'], p=[0.6, 0.4])
            
            # Generate qualifications
            qualifications = np.random.choice(['SSC', 'UG', 'GRAD', 'OTHERS', 'POSTGRAD', 'PHD', 'DIP', 'DIPLOMA', 'N_A'], 
                                            p=[0.2, 0.25, 0.2, 0.1, 0.1, 0.02, 0.08, 0.03, 0.02])
            
            # Generate past loans
            past_loans = np.random.choice(['PAST_LOANS_ACTIVE', 'NO_PAST_LOANS'], p=[0.3, 0.7])
            
            # Generate pincode
            pincode = np.random.choice(list(self.PINCODE_MAP.keys()))
            
            # Generate make code
            make_code = np.random.choice(list(self.MAKE_CODE_MAP.keys()))
            
            # Get model info for the make code
            model_options = self.MAKE_CODE_MAP[make_code]
            selected_model = np.random.choice(model_options)
            
            # Generate loan amount based on model price
            avg_model_price = selected_model['Avg_Model_Price']
            loan_amount = np.random.uniform(0.6 * avg_model_price, 0.9 * avg_model_price)
            
            # Calculate approval based on realistic criteria from original code
            ltv_ratio = (loan_amount / avg_model_price) * 100
            income_to_loan_ratio = loan_amount / net_salary if net_salary > 0 else float('inf')
            
            # Approval logic based on original Python code
            approval_score = 0
            
            # Age factor
            if 25 <= age <= 50:
                approval_score += 0.3
            elif 18 <= age < 25 or 50 < age <= 60:
                approval_score += 0.1
            
            # Income factor
            if net_salary > 0 and income_to_loan_ratio < 2:
                approval_score += 0.4
            elif net_salary > 0 and income_to_loan_ratio < 3:
                approval_score += 0.2
            elif net_salary > 0 and income_to_loan_ratio < 5:
                approval_score += 0.1
            
            # Employment factor
            if employment_type in ['SAL', 'GOVT']:
                approval_score += 0.2
            elif employment_type in ['BUS', 'SEP']:
                approval_score += 0.1
            
            # LTV factor
            if ltv_ratio < 70:
                approval_score += 0.1
            elif ltv_ratio > 85:
                approval_score -= 0.1
            
            # Past loans factor
            if past_loans == 'NO_PAST_LOANS':
                approval_score += 0.1
            else:
                approval_score -= 0.1
            
            # Add some randomness
            approval_score += np.random.normal(0, 0.1)
            
            # Final approval decision
            approved = 1 if approval_score > 0.5 else 0
            
            data.append({
                'Age': age,
                'Gender': gender,
                'Pincode': pincode,
                'Qualifications': qualifications,
                'Employment_Type': employment_type,
                'Net_salary': net_salary,
                'Make_Code': make_code,
                'Loan_Amount': loan_amount,
                'PAST_LOANS_ACTIVE': past_loans,
                'Model_Description': selected_model['Model_Description'],
                'Product_Code': selected_model['Product_Code'],
                'Avg_Model_Price': avg_model_price,
                'Approved': approved
            })
        
        return pd.DataFrame(data)

    def feature_engineering(self, df):
        """Apply feature engineering as per original Python code"""
        df = df.copy()
        
        # Map pincode to state info
        df['State'] = df['Pincode'].map(lambda x: self.PINCODE_MAP.get(x, {}).get('State', 'Unknown'))
        df['State_Avg_Salary'] = df['Pincode'].map(lambda x: self.PINCODE_MAP.get(x, {}).get('State_Avg_Salary', 0))
        df['Final_Tier'] = df['Pincode'].map(lambda x: self.PINCODE_MAP.get(x, {}).get('Final_Tier', 'Unknown'))
        
        # Create Income_Presence feature
        df['Income_Presence'] = 'Income'  # default
        mask_no_income = (df['Employment_Type'].isin(['STU', 'NON_APP', 'Nonearnmem'])) & (df['Net_salary'] == 0)
        mask_guarantor = (df['Employment_Type'].isin(['STU', 'NON_APP', 'Nonearnmem'])) & (df['Net_salary'] > 0)
        df.loc[mask_no_income, 'Income_Presence'] = 'No Income'
        df.loc[mask_guarantor, 'Income_Presence'] = 'Guarantor'
        
        # Binned Numerical Features
        df['Age_Group'] = pd.cut(df['Age'], bins=self.BINS_AGE, labels=self.LABELS_AGE, right=True, include_lowest=True)
        
        # LTV calculation and binning
        df['LTV'] = (df['Loan_Amount'] / df['Avg_Model_Price']) * 100
        df['LTV_Band'] = pd.cut(df['LTV'], bins=self.BINS_LTV, labels=self.LABELS_LTV, include_lowest=True)
        
        df['Income_Tier'] = pd.cut(df['Net_salary'], bins=self.BINS_SALARY, labels=self.LABELS_SALARY, include_lowest=True)
        df['Loan_Amount_Band'] = pd.cut(df['Loan_Amount'], bins=self.BINS_LOAN, labels=self.LABELS_LOAN, include_lowest=True)
        
        # Interaction Features
        df['Employment_Gender'] = df['Employment_Type'].astype(str) + '_' + df['Gender'].astype(str)
        df['PastLoans_Employment_Interaction'] = df['PAST_LOANS_ACTIVE'].astype(str) + '_' + df['Employment_Type'].astype(str)
        
        # String manipulation for zones
        df['Pincode_Str'] = df['Pincode'].astype(str).str.zfill(6)
        df['Pincode_Prefix_3'] = df['Pincode_Str'].str[:3]
        df['State_Pincode_Zone'] = df['State'].astype(str) + '_' + df['Pincode_Prefix_3'].astype(str)
        
        # Ratio features
        df['Income_to_Loan_Ratio'] = df.apply(
            lambda row: row['Loan_Amount'] / row['Net_salary'] if row['Net_salary'] > 0 else 0, axis=1
        )
        df['Age_to_Loan_Amount_Ratio'] = df.apply(
            lambda row: row['Loan_Amount'] / row['Age'] if row['Age'] > 0 else 0, axis=1
        )
        df['Salary_vs_State_Avg_Ratio'] = df.apply(
            lambda row: row['Net_salary'] / row['State_Avg_Salary'] if row['State_Avg_Salary'] > 0 else 0, axis=1
        )
        
        return df

    def prepare_features(self, df):
        """Prepare features for model training"""
        # Select features for training
        categorical_features = ['Gender', 'Qualifications', 'Employment_Type', 'PAST_LOANS_ACTIVE',
                              'State', 'Final_Tier', 'Income_Presence', 'Age_Group', 'LTV_Band',
                              'Income_Tier', 'Loan_Amount_Band', 'Employment_Gender',
                              'PastLoans_Employment_Interaction', 'State_Pincode_Zone', 'Make_Code']
        
        numerical_features = ['Age', 'Net_salary', 'Loan_Amount', 'Avg_Model_Price', 'LTV',
                            'Income_to_Loan_Ratio', 'Age_to_Loan_Amount_Ratio', 'Salary_vs_State_Avg_Ratio',
                            'State_Avg_Salary']
        
        # Encode categorical features
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                df[feature + '_encoded'] = self.label_encoders[feature].fit_transform(df[feature].astype(str))
            else:
                # Handle unseen categories
                df[feature + '_encoded'] = df[feature].apply(
                    lambda x: self.label_encoders[feature].transform([str(x)])[0] 
                    if str(x) in self.label_encoders[feature].classes_ 
                    else -1
                )
        
        # Scale numerical features
        scaler = StandardScaler()
        df[numerical_features] = scaler.fit_transform(df[numerical_features])
        
        # Combine all features
        feature_columns = numerical_features + [f + '_encoded' for f in categorical_features]
        self.feature_names = feature_columns
        
        return df[feature_columns]

    def train_model(self):
        """Train the loan approval model"""
        print("Generating synthetic training data...")
        df = self.generate_synthetic_data(10000)
        
        print("Applying feature engineering...")
        df_engineered = self.feature_engineering(df)
        
        print("Preparing features...")
        X = self.prepare_features(df_engineered)
        y = df_engineered['Approved']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Apply SMOTE for class imbalance
        print("Applying SMOTE for class balance...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        # Train LightGBM model
        print("Training LightGBM model...")
        self.model = lgb.LGBMClassifier(
            objective='binary',
            metric='binary_logloss',
            boosting_type='gbdt',
            num_leaves=31,
            learning_rate=0.05,
            feature_fraction=0.9,
            bagging_fraction=0.8,
            bagging_freq=5,
            verbose=0,
            random_state=42,
            n_estimators=100
        )
        
        self.model.fit(X_train_balanced, y_train_balanced)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        print(f"Model Training Complete!")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"AUC Score: {auc_score:.4f}")
        print(f"Classification Report:")
        print(classification_report(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_balanced, y_train_balanced, 
                                   cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42))
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.is_trained = True
        
        # Save model and encoders
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'auc_score': auc_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }

    def predict_single(self, user_data):
        """Make prediction for a single user input"""
        if not self.is_trained:
            raise ValueError("Model not trained yet. Please train the model first.")
        
        # Create DataFrame from user input
        df = pd.DataFrame([user_data])
        
        # Apply feature engineering
        df_engineered = self.feature_engineering(df)
        
        # Prepare features
        X = self.prepare_features(df_engineered)
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        prediction_proba = self.model.predict_proba(X)[0]
        
        return {
            'approved': bool(prediction),
            'approval_probability': float(prediction_proba[1]),
            'rejection_probability': float(prediction_proba[0]),
            'confidence': float(max(prediction_proba))
        }

    def save_model(self):
        """Save trained model and encoders"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'pincode_map': self.PINCODE_MAP,
            'make_code_map': self.MAKE_CODE_MAP,
            'is_trained': self.is_trained,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('loan_model.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print("Model saved successfully as 'loan_model.pkl'")

    def load_model(self):
        """Load trained model and encoders"""
        try:
            with open('loan_model.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.PINCODE_MAP = model_data['pincode_map']
            self.MAKE_CODE_MAP = model_data['make_code_map']
            self.is_trained = model_data['is_trained']
            
            print("Model loaded successfully!")
            return True
        except FileNotFoundError:
            print("No saved model found. Please train the model first.")
            return False

def main():
    """Main function to train and test the model"""
    print("=== TVS Credit Epic Analytics - Loan Approval Model ===")
    
    # Initialize model
    loan_model = LoanApprovalModel()
    
    # Try to load existing model
    if not loan_model.load_model():
        # Train new model if no saved model exists
        print("\nTraining new model...")
        metrics = loan_model.train_model()
        print(f"\nTraining completed with metrics: {metrics}")
    
    # Test with sample data
    print("\n=== Testing Model with Sample Data ===")
    
    test_cases = [
        {
            'Age': 28,
            'Gender': 'Male',
            'Pincode': 560001,
            'Qualifications': 'GRAD',
            'Employment_Type': 'SAL',
            'Net_salary': 60000,
            'Make_Code': 'APACHE',
            'Loan_Amount': 100000,
            'PAST_LOANS_ACTIVE': 'NO_PAST_LOANS'
        },
        {
            'Age': 35,
            'Gender': 'Female',
            'Pincode': 400001,
            'Qualifications': 'POSTGRAD',
            'Employment_Type': 'BUS',
            'Net_salary': 80000,
            'Make_Code': 'JUPITER',
            'Loan_Amount': 70000,
            'PAST_LOANS_ACTIVE': 'PAST_LOANS_ACTIVE'
        },
        {
            'Age': 42,
            'Gender': 'Male',
            'Pincode': 700001,
            'Qualifications': 'UG',
            'Employment_Type': 'SAL',
            'Net_salary': 50000,
            'Make_Code': 'NTORQ',
            'Loan_Amount': 90000,
            'PAST_LOANS_ACTIVE': 'NO_PAST_LOANS'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case}")
        result = loan_model.predict_single(test_case)
        print(f"Prediction: {result}")
        print("-" * 50)

if __name__ == "__main__":
    main()
