# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:20:28 2021

@author: fatjo876
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry.polygon import Polygon, LineString
from eppy.modeleditor import IDF
import numpy as np
import matplotlib.pyplot as plt
import os,  glob
from time import time
from multiprocessing import Pool
import multiprocessing
from shapely import wkt

from simulation import Simulation
from archetype import Archetype
from occupancy import Initials
from hvac import HVAC
from visualization import Visualization





""" Initializing the simulation tool EnergyPlus """

# Call the idd (EnergyPlus exe file)
iddfile = "C:/EnergyPlusV9-2-0/Energy+.idd"

# Initialize the idf file processing.
IDF.setiddname(iddfile)


""" Importing the input parameters """

# EnergyPlus weather file.
#epw = "inputs/SWE_Stockholm.Arlanda.024600_IWEC.epw"
epw = "inputs/tmy_Borlange_2005_2020.epw"

#gis = gpd.read_file('X:/UBEM/data/GIS_Borlänge/footprintData')
gis = pd.read_csv('X:/UBEM/Data Pre-processing/outputData/processedGisDataBorlange.csv')
gis['geometry'] = gis['geometry'].apply(wkt.loads)
gis = gpd.GeoDataFrame(gis, crs='epsg:3006')
gis = gis.drop('Unnamed: 0', axis = 1)
gis = gis.drop_duplicates(subset=['buildingId','geometry'])
gis = gis.reset_index(drop=True)

# The Geocoded building data from the previous methods.
df = pd.read_csv('X:/UBEM/Data Pre-processing/outputData/processedGisDataBorlangeWithEPCCalibrated.csv')

#df = pd.read_csv('X:/UBEM/Data Pre-processing/outputData/dfCompleteBorlangeCalibratedV1.csv')
#df = pd.read_excel('X:/UBEM/Data Pre-processing/outputData/dfCompleteGISonlyModifiedHeightBorlange.xlsx')

df['geometry'] = df['geometry'].apply(wkt.loads)
df = gpd.GeoDataFrame(df, crs='epsg:3006')
df = df.drop('Unnamed: 0', axis = 1)

df = df[(df['EgenAntalPlan']!=0)&
        (df['EgenAtemp']!=0)]

df = df[df['costructionYear']!=0]
df = df.reset_index(drop=True)


# Input parameters from a user defined text file.
parameters = pd.read_csv('parameters.txt', sep = ',', header = 'infer', 
                         encoding= 'ANSI')


""" Initializing the input parameters """

# Hot and cold water temperatures for domestic hot water use.
hotWaterTemp = parameters.hotWaterTemp[0]
coldWaterTemp = parameters.coldWaterTemp[0]

infiltration = pd.read_csv('archetypesCalibrated.txt').infiltration
#infiltration = 0

"ARCHETYPES"
#cosntruction = pd.read_csv('construction.txt', sep = ',')


#---------------------------------------------------
def leap_year(year):
    """
    Checks if the given year is leap year
    """
    if ((year % 400 == 0) or (year % 100 == 0) and (year % 4 ==0)):
        return 1
    else:
        return 0



firstDayOfYear = pd.read_csv(epw,sep=',',skiprows = 7,
                             low_memory=False).columns[4]

year = int(pd.read_csv(epw,sep=',',skiprows = 8, low_memory=False).columns[0])
leapYear = leap_year(year)

occupancyInputs = pd.read_csv('occupancyInputs.csv', sep=';',low_memory=False)
buildings = ['Apartment', 'House']

for i in range(2):
    occupancy = occupancyInputs.iloc[:,2*i:2*i+2]
    personHeat = occupancyInputs.iloc[:,2*i+4:2*i+6]
    appliances = occupancyInputs.iloc[:,2*i+8:2*i+10]
    hotWater = occupancyInputs.iloc[:,2*i+12:2*i+14] 
    lighting = occupancyInputs.iloc[:,(24*i+20):(23*i+45)]

    _,_,_,_,_,maxFlowHotWater = Initials.profile_generator (occupancy,
                                                            personHeat, 
                                                            appliances,
                                                            hotWater,
                                                            lighting, 
                                                            firstDayOfYear,
                                                            leapYear, 
                                                            buildings[i])

# MULTIPROCESSING SIMULATION RUN FOR THE DATASET
#-----------------------------------------------


def remove ():
    """
    Removes the output files from EnergyPlus after each simulation run.
    """
    for filename in glob.glob('eplus*'):
        os.remove(filename)
    return None



"RUNS the SIMULATION"
if __name__ == '__main__':
    nThreads = multiprocessing.cpu_count()

    with Pool(nThreads) as p:
        t1 = time()
        print('_________________________')
        print('SIMULATION IS RUNNING ...')
        print('                         ')
        
        DH = []
        A = []
        for i in range (len(df)):           
            print ('Building',i,'/',len(df))
            try:
                dff = gpd.GeoDataFrame((df.iloc[i]).to_frame().T).reset_index(drop=True)
                dff = dff.set_crs('EPSG:3006')
                idx = i
                buildingType = dff.buildingType[0]
                mainType = Archetype.building_type(buildingType)
                buildingYear = dff.costructionYear[0]
                arch = Archetype.archetype(mainType, buildingYear)
                A.append(arch)

                #floorHeight = 2.8
                floorHeight = 2.5 #!! Change the height for the occupanct as well. 
                buildingId = dff.buildingId[0]
                buildingPolygon= Polygon (dff.geometry[0])            
                basementInfo = dff.EgenAntalKallarplan[0]
                #buildingHeight = dff.modifiedHeight[0] 
                buildingHeight = (dff.EgenAntalPlan[0]*floorHeight) + (1 if basementInfo!=0 else 0)
                buildingArea = dff.area[0]
                propertyCode = dff.propertyCode[0]
                buildingFloor = dff.EgenAntalPlan[0] #On ground floors
                #buildingFloor = np.round(buildingHeight/2.8)
                windowAreaBBR = np.round(buildingArea * buildingFloor * 0.1)
                perimeter = 0
                x,y = dff.geometry[0].exterior.xy
                for j in range(len(x)-1):
                    line = LineString([(x[j],y[j]),(x[j+1],y[j+1])]).length
                    if line>2:
                        perimeter += line
                        
                wwr = windowAreaBBR/(perimeter * buildingFloor*floorHeight)
    
                
                material_idf = IDF("archetypesCalibrated/Archetype%d.idf" %arch)   
                heatRecovery = 1 if dff.VentTypFTX[0] =='Ja' or dff.VentTypFmed[0]=='Ja' else 0
                heatRecoveryEffect = 0.5 if heatRecovery == 1 else 0
                infFlow = infiltration[arch-1]
                idf = Simulation.building_idf (buildingPolygon, buildingArea, 
                                               buildingHeight, buildingId, 
                                               basementInfo, epw, 
                                               wwr, material_idf,
                                               df, hotWaterTemp, coldWaterTemp, 
                                               maxFlowHotWater, mainType,
                                               heatRecovery, heatRecoveryEffect,
                                               infFlow, gis, idx, propertyCode)
                DH.append(Simulation.simulation (idf ,basementInfo))
    
                remove()
            except:
                DH.append([0,0,0,0,0])
            
             
    t2 = time()
    print('SIMULATION IS DONE!')
    print('                   ')
    print("----- Running time:", (t2-t1)//60, ' minutes and', np.round((t2-t1)-60*(t2-t1)//60,2)*60, ' seconds')
    print("----- Running time per building:", np.round((t2-t1)/len(df),2), ' seconds')

#VALIDATION OF RESULTS
#-----------------------------

df['archetype']=A



dh = pd.DataFrame(DH)


Troom = []
Tamb = []
SH = []
DHW = []
annualDHW = []
El = []
annualSH = []
annualElHousehold = []
tot = []
EP = []
for i in range(len(dh)):
    Tamb.append(dh[0][i])
    Troom.append(dh[1][i])
    El.append(dh[2][i])
    SH.append(dh[3][i])
    DHW.append(dh[4][i])
    annualDHW.append(np.sum(dh[4][i]))
    annualSH.append(np.sum(dh[3][i]))
    annualElHousehold.append(np.sum(dh[2][i]))
    tot.append(np.sum(dh[4][i])+np.sum(dh[3][i]))
    EP.append(df.EgiEnergianvandning[i]-df.EgiFastighet[i]+df.EgiBerEngProduktion[i])


   
    
plt.scatter(tot, EP)

df['Troom'] = Troom
df['Tamb'] = Tamb
df['DHW'] = DHW
df['El'] = El
df['SH'] = SH
df['tot'] = tot
df['annualSH']= annualSH
df['annualDHW'] = annualDHW
df['annualElHousehold'] = annualElHousehold
df['EPC(kWh/y)'] = EP

new = df[(df['tot']!=0)|(df['tot']!='NaN')|(df['EgiEnergianvandning']==0)].reset_index(drop=True)




TgroundMonthly = np.array(pd.read_csv(epw, header=None,sep = "[,\n]", skiprows=3,
                      skipfooter = 8764, engine='python').iloc[0,38:])
        
Tground = []
for i in range(12):
    Tg =np.tile( TgroundMonthly[i], 730)
    Tground.append(Tg) 
       
Tground = np.array(Tground).flatten()



annualEnergy= []
annualHeat = []
annualWood = []
annualEl = []
hourlyEnergy = []

j = 0  #SHOULD BE FIXED
for i in range(len(new)):
    dff = gpd.GeoDataFrame((new.iloc[i]).to_frame().T).reset_index(drop=True)
    dff = dff.set_crs('EPSG:3006')
    dff['districtHeat'] = dff['EgiFjarrvarmeUPPV'][0]+dff['EgiFjarrvarme'][0]
    dff['groundHeatPump'] = dff['EgiPumpMarkUPPV'][0] + dff['EgiPumpMark'][0] 
    dff['exhaustHeatPump'] = dff['EgiPumpFranluftUPPV'][0]+dff['EgiPumpFranluft'][0]
    dff['airHeatPump'] = dff['EgiPumpLuftLuftUPPV'][0] + dff['EgiPumpLuftLuft'][0]
    dff['directElectric']= dff['EgiElDirektUPPV'][0]+dff['EgiElDirekt'][0]+ dff['EgiElVattenUPPV'][0]+ dff['EgiElVatten'][0]+ dff['EgiElLuftUPPV'][0]+dff['EgiElLuft'][0]                          
    dff['Boiler'] = dff['EgiVedUPPV'][0]+ dff['EgiVed'][0] + dff['EgiFlisUPPV'][0]+dff['EgiFlis'][0]+dff['EgiOljaUPPV']+ dff['EgiOlja']+dff['EgiGasUPPV']+dff['EgiGas']
    
    
    total = float(dff['districtHeat'][0] + dff['groundHeatPump'][0]*4 +
                  dff['airHeatPump'] * 3 + dff['exhaustHeatPump'][0] * 2.5 +
                  dff['directElectric'][0] + 
                  dff['Boiler'][0]* 0.7)
    
    shareDistrictHeat = dff['districtHeat'][0] /total
    shareGroundHeatPump = dff['groundHeatPump'][0]*4/total
    shareExhaustHeatPump = dff['exhaustHeatPump'][0]* 2.5/total
    shareAirHeatPump = dff['airHeatPump'][0]* 3/total
    shareDirectElectric = dff['directElectric'][0]/total
    shareBoiler = dff['Boiler'][0]*0.7/total
    
    if np.sum(new['SH'][j])>0:
        EGSHP = HVAC.GSHP(np.array(Tamb[i]),np.array(Tground),np.array(new['SH'][j])*shareGroundHeatPump)
        EXAHP = HVAC.XSHP(np.array(Tamb[i]),np.array(new['Troom'][i]),np.array(new['SH'][j])*shareExhaustHeatPump)
        EASHP = HVAC.ASHP(np.array(Tamb[i]),np.array(new['SH'][j])*shareAirHeatPump)
        EDH = np.array(new['SH'][j])*shareDistrictHeat
        EWB = np.array(new['SH'][j])*shareBoiler/0.7
        EDEL = np.array(new['SH'][j]*shareDirectElectric)
        
        E = np.sum(EGSHP+EXAHP+EASHP+EDH+EWB+EDEL)
        Ehour = EGSHP+EXAHP+EASHP+EDH+EWB+EDEL+dff['DHW'][0]
        eltot= np.sum(EGSHP+EXAHP+EASHP+EDEL)
    else:
        E = 0
    hourlyEnergy.append(Ehour)
    annualEnergy.append(E)
    annualHeat.append(np.sum(EDH))
    annualEl.append(eltot)
    annualWood.append(np.sum(EWB)/(18/3.6))
    j += 1    
 

new['annualEnergy'] = (np.array(annualEnergy)+np.array( new['annualDHW'])).flatten()
new['annualElSH']= annualEl
new['annualHeatSH'] = annualHeat
new['annualWoodSH']= annualWood
new['hourlyEnergy']= hourlyEnergy




new = new[new['annualEnergy'].notna()].reset_index(drop=True)
new['EPC']= new.EgiEnergianvandning-new.EgiFastighet+new.EgiBerEngProduktion
new['PE'] = (new.annualEnergy-new.EPC)/new.EPC
new = new[new['PE']<2]
new['APE'] = np.abs(new.PE)


new.to_excel('results/processedGisDataBorlangeWithEPCCalibrated-Results2023.xlsx')

    print(np.mean(new['APE']), len(new),np.mean(new['annualEnergy']//new['EgenAtemp']),
          np.mean(new['EPC']//new['EgenAtemp']))

# ANALYSYS

for i in (range(1,16)):
    a = new[new['archetype']==i].reset_index(drop=True)
    
    print(np.round(np.mean(a['APE']*100)), len(a),np.round(np.mean(a['annualEnergy']//a['EgenAtemp'])),
          np.round(np.mean(a['EPC']//a['EgenAtemp'])))

#_____________________________________________________________

properties = new['propertyCode'].unique()

APE =[]
for i in properties:
    a = new[new['propertyCode']==i]
    sim = np.sum(a['annualEnergy'] )
    epc = np.sum(a['EPC'])
    ape = np.abs((sim-epc)/epc)
    APE.append(ape)
    
np.mean(APE)
len(properties)

district = new['propertyCode'].str.replace(' \d+:\d+', '',regex=True)
district = district.str.replace(' \d+', '',regex=True)
districts = district.unique()


APE =[]
for i in districts:
    a = new[new['propertyCode'].str.contains(i, na=True)]
    sim = np.sum(a['annualEnergy'] )
    epc = np.sum(a['EPC'])
    ape = np.abs((sim-epc)/epc)
    APE.append(ape)
    
np.mean(APE)
len(districts)

zipcode = new['zipcode'].unique()

APE =[]
for i in zipcode:
    a = new[new['zipcode']==i]
    sim = np.sum(a['annualEnergy'] )
    epc = np.sum(a['EPC'])
    ape = np.abs((sim-epc)/epc)
    APE.append(ape)
    
np.mean(APE)
len(zipcode)

sim = np.sum(new['annualEnergy'] )
epc = np.sum(new['EPC'])
APE = np.abs((sim-epc)/epc)
np.mean(APE)*100






a = np.sum(new['hourlyEnergy'], axis = 0)
b = np.sum(new['SH'], axis = 0)
plt.plot(a)
plt.plot(b)
plt.show()

a = np.sum(new['DHW'])
pd.DataFrame(a).to_excel('results/borlangeResults-calibrated-epc-hourlyEnergyDHW.xlsx')



new.to_excel('results/borlangeResults-uncalibrated-epc-v2.xlsx')

df.to_csv('results/borlangeResults-calibrated-complete.csv')
#t = pd.read_csv(epw,sep=',', skiprows = 8, header = None ).weatherData[6]




#VISUALIZATION OF RESULTS
#----------------------------




Visualization.plot(new, 'annualEnergy')



    
    
"""    

import pyproj


DHUse = pd.read_excel('X:/UBEM/data/GIS_Borlange/energy_use/EL_DH_month_v3_borlange.xlsx',
                      sheet_name='DH_month_clean')
DHUse  = DHUse.dropna(subset=[ 'Latitude'])
transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:3006")

coordinatesX = []
coordinatesY = [] 
for i in range (len(DHUse)):
    x,y = transformer.transform(DHUse.Latitude[i], DHUse.Longitude[i])  
    coordinatesX.append(int(y))
    coordinatesY.append(int(x))
    
DHUse = DHUse.drop (['Latitude','Longitude'], axis = 1)
coordinates = pd.DataFrame({'x':coordinatesX,'y':coordinatesY})
DHUse['x'] = coordinates.x
DHUse['y'] = coordinates.y

DHUse =  gpd.GeoDataFrame(DHUse, geometry=gpd.points_from_xy(DHUse.x, DHUse.y))
DHUse = DHUse .set_crs('EPSG:3006')  




validation_df = gpd.sjoin(df, DHUse,how='inner', op = 'intersects')
validation_df = validation_df.reset_index(drop=True)

validation_df = validation_df[validation_df['IdFastBet']!='0']

validation_df = validation_df.drop_duplicates(subset = 'geometry')
validation_df = validation_df.reset_index(drop=True)



validation_df = validation_df[validation_df['IdFastBet']!='ALF 10']
validation_df = validation_df[validation_df['IdFastBet']!='BYGGHERREN 2']
validation_df = validation_df[validation_df['IdFastBet']!='RÖKEN 4']
validation_df = validation_df[validation_df['IdFastBet']!='LINTEGEN 2']
validation_df = validation_df[validation_df['IdFastBet']!='ROSEN 1']
validation_df = validation_df[validation_df['IdFastBet']!='KLÖVERVALLEN 2']
validation_df = validation_df[validation_df['IdFastBet']!='URD 3']
validation_df = validation_df[validation_df['IdFastBet']!='SKULD 1']
validation_df = validation_df[validation_df['IdFastBet']!='HEIMER 9']
validation_df = validation_df[validation_df['IdFastBet']!='LAXEN 4']
validation_df = validation_df[validation_df['IdFastBet']!='IDKERBERGET 6:21']
validation_df = validation_df.reset_index(drop=True)


gis = gis.drop_duplicates(subset = 'geometry')
gis = gis.reset_index(drop=True)

prop = validation_df['IdFastBet'].unique()

newData = gpd.GeoDataFrame()
for i in prop:
    
    validationdat = validation_df[validation_df['IdFastBet'] == i]
    gisdat = gis[ gis['IdFastBet'] == i ]
    
    if len (validationdat)== len(gisdat):
        newData = newData.append(validationdat)
    else:
         newData = newData.append(gisdat)
        
newData = newData.fillna(0)
newData = newData.reset_index(drop = True).set_

crs('EPSG:3006')   

"""


