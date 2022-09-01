import pandas as pd
import time
import sys
from subprocess import call

# District Level Data
def read_DistrictLevelData():
    DistrictLevelData=pd.read_csv ("High_Level_Input_Data.csv", na_values=["nan", "NaN", "NAN", "na", "n/a", "/", "-", "--", ".", "_", "o", "O","None"],encoding='latin1')
    if DistrictLevelData.isnull().sum().sum() > 0:
        raise ValueError("some variables in DistrictLevelData.csv file are not defined")
    return DistrictLevelData

# Estimate the number of dwellings in district level
def Estimate_Number_of_Dwellings(DistrictLevelData): 
    From=pd.to_datetime(DistrictLevelData.iloc[0,0])
    To=pd.to_datetime(DistrictLevelData.iloc[0,1])
    if To <= From:
        raise ValueError("ADJUST TIME FRAME: Ending-date (To) should be after Starting-date (From)")
    NoShops=DistrictLevelData.iloc[0,2]
    Pop=DistrictLevelData.iloc[0,3]
    Tax=DistrictLevelData.iloc[0,4]
    TaxMedian=DistrictLevelData.iloc[0,5]
    TaxRatio=DistrictLevelData.iloc[0,6]
    TaxIQD=DistrictLevelData.iloc[0,7]
    Dwellings=DistrictLevelData.iloc[0,8]
    Room=DistrictLevelData.iloc[:,9:18]
    ResidentialDensity=(DistrictLevelData.iloc[0,18]/100)  #unités/hectare
    Unemployed=DistrictLevelData.iloc[0,19]
    TotalRoom=(Dwellings/100)*((1*Room.iloc[0,0])+(2*Room.iloc[0,1])+(3*Room.iloc[0,2])+(4*Room.iloc[0,3])+(5*Room.iloc[0,4])+(6*Room.iloc[0,5])+(7*Room.iloc[0,6])+(8*Room.iloc[0,7])+(9*Room.iloc[0,8]))
    RoomSize=(Dwellings/TotalRoom)/(ResidentialDensity)
    UnEpeople=Unemployed//(Tax/2)
    Inhabitant=Pop//Tax

    TaxQ1=((TaxRatio*TaxMedian)-TaxIQD+TaxMedian)/(TaxRatio+1)
    if TaxQ1 <0:
       TaxQ1=0
    TaxQ3=TaxIQD+TaxQ1
    TaxMin=TaxQ1-(1.5*TaxIQD)
    if TaxMin <0:
       TaxMin=0
    TaxMax=TaxQ3+(1.5*TaxIQD)
# Poverty Line (PL) for a single person (yearly income in euros)   
    PL1=1250*12
# Poverty Line (PL) for a family (yearly income in euros)       
    PL2=2500*12
# No.s of Dwelling based on Tax-Condition (default-Normal distribution)
    Ratio_Rich=0.25
    Ratio_Average=0.25
    Ratio_Poor=0.25
    Ratio_VPoor=0.25  
# No.s of Dwelling based on Tax-Condition-1
    if TaxMax <= PL1:
       Ratio_Rich=0.0
       Ratio_Average=0.0
       Ratio_Poor=0.10
       Ratio_VPoor=0.90
# No.s of Dwelling based on Tax-Condition-2
    if PL1 <= TaxMax <= PL2 and TaxMedian < PL1:
       Ratio_Rich=0.0
       Ratio_Average=0.0
       Ratio_Poor=0.40
       Ratio_VPoor=0.60
# No.s of Dwelling based on Tax-Condition-3
    if TaxMax <= PL2 and TaxMedian == PL1:
       Ratio_Rich=0.0
       Ratio_Average=0.10
       Ratio_Poor=0.40
       Ratio_VPoor=0.50
# No.s of Dwelling based on Tax-Condition-4
    if TaxMax <= PL2 and PL1 < TaxMedian <= PL2 and TaxMin <= PL1:
       Ratio_Rich=0.0
       Ratio_Average=0.10
       Ratio_Poor=0.60
       Ratio_VPoor=0.30
# No.s of Dwelling based on Tax-Condition-5
    if TaxMax > PL2 and PL1 <= TaxMedian <= PL2 and TaxMin <= PL1:
       Ratio_Rich=0.05
       Ratio_Average=0.15
       Ratio_Poor=0.50
       Ratio_VPoor=0.30
