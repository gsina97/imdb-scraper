import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import math



def main():
    df = pd.read_csv('imdbhorrordata5kratingsv2.csv')
    DateList = df['Date'].tolist()
    ShavedList = []
    # print(DateList)
    # print("")
    for i in range(len(DateList)):
        if str(DateList[i]) != 'nan':
        # print(type(DateList[i]))
            if (int(DateList[i][2:4]) >= 9) and (int(DateList[i][2:4]) <= 19):
                # print((DateList[i][2:4]))
                # print(DateList[i])
                # print(i)
                ShavedList.append(i)
    df2 = pd.DataFrame()
    for i in range(len(ShavedList)):
        new_row = df.iloc[ShavedList[i], :]
        # print(df.iloc[ShavedList[i], :])
        df2 = df2.append(new_row, ignore_index=True)
    print(df2)
    # df2.to_csv('imdbhorrordata5kratingsv3.csv')

    NetList = df2['Net'].tolist()
    NewNetList = []
    for i in range(len(NetList)):
        if str(NetList[i]) != 'nan':
            NewNetList.append(i)
    df3 = pd.DataFrame()
    for i in range(len(NewNetList)):
        new_row = df2.iloc[NewNetList[i], :]

        df3 = df3.append(new_row, ignore_index=True)

    print(df3)
    df3.to_csv('imdbhorrordata5kratingsv3_allnet.csv')

    
if __name__ == "__main__":
    main()