import pandas as pd
import numpy as np
from sklearn import preprocessing
from tslearn import barycenters



def read_DBed ():
    ed=pd.read_csv("ED.csv",na_values=["nan", "NaN", "NAN", "na", "n/a", "/", "-", "--", ".", "_", "o", "O","None"],encoding='latin1')
    return ed

def read_DBattributes():
    Attributesdata=pd.read_csv("Attributes.csv",  na_values=["nan", "NaN", "NAN", "na", "n/a",
                                                                 "/", "-", "--", ".", "_", "o",
                                                                 "O", "None"],encoding='latin1')
    Attributesdata=Attributesdata.iloc[:, 1:]
    # Replace missing attributes by averages on the whole dataset
    Attributesdata.fillna(Attributesdata.mean(), inplace=True)
    return Attributesdata

def read_high_level_dwellings():    
    high_level_dwellings = pd.read_csv("High_Level_Dwellings.csv",encoding='latin1')
    From = pd.to_datetime(high_level_dwellings.iloc[:,1])
    To = pd.to_datetime(high_level_dwellings.iloc[:,2])
    ToUser = To
    high_level_dwellings.insert(3,"ToUser",ToUser)

    EDuser = high_level_dwellings.iloc[:,12] #daynighttarif

    for i in range(len(From)):  #si y'a un tarif daynight (compteur bi-horaire), alors on rajoute 1 an
        if EDuser.at[i] > 0:
           To.at[i]=From.at[i]+pd.DateOffset(years=1)
    high_level_dwellings['To']=To


    return high_level_dwellings

def loop_ED (Dwellings, ed, k, Attributesdata):
    output=pd.DataFrame()
    for i in range(len(Dwellings)): #Nombres de type de maison et comportement consomm
        From=pd.to_datetime(Dwellings.iloc[i,1])
        To=pd.to_datetime(Dwellings.iloc[i,2])
        ToUser=pd.to_datetime(Dwellings.iloc[i,3])
        NoDwellings=Dwellings.iloc[i,5]
        DwellingsAttributes=Dwellings.iloc[i,6:]
        DwellingsAttributes=pd.DataFrame(DwellingsAttributes)
        DwellingsAttributes=DwellingsAttributes.T
        ### KNN generation part
        # Find KNNs
        KNN_EDs=find_KNN(ed, k, Attributesdata, DwellingsAttributes)
        ### Time frame update:
        To_edited, From_edited=update_From(From, ToUser)

        ### Generate ED profile using DTW averaging
        ED_profile=DTW_Averaging(KNN_EDs, From_edited, To_edited)


        ### Aggregation the generated ED
        ED_profile=aggregation_ED (ED_profile, DwellingsAttributes, NoDwellings, From, To, ToUser)
        ### Output results
        output[i]=ED_profile


    return output

def read_ED_NonResidential():    
    ED_NonResidential=pd.read_csv("High_Level_ED_NonResidential.csv",na_values=["nan", "NaN", "NAN", "na", "n/a", "/", "-", "--", ".", "_", "o", "O","None"],encoding='latin1')
    return ED_NonResidential

def Euclidean_Distance (input_data_min_max,user_min_max):
    user_data=pd.DataFrame (user_min_max)
    user_data=list (user_data.iloc[0,:])
    input_data=pd.DataFrame (input_data_min_max)
    sq=np.square(input_data-user_data)
    sum_sq=sq.sum(axis=1)
    distance=np.sqrt(sum_sq)
    return distance

def find_KNN (n,k,Attributesdata,DwellingsAttributes):
    # Data preprocessing: normalizing the attributes
    min_max_Scaler=preprocessing.MinMaxScaler()
    input_data_min_max=min_max_Scaler.fit_transform(Attributesdata)
    Dwellings_min_max=min_max_Scaler.transform(DwellingsAttributes)
    # KNN with Euclidean distance
    dis=Euclidean_Distance (input_data_min_max,Dwellings_min_max)
    ranked_dis=sorted(range(len(dis)), key=lambda x:dis[x])[:k]
    KNN_EDs=[]
    for i in range(k):
        KNN_EDs.insert(0, list (n.iloc[:,ranked_dis [i]]))
    KNN_EDs=KNN_EDs
    return KNN_EDs

def update_From (From,To):
    # Yearly update
    From_edited=From+pd.DateOffset(days=(To.year-2021))
    To_edited=To+pd.DateOffset(days=(To.year-2021))
    # To determine whether a year is after a leap year
    From_edited=From_edited+pd.DateOffset(days=((From_edited.year-2020)//5))
    To_edited=To_edited+pd.DateOffset(days=((To_edited.year-2020)//5))
    # Yearly update
    From_edited=From_edited+pd.DateOffset(days=(To_edited.year-To.year))
    To_edited=To_edited+pd.DateOffset(days=(To_edited.year-To.year))
    return To_edited, From_edited

def DTW_Averaging (KNN_EDs,From_edited,To_edited):
    ed_knn=pd.DataFrame(KNN_EDs)
    ed_knn=ed_knn.T
    ed=[]
    if From_edited.year == To_edited.year:
        From_ed = pd.date_range(start=str(From_edited.year) + "-01-01 00:00",
                                end=From_edited,
                                freq="15 min")

        Range_ed = pd.date_range(start=From_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 end=To_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 freq="15 min")
        h = (len(From_ed) % 96) - 1
        for d in range(len(From_ed)//96, (len(From_ed)//96)+(len(Range_ed)//96), 1):
            ed_day=ed_knn.iloc[(d * 96 + h):(96 + (96 * d) + h), :]
            ed_day_t=ed_day.T
            dtw_day=barycenters.dtw_barycenter_averaging(ed_day_t.values.tolist(), max_iter=5)
            ed=np.append(ed, dtw_day)
            ed=pd.DataFrame(data=list(ed))

        return ed
    else:
        From_ed = pd.date_range(start=str(From_edited.year)+ "-01-01 00:00", end=From_edited, freq="15 min")

        h = (len(From_ed) % 96) - 1
        for d in range(len(From_ed)//96, 365, 1):
            ed_day = ed_knn.iloc[(d * 96 + h):(96 + (96 * d) + h), :]
            ed_day_t = ed_day.T
            dtw_day = barycenters.dtw_barycenter_averaging(ed_day_t.values.tolist(), max_iter=5)
            ed = np.append(ed, dtw_day)
            ed_first = pd.DataFrame(data=list(ed))
        ed=[]
        Range_ed = pd.date_range(start=str(To_edited.year) + "-01-01 00:00",
                                 end=To_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 freq="15 min")
        for d in range(0, (len(Range_ed)//96), 1):
            ed_day = ed_knn.iloc[(d * 96 + h):(96 + (96 * d) + h), :]
            ed_day_t = ed_day.T
            dtw_day = barycenters.dtw_barycenter_averaging(ed_day_t.values.tolist(), max_iter=5)
            ed = np.append(ed, dtw_day)
            ed_second = pd.DataFrame(data=list(ed))

        ed = ed_first.append(ed_second)

    return ed

def aggregation_ED (x, DwellingsAttributes, NoDwellings, From, To, ToUser):
    if NoDwellings > 0:
       x=x.multiply(NoDwellings)
    EDuser=DwellingsAttributes.iloc[0,8]
    EDsum=x.sum(axis=0,skipna=True)
    # UserED (MWh) & SumED (kW)
    EDsum=EDsum/4000
    if EDuser > 0:
       x=x.multiply(EDuser/EDsum)
    idx = pd.date_range(start=From.strftime("%Y-%m-%d %H:%M:%S"),
                        end=To.strftime("%Y-%m-%d %H:%M:%S"),
                        freq="15 min")

    x.index = idx
    x = x[From:To]

    return x

def edited_EDNonResidential (ED_NonResidential,Dwellings):
    From=pd.to_datetime(Dwellings.iloc[0,1])
    To=pd.to_datetime(Dwellings.iloc[0,2])
    To_edited, From_edited=update_From(From,To)
    ed_knn=ED_NonResidential
    ed=[]
    if  From_edited.year==To_edited.year:
        From_ed = pd.date_range(start=str(From_edited.year) + "-01-01 00:00",
                                end=From_edited,
                                freq="15 min")

        Range_ed = pd.date_range(start=From_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 end=To_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 freq="15 min")
        h = (len(From_ed) % 96) - 1

        for d in range(len(From_ed)//96, (len(From_ed)//96)+(len(Range_ed)//96), 1):
            ed_day=ed_knn.iloc[d*96:96+(96*d) + h, :]
            ed=np.append(ed,ed_day)
        return ed
    else:
        From_ed=pd.date_range(start=str(From_edited.year)+ "-01-01 00:00", end=From_edited, freq="15 min")
        h = (len(From_ed) % 96) - 1

        for d in range(len(From_ed)//96, 365, 1):
            ed_day=ed_knn.iloc[d*96:96+(96*d) + h, :]
            ed=np.append(ed, ed_day)
            ed_first=ed
        ed=[]
        Range_ed = pd.date_range(start=str(To_edited.year) + "-01-01 00:00",
                                 end=To_edited.strftime("%Y-%m-%d %H:%M:%S"),
                                 freq="15 min")
        for d in range(0, (len(Range_ed)//96), 1):
            ed_day=ed_knn.iloc[d*96:96+(96*d) + h,:]
            ed=np.append(ed, ed_day)
            ed_second=ed
        ed=ed_first.append(ed_second)
    return ed

def NonResidential(editedEDNonResidential,Dwellings):
    From=pd.to_datetime(Dwellings.iloc[0,1])
    To=pd.to_datetime(Dwellings.iloc[0,2])
    ToUser=pd.to_datetime(Dwellings.iloc[0,3])
    NoShops=Dwellings.iloc[0,4]
    x=pd.DataFrame(editedEDNonResidential)
    idx=pd.date_range(start=From.strftime("%Y-%m-%d %H:%M:%S"), end=To.strftime("%Y-%m-%d %H:%M:%S"), freq="15 min")
    x.index=idx
    x=x[From:To]
    print(f"index : {idx}")

    x=x*NoShops
    return x

def write_ED(outputResidential,ED_NonResidential):
    outputResidential=outputResidential.sum(axis=1,skipna=True) 
    outputResidential=pd.DataFrame(outputResidential)
    output=outputResidential+ED_NonResidential
    output.to_csv("Output_ED_in_[kW]_for_High_Level.csv")

def fill_Missed_Data(x):
    x=x.iloc[: , 1:]
    x=x.replace(["nan", "NaN", "NAN", "na", "n/a", "/", "-", "--", ".", "_", "o", "O","None"], np.NaN)
    index=pd.DataFrame(np.where(np.asanyarray(np.isnan(x))))
    w=1
    while x.isnull().values.any()==True:
        for i in (list(set(index.iloc[1,:]))):
            inds=np.where(x.iloc[:,i].isnull())[0]
            inds_new=inds-[96*7*w]
            last_week=x.iloc[inds_new.tolist(),i]
            x.iloc[inds.tolist(),i]=[last_week]
        w=1+w
        if x.isnull().values.any()==True and w==5:
            x.fillna(0, inplace=True)
    x_last_week=x
    return (x_last_week)

def main():

    ed=read_DBed()
    ed=fill_Missed_Data(ed)
    Attributesdata=read_DBattributes()
    k=int(np.sqrt(len(Attributesdata)))
    k=k+((k+1) % 2) # Rule of thumb: k = Sqrt(number of load profiles)
    # Reading High_Level_Dwellings.csv # Reading High_Level_Dwellings.csv generated by "High_Level.py"
    Dwellings = read_high_level_dwellings()
    # loop for ED generation of each Dwelling in "High_Level_Dwellings.csv" file
    outputResidential=loop_ED(Dwellings, ed, k, Attributesdata)
    # Read "High_Level_ED_NonResidential.csv" as load profile of shopes downloaded from [http://www.synergrid.be/index.cfm?PageID=16896]
    ED_NonResidential=read_ED_NonResidential()
    # Routine for filling missing values in "High_Level_ED_NonResidential.csv"
    ED_NonResidential=fill_Missed_Data(ED_NonResidential)
    # Edit "High_Level_ED_NonResidential.csv" according to the Time-frame
    editedEDNonResidential=edited_EDNonResidential(ED_NonResidential, Dwellings)
    # Select user-defined time-frame from "High_Level_ED_NonResidential.csv"
    ED_NonResidential=NonResidential(editedEDNonResidential, Dwellings)
    # Write output file "Output_ED_in_[kW]_for_High_Level.csv" for generated High_Level ED profile
    write_ED(outputResidential, ED_NonResidential)
    
if __name__ == "__main__":
       
    main()      
