import scipy as sp
# 
#Developed by M. Oshagh. Contact: mahmood.oshagh@gmail.com
#
from pathlib import Path
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from timezonefinder import TimezoneFinder

class DataPreparation:
    def __init__(self):
        self.path = input("Please enter path to the directroy of data")
        self.headernum = input("Please enter the row number which should be used as the header")
       

    def LoadCombineDatasets(self):
        files=list(Path(self.path).glob('*.xlsx')) ### path's of data
        df = pd.DataFrame()
        ####Load several xlsl files into a single pandas DataFrame
        print("I am combining dataset in single dataframe, will print head of it when I am done!")
        for file in files:
            df = df.append(pd.read_excel(file, header=int(self.headernum)), ignore_index=True) 
        print(df.head(10))
        return df    

    def Statsitics(self,df):
        print(df.describe(include="all"))

    def BetterHeaderName(self,df):
        df = df.rename(columns={'Unnamed: 0': str(input("Input name of first column")), 'Potencia(MW)': str(input("Input name of first column")),'Radiación (kW/m2)': str(input("Input name of first column")), })

    def Resampling(self,df):
        print("I am resampling every 10 min, will print head of it when I am done!")

        df = df.rename(columns={'Unnamed: 0': 'Time', 'Potencia(MW)': "Potencia",'Radiación (kW/m2)': "Radiacion", })
        df.Time=pd.to_datetime(df.Time)
        df.set_index("Time", inplace=True)
        ### remove outlier
        q_low = df["Potencia"].quantile(0.01)
        q_hi  = df["Potencia"].quantile(0.99)
        df= df[(df["Potencia"] < q_hi) & (df["Potencia"] > q_low)]

        ### remove negative values
        indexNames = df[df['Potencia'] < 0 ].index

        df.drop(indexNames , inplace=True)

        ###resampleing every 10 min
        df_resampled=df.resample('10T').mean()
        df_resampled=df_resampled.dropna()
        print(df_resampled.head(10))
        return df_resampled

    def Convert_UTC(self,df_resampled):
        self.lat=input("Please enter Latitude of power plant in degree")
        self.long=input("Please enter Longitude of power plant in degree")
        tf = TimezoneFinder()
        latitude, longitude =  float(self.lat), float(self.long)    ###10.7015, -85.1933
        #tf.timezone_at(lng=longitude, lat=latitude)    
        df_resampled=df_resampled.tz_localize(tz=tf.timezone_at(lat=latitude, lng=longitude))
        df_resampled_UTC=df_resampled.tz_convert("UTC")
        return df_resampled_UTC

    def DailyMean(self, df_resampled_UTC):
        means=df_resampled_UTC.groupby(df_resampled_UTC.index.floor('D')).mean() ###Daily mean
        means=means.round(3) ### up to 3 deciaml is saved
        quest=input("Do you want the final processed data be saved? y/n: ")
        if quest=="y":
            quest2=input("How do you want it to be saved? pickle or csv: ")
            if quest2=="pickle":
                means.to_pickle("data/processed/means.pkl") 
            elif quest2=="csv":
                means.to_csv('data/processed/means.csv') 
        if quest=="n":
            print("Okay, I respect your choice, have a nice day!")   
