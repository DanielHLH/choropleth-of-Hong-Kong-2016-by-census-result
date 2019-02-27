import pandas as pd
import numpy as np

class District(object):
    def __init__(self,data):
        self.name = str(data).split(".")[0][5:]
        
        self.age = pd.read_excel(data,sheet_name = "D2",
                                 header=None,names=['Age','Male','Female'],
                                 usecols=[0,1,2],skiprows=np.linspace(0,4,5),nrows=18)
        
        self.median_age = self.parse_median_age(data)
        
        self.ethnicity = self.parse_ethnicity(data)
        
        self.marital_status = pd.read_excel(data,sheet_name="D5",
                               header=None,names=["Marital_status","Male","Female"],
                               usecols=[0,1,2],skiprows=np.linspace(0,4,5),nrows=5)
        
        self.usual_spoken_language = pd.read_excel(data,sheet_name='D6',
                               header=None,names=["Usual Spoken Language","Male","Female"],
                               usecols=[0,2,3],skiprows=np.linspace(0,4,5),nrows=5)
        
        self.language_literacy = self.parse_literacy(data)
        
    def parse_ethnicity(self,data):
        ethnicity = pd.read_excel(data,sheet_name = "D4",
                                header=None,names=["Ethnicity","Male","Female"],
                                usecols=[0,2,3],skiprows=np.linspace(0,4,5),nrows=11)
        ethnicity.loc[10,"Ethnicity"] = ethnicity.loc[10,"Ethnicity"].split("(")[0]
        ethnicity[["Male","Female"]] = ethnicity[["Male","Female"]].replace("[^0-9]",0,regex=True)
        ethnicity["Total"] = ethnicity["Male"] + ethnicity["Female"]
        return ethnicity
        
    def parse_median_age(self,data):
            median_df = pd.read_excel(data,sheet_name="D3",
                        header=None,names=["Male","Female","Total"],
                        usecols=[2,3,4],skiprows=2,nrows=1)
        
            return pd.Series(median_df.iloc[0],index=median_df.columns,name="Median")
        
    def parse_literacy(self,data):
            language_literacy = pd.read_excel(data,sheet_name=[7,9,8,10],header=None,
                        usecols=[1,2],skiprows=np.linspace(0,4,5),nrows=2)
            language_literacy = pd.concat([language_literacy[i].T for i in [7,9,8,10]])
            language_literacy.columns = ["Y","N"]
            language_literacy.index = pd.MultiIndex.from_product([["Chi","Eng"],
                                             ["reading","writing"],["Male","Female"]],                                                    names=['language','type',"sex"])
            return language_literacy
    
    def population(self):
        # it calculates the population of the district
        male = self.age["Male"].sum()
        female = self.age["Female"].sum()
        total = male + female
        return pd.Series([male,female,total],index=["Male","Female","Total"])
        
    def elderly_ratio(self):
        # it calculates the percentage of elderly (age >= 65) in the district
        index = [i for i in range(13,18)]
        population = self.population()
        male = self.age["Male"].iloc[index].sum()
        female = self.age["Female"].iloc[index].sum()
        total = male + female
        male_ratio = male / population["Male"]
        female_ratio = female / population["Female"]
        total_ratio = total / population["Total"]
        return pd.Series([male_ratio,female_ratio,total_ratio],
                         index=["Male","Female","Total"])
    
    def ethnicity_ratio(self):
        population = self.population()
        ethnicity = self.ethnicity
        sex = ["Male","Female","Total"]
        index = pd.MultiIndex.from_product([ethnicity["Ethnicity"],sex],names=["Ethnicity","Sex"])
        ethnicity_ratio = pd.Series(index=index)
        for i, e in enumerate(ethnicity["Ethnicity"]):
            for s in sex:
                try:
                    ethnicity_ratio.loc[e,s] = ethnicity.loc[i,s]*(1/population[s])
                except TypeError:
                    ethnicity_ratio.loc[e,s] = 0           
        return ethnicity_ratio
    
    def summary(self):
        # Create columns
        age_index = list((self.median_age.name.lower())+"_"+self.median_age.index)
        elderly_ratio_index = list("elderly_" + self.elderly_ratio().index + "_r")
        ethnicity_ratio_index = list("{0}_{1}_r".format(index[0],index[1]) for index in self.ethnicity_ratio().index)
        index = age_index + elderly_ratio_index + ethnicity_ratio_index
        # Create a DataFrame using these columns
        summary = pd.Series(index = index, name = self.name)
        median = self.median_age
        elderly_ratio = self.elderly_ratio()
        ethnicity_ratio = self.ethnicity_ratio()
        summary.loc[:] = pd.concat([median,elderly_ratio,ethnicity_ratio]).values
        return summary