# No.s of Dwelling based on Tax-Condition-6
    if TaxMax > PL2 and TaxMedian > PL2 and TaxMin <= PL1:
       Ratio_Rich=0.20
       Ratio_Average=0.50
       Ratio_Poor=0.20
       Ratio_VPoor=0.10
# No.s of Dwelling based on Tax-Condition-7
    if TaxMax > PL2 and TaxMedian==PL2 and TaxMin <= PL1:
       Ratio_Rich=0.15
       Ratio_Average=0.50
       Ratio_Poor=0.25
       Ratio_VPoor=0.10
# No.s of Dwelling based on Tax-Condition-8
    if PL1 <= TaxMax <= PL2 and PL1 <= TaxMin <= PL2:
       Ratio_Rich=0.0
       Ratio_Average=0.15
       Ratio_Poor=0.70
       Ratio_VPoor=0.15
# No.s of Dwelling based on Tax-Condition-9
    if TaxMax >= PL2 and PL1 < TaxMedian < PL2 and PL1 <= TaxMin < PL2:
       Ratio_Rich=0.10
       Ratio_Average=0.15
       Ratio_Poor=0.70
       Ratio_VPoor=0.05
# No.s of Dwelling based on Tax-Condition-10
    if TaxMax >= PL2 and TaxMedian==PL2 and PL1 <= TaxMin < PL2:
       Ratio_Rich=0.20
       Ratio_Average=0.45
       Ratio_Poor=0.30
       Ratio_VPoor=0.05
# No.s of Dwelling based on Tax-Condition-11
    if TaxMax > PL2 and TaxMedian > PL2 and PL1 <= TaxMin <= PL2:
       Ratio_Rich=0.35
       Ratio_Average=0.50
       Ratio_Poor=0.10
       Ratio_VPoor=0.05
# No.s of Dwelling based on Tax-Condition-12
    if TaxMin >= PL2:
       Ratio_Rich=0.80
       Ratio_Average=0.20
       Ratio_Poor=0.0
       Ratio_VPoor=0.0   
# if there is UnEmployed (UE) peopel     
    if UnEpeople > 0:
       Ratio_Rich=Ratio_Rich/2 
       Ratio_Average=Ratio_Average/2
       Ratio_Poor=Ratio_Poor/2
       Ratio_VPoor=Ratio_VPoor/2      

# Characteristic of Rich Family
    RichFamily=pd.DataFrame()
    for i in range (9):   
       RichHome=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Rich,Inhabitant,0,1,1,1,1,1,0,0,0,2,(i+1)*RoomSize,1,(i+1),1,5]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Rich-Room"+str(i+1)])
       if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Rich)!=0:
          RichFamily=RichFamily.append(RichHome)
# Characteristic of Average-income Family       
    AverageFamily=pd.DataFrame()
    for i in range (9):   
       AverageHome=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Average,Inhabitant,0,1,1,0,1,0,0,0,0,1,(i+1)*RoomSize,6,(i+1),1,3]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Average-Room"+str(i+1)])
       if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Average)!=0:
          AverageFamily=AverageFamily.append(AverageHome)
# Characteristic of Poor Family     
    PoorFamily=pd.DataFrame()
    for i in range (9):   
        PoorHome=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Poor,Inhabitant,0,0,1,0,0,0,0,0,0,0,(i+1)*RoomSize,6,(i+1),1,2]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Poor-Room"+str(i+1)])
        if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Poor)!=0:
           PoorFamily=PoorFamily.append(PoorHome)
# Characteristic of Very Poor Family         
    VeryPoorFamily=pd.DataFrame()
    for i in range (9):   
        VeryPoorHome=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_VPoor,Inhabitant,0,0,0,0,0,0,0,0,0,0,(i+1)*RoomSize,7,(i+1),0,1]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["VeryPoor-Room"+str(i+1)])
        if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_VPoor)!=0:
           VeryPoorFamily=VeryPoorFamily.append(VeryPoorHome)   
    
    Family=RichFamily.append(AverageFamily.append(PoorFamily.append(VeryPoorFamily)))
       
# Characteristic of Rich Family with UnEmployed (UE) people at home   
    RichFamily_Unemployed=pd.DataFrame()
    for i in range (9):   
       RichHome_Unemployed=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Rich,Inhabitant,UnEpeople,1,1,1,1,1,1,16,10,2,(i+1)*RoomSize,2,(i+1),1,5]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Rich-UE-Room"+str(i+1)])
       if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Rich)!=0:
          RichFamily_Unemployed=RichFamily_Unemployed.append(RichHome_Unemployed)
