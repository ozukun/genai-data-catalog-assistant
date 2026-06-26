
from functools import wraps
import pandas as pd


list1=[['x',10],['x2',110]]


df1=pd.DataFrame(columns=['col1','col2'],data=list1)
df1.index=df1.col1



if __name__=="__main__":
    print(df1.loc["x"])