import numpy as np
import pandas as pd
import datetime

def interpolate(startDate, endDate, date,  startVal, endVal):
    days = (endDate-startDate).days
    iter = (endVal-startVal)/days
    t= np.arange(start=startVal, stop=endVal, step=iter)
    d = (date-startDate).days
    return t[d]

def updateDataFrame(df, x, y, date, colName, value):
    
    if value == "?" or value == "L" or value == "N":
        print(f"Skipped (bad Value): {x}, {y}, {date}, {colName} value: {value}")
        return
    if len(df[df.X==x][df.Y == y][df.date == date])>= 1: 
        if df.at[df[df.X==x][df.Y == y][df.date == date].index[0], colName ] == -1.0:
            df.at[df[df.X==x][df.Y == y][df.date == date].index[0], colName ] = float(value)
        else:
            df.at[df[df.X==x][df.Y == y][df.date == date].index[0], colName ] += float(value)
    else: 
        print(f"Skipped (out of date range): {x}, {y}, {date}, {colName} value: {value}")

def interpolateDataFrameForLocation(df, x, y, colName, values):
    sd = datetime.date(1986, 4, 27)
    ed = datetime.date(1986, 6, 1)
    duration = (ed-sd).days
    if len(values) != duration:
        raise Exception
    for i in range(duration):
        d = sd + datetime.timedelta(days=i)
        updateDataFrame(df, x, y, d, colName, values[i])
    
def getDataframeValues(df, x, y, colName):
    t = df[df.X==x][df.Y == y]
    varray = []
    for v in t.filter([colName]).values:
        varray.append(v[0])
    return varray

def getDataframeColumn(df, colName):
    varray = []
    for v in df.filter([colName]).values:
        varray.append(v[0])
    return varray

def fixInterpolation(array):
    newarray = np.array(array, dtype=np.float64)
    if array[0] == -1:
        newarray[0] = 0
    if array[-1] == -1:
        newarray[-1] = 0
    
    startIndex = 0
    while -1.0 in newarray and startIndex < len(array):
        #find start index
        while newarray[startIndex] != -1.0:
            startIndex += 1
        startIndex -= 1 #go back one index to non negative number
        #find end index
        endIndex = startIndex + 1
        while newarray[endIndex] == -1:
            endIndex += 1
        
        if newarray[startIndex] ==  newarray[endIndex]:
            subarray = np.zeros((endIndex - startIndex))
            for i in range(len(subarray)):
                subarray[i] = newarray[startIndex]
        else:
            num = endIndex - startIndex
            step = (newarray[endIndex]-newarray[startIndex])/num
            subarray = np.arange(newarray[startIndex], newarray[endIndex], step, dtype=np.float64)

        for i in range(len(subarray)):
            newarray[startIndex + i] = subarray[i]

    return newarray

def fillInDataFrame(df, data, name, file):
    for x, y, strd, v in data.filter(['X','Y','Date', name]).values:
        s_year, s_month, s_day = strd.split('/')
        year = int(s_year) + 1900
        month = int(s_month)
        day = int(s_day)
        updateDataFrame(df, x, y, datetime.date(year, month, day), name, v )


    for x, y in df.filter(['X', 'Y']).drop_duplicates().values:
        z = getDataframeValues(df, x, y, name)
        nz = fixInterpolation(z)
        interpolateDataFrameForLocation(df, x, y, name, nz)


    df.to_csv(f"data/cleaned{file}.csv")



data = pd.read_csv("data/archive/data.csv")

startDate = datetime.date(1986, 4, 27)
endDate = datetime.date(1986, 6, 1)
days = (endDate-startDate).days

measurements = ["I_131_(Bq/m3)","Cs_134_(Bq/m3)","Cs_137_(Bq/m3)"]

# data[measurements] = data[measurements].replace("?", "NaN")
# data[measurements] = data[measurements].replace("L", "NaN")
# data[measurements] = data[measurements].replace("N", "NaN")

# data[measurements] = data[measurements].astype("float64")
# data.dropna(inplace=True)

x=[]
y=[]
for X, Y in data.filter(['X','Y']).drop_duplicates().values:
    for _ in range(days):
        x.append(X)
        y.append(Y)

dates=[]
for _ in range(len(x)//days):
    s = startDate
    for _ in range(days):
        dates.append(s)
        s += datetime.timedelta(days=1)

I131 = pd.DataFrame()
I131.insert(0, 'X', x)
I131.insert(1, 'Y', y)
I131.insert(2, 'date', dates)
I131.insert(3,"I_131_(Bq/m3)", -1.0)


CS134 = pd.DataFrame()
CS134.insert(0, 'X', x)
CS134.insert(1, 'Y', y)
CS134.insert(2, 'date', dates)
CS134.insert(3,"Cs_134_(Bq/m3)", -1.0)


CS137 = pd.DataFrame()
CS137.insert(0, 'X', x)
CS137.insert(1, 'Y', y)
CS137.insert(2, 'date', dates)
CS137.insert(3,"Cs_137_(Bq/m3)", -1.0)

fillInDataFrame(I131, data, "I_131_(Bq/m3)", "I131")
fillInDataFrame(CS134, data, "Cs_134_(Bq/m3)", "CS134")
fillInDataFrame(CS137, data, "Cs_137_(Bq/m3)", "CS137")

complete = pd.DataFrame()
complete.insert(0, 'X', x)
complete.insert(1, 'Y', y)
complete.insert(2, 'date', dates)
complete.insert(3, "I_131_(Bq/m3)", getDataframeColumn(I131,'I_131_(Bq/m3)'))
complete.insert(4, "Cs_134_(Bq/m3)", getDataframeColumn(CS134,'Cs_134_(Bq/m3)'))
complete.insert(5,"Cs_137_(Bq/m3)", getDataframeColumn(CS137,'Cs_137_(Bq/m3)'))

complete.to_csv("data/cleaned.csv")
