# District Level Load Profile Generator

Introduction: 

The objective of this tool is to automatically generate profiles of quarter-hourly electricity consumption on an annual basis for district level load profile in Waloon Low Voltage Electricity network. 
In that context, the present project aims at developing a software tool in Python able to generate quarter hourly electricity consumption profiles of district level in the Waloon at a user-defined time frame, which takes as input a list of attributes characterizing the concerned area (i.e. Population, Number of Tax Declarations, Number of Dwellings, Share of Dwellings with Different Rooms, Residential Density, Number of Unemployed People, Number of Shops).

The tool works in two different level:

1-High level (District Level)

2-Low-level (Residential Level)

“High level”:

Different hypothesizes have been developed at “High level” program to estimate the number of dwellings and their characterization in a district. 

“Low-level”:

At “low level”, it generates quarter hourly electricity consumption profiles of households by taking the list of attributes (e.g. surface, number of floors, number of inhabitants, quality of insulation, household heating with gas or electric, domestic water heating using electricity or not, etc.) characterizing each dwellings developed by High level program. 
Finally, the tool aggregates all load profiles of households as a residential load profile for district level. A typical non-residential load profile (as an aggregated load profile of shops at district level) is also added to the residential load profile to generate a district level load profile.  


Installation:

The tool requires the installation of Python as well as various libraries Python. To do this, it is necessary to download and install, for example, the Anaconda distribution (https://www.anaconda.com/distribution/ ). Once that a Python distribution is installed, the following libraries should be installed (pip install + name of the library)

Libraries, Version:

tslearn	 0.2.1

pandas	 0.25.1

sklearn	 0.21.3

numpy	   1.17.1


Details of developed tool:

To start the tool, “High_Level.py” should be executed. At first, it starts the high-level program, then automatically calls low level program “Low_Level.py” for generating a district level load profile. 
The tool generates “Output_ED_in_[kW]_for_High_Level.csv” file containing the district level load profile as final output.





1-High-Level:

In general, four type of doweling with predefined home appliances have been considered according to the income level of families (rich, average income, poor and very poor). Share of each family at the district level is estimated according to the Tax declarations. Families without any Tax declaration are considered as very very poor family. 
The sequential steps in the tool at High-Level program “High_Level.py” for estimating the number of doweling and their characterizations are as follows:


1-	Read "High_Level_Input_Data.csv" file as input-data characterizing the district level

2-	Estimate the number of dwellings in district level according to Tax-Conditions

3-	Define characteristic of rich family

4-	Define characteristic of average-income family  

5-	Define characteristic of poor family     

6-	Define characteristic of very poor family 

7-	Define characteristic of rich family with unemployed people at home 

8-	Define characteristic of poor family with unemployed people at home 

9-	Define characteristic of very poor family with unemployed people at home 

10-	Define characteristic of very very poor family (people without Tax declaration)  

11-	Write output file "High_Level_Dwellings.csv" 




2-Low-Level: 

In general, low-level program “Low_Level.py” will be automatically executed to run a k-nearest neighbors algorithm with Euclidean distance in the attribute space to find the K-nearest neighbors of attributes specified by High level program. Then applying Dynamic Time Warping Barycenter Averaging (DBA) to average the time series of all selected K-nearest neighbors and generate a load profile for the attributes specified by users. 
The sequential steps in the tool for generating a user-defined time frame of electricity demand are as follows: 


1-	Read "High_Level_Dwellings.csv" file

2-	Read "High_Level_ED_NonResidential.csv" file

3-	Read "Low_Level_ED.csv" as recorded profiles of houses (Residential Electricity Demand or ED)

4-	Read "Low_Level_Attributes.csv" file (specification of recorded houses)

5-	Read "High_Level_ED_NonResidential.csv" file as non-residential load profile (Non-Residential ED)

6-	Fill missed data in Residential ED (Low_Level_ED.csv) by value in last week

7-	Compute the Euclidean distance

8-	Find k-nearest neighbors and return corresponding profiles

9-	Time frame update

10-	Compute barycenter on the KNNs via DTW for each day

11-	Aggregation the generated ED according to the number of dwellings

12-	loop for generating ED profile of all dwelling

13-	Edit "High_Level_ED_NonResidential.csv" file according to user-defined time frame

14-	Select Non-Residential ED profile according to user-defined time frame

15-	Write output file "Output_ED_in_[kW]_for_High_Level.csv" 





K-Nearest Neighbors (KNN):

KNN is a distance-based classifier, meaning that it implicitly assumes that the smaller the distance between two points, the more similar they are. The idea behind is that “distance helps us quantify similarity” and more similar objects are more likely to be the same class. Depending on the context of the problem, several distance metrics can be used. Euclidean distance is used in this tool. In KNN, each column acts as a dimension. In a dataset with two columns, we can easily visualize this by treating values for one column as X coordinates and the other as Y coordinates. 

The equation at the heart of this distance is the Pythagorean theorem: 𝑎^2+𝑏^2=𝑐^2 and in general, for points given by Cartesian coordinates in n-dimensional space. For each dimension, subtract one point’s value from the others to get the length of that “side” of the triangle in that dimension, square it, and add it to running total. The square root of that running total is Euclidean distance.

KNN takes a point that we want a class prediction for calculates the distances between that point and every single point. It then finds the K closest points, or Neighbors, and examines the labels of each. 
In this tool, KNN as a Supervised learning algorithm works on Attributes space linked to each load profile in the data base to select load profiles with highest similarity to the Attributes specified by the user. 


Normalizing the Attributes:

Normalization of ratings means adjusting values measured on different scales to a notionally common scale, often prior to processing (preprocessing). Normalization transforms features by scaling each feature to a given range. 
This estimator scales and translates each feature individually such that it is in the given range on the training set, e.g. between zero and one.
To rescale a range between an arbitrary set of values [a, b]. In this tool all Attributes will normalize between zero and one [a=0, b=1]. 


Dynamic Time Warping Barycenter Averaging (DBA):

DBA stands for Dynamic Time Warping Barycenter Averaging. DBA is an averaging method that is consistent with Dynamic Time Warping.
