from pymongo import MongoClient
import pandas as pd


data=pd.read_csv("placement-data.csv")
for col in data.columns:
    print(col)