# Characteristic of Average-income Family with UnEmployed (UE) peopel at home    
    AverageFamily_Unemployed=pd.DataFrame()
    for i in range (9):   
       AverageHome_Unemployed=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Average,Inhabitant,UnEpeople,1,1,0,1,0,1,7.5,2.6,1,(i+1)*RoomSize,5,(i+1),1,3]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Average-UE-Room"+str(i+1)])
       if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Average)!=0:
          AverageFamily_Unemployed=AverageFamily_Unemployed.append(AverageHome_Unemployed)
# Characteristic of Poor Family with UnEmployed (UE) people at home       
    PoorFamily_Unemployed=pd.DataFrame()
    for i in range (9):   
        PoorHome_Unemployed=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_Poor,Inhabitant,UnEpeople,0,1,0,0,0,1,3.5,1.9,0,(i+1)*RoomSize,6,(i+1),0,2]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["Poor-UE-Room"+str(i+1)])
        if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_Poor)!=0:
           PoorFamily_Unemployed= PoorFamily_Unemployed.append(PoorHome_Unemployed)
# Characteristic of very Poor Family with UnEmployed (UE) people at home              
    VeryPoorFamily_Unemployed=pd.DataFrame()
    for i in range (9):   
        VeryPoorHome_Unemployed=pd.DataFrame([[Dwellings*(Room.iloc[0,i]/100)*Ratio_VPoor,Inhabitant,UnEpeople,0,0,0,0,0,1,1.2,0.7,0,(i+1)*RoomSize,7,(i+1),0,1]],
                             columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'],
                             index=["VeryPoor-UE-Room"+str(i+1)])
        if round(Dwellings*(Room.iloc[0,i]/100)*Ratio_VPoor)!=0:
           VeryPoorFamily_Unemployed= VeryPoorFamily_Unemployed.append(VeryPoorHome_Unemployed)  
    
    Family_Unemployed=RichFamily_Unemployed.append(AverageFamily_Unemployed.append(PoorFamily_Unemployed.append(VeryPoorFamily_Unemployed)))
    Family=Family.append(Family_Unemployed)
# Characteristic of very very Poor Family (people without Tax declaration)   
    VeryVeryPoorPeopel=Family['Dwellings']*Family['Number of inhabitants']
    VeryVeryPoorPeopel=VeryVeryPoorPeopel.sum()
    VeryVeryPoorPeopel=Pop-VeryVeryPoorPeopel
    DwellingsViaTax=Family['Dwellings'].sum()
    
    if VeryVeryPoorPeopel > 0 and (VeryVeryPoorPeopel//(Dwellings-DwellingsViaTax)) >0:
       VeryVeryPoorPeopel=VeryVeryPoorPeopel//(Dwellings-DwellingsViaTax)
    else:
        VeryVeryPoorPeopel=1
    
    if Dwellings-DwellingsViaTax > 0:
       VeryVeryPoorFamily=pd.DataFrame([[Dwellings-DwellingsViaTax,VeryVeryPoorPeopel,0,0,0,0,0,0,1,0.6,0.3,0,1*RoomSize,7,1,0,1]], 
                                       columns=['Dwellings','Number of inhabitants','Number of people staying at home during the day','Dishwasher','Clothes Washer','Dryer ','Electric Cooking','Electric sanitary Hot Water','Day-night Tariff','Annual Electricity Consumption (MWh)','Annual Electricity Consumption at Night Tariff (MWh)','Heating System','Total Surface of House (m2)','Building Energy Rating','Total Number of Rooms','Apartment or House', 'Number of Walls Connected to the External Ambiance'], 
                                       index=['VVPoor'])
       Family=Family.append(VeryVeryPoorFamily)
 
    Dwellings=Family
    Dwellings.insert(0,'From',From)
    Dwellings.insert(1,'To',To)
    Dwellings.insert(2,'NoShops',NoShops)
    return Dwellings
# Write output file "High_Level_Dwellings.csv" 
def Write_Output (Dwellings):
    Dwellings.to_csv("High_Level_Dwellings.csv", date_format='%Y%m%d% H%M%S')
    

def main():
    DistrictLevelData=read_DistrictLevelData()
    Dwellings=Estimate_Number_of_Dwellings(DistrictLevelData)
    Write_Output (Dwellings)
    call(["python", "Low_Level.py"]) 
    
if __name__ == "__main__":

    main()
     
         
    