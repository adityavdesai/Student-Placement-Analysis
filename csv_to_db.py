from pymongo import MongoClient
import pandas as pd
#import names
import random


data=pd.read_csv("placement-data.csv")
df=data[data.duplicated(subset=["FirstName","LastName"])]
#print(df)
email=[]


def getUniqueEmail(i):
    first=data.iloc[i,1]
    last=data.iloc[i,2]
    id=data.iloc[i,0]
    email.append(str(first.lower()+last.lower()+"."+str(id)+"@email.com"))
    #print(len(email))

for i in range(0,20000):
    getUniqueEmail(i)
    if(i == 1):
        print(email)
data.insert(3,'email',email)
print(data.head())
data.to_csv('placement-data.csv',index=False)

'''gender=['Male','Female']

fname=[]
lname=[]
ngender=[]

def namesGender():
    g = random.choice(gender)
    if g=='Male':
        fname.append(names.get_first_name(gender='male'))
    if g=='Female':
        fname.append(names.get_first_name(gender='female'))
    lname.append(names.get_last_name())
    ngender.append(g)


for i in range(0,20000):
    namesGender()
   
data.insert(0,'FirstName',fname)
data.insert(1,'LastName',lname)
data.insert(2,'Gender',ngender)
print(data.head())
data.to_csv('placement-data.csv')'''

