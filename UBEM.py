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





""" Initializing the simulation tool EnergyPlus """

# Calls the idd (EnergyPlus exe file)
iddfile = "C:/EnergyPlusV9-2-0/Energy+.idd"

# Initializes the idf file processing.
IDF.setiddname(iddfile)


""" Importing the input parameters """

# EnergyPlus weather file.
epw = "inputs/SWE_Stockholm.Arlanda.024600_IWEC.epw"


# Reads the input data for buildings.
df = pd.read_csv('inputs/exampleData.csv')
# Converts the data frame to a geodataframe
df['geometry'] = df['geometry'].apply(wkt.loads)
df = gpd.GeoDataFrame(df, crs='epsg:3006')
df = df.drop('Unnamed: 0', axis = 1)



# For the example file, Atemp = footprint area
gis = df


# Input parameters from a user defined text file.
parameters = pd.read_csv('inputs/parameters.txt', sep = ',', header = 'infer', 
                         encoding= 'ANSI')

# Reads the occupancy inputs.
occupancyInputs = pd.read_csv('inputs/occupancyInputs.csv', sep=';',low_memory=False)

""" Initializing the input parameters """

# Hot and cold water temperatures for domestic hot water use.
hotWaterTemp = parameters.hotWaterTemp[0]
coldWaterTemp = parameters.coldWaterTemp[0]

# Infiltration
infiltration = pd.read_csv('archetypesCalibrated.txt').infiltration


""" Initializing the occupancy profiles """

def leap_year(year):
    """
    Checks if the given year is leap year
    """
    if ((year % 400 == 0) or (year % 100 == 0) and (year % 4 ==0)):
        return 1
    else:
        return 0


# Finds the first day of the year, i.e., Mon, Tue, ...
firstDayOfYear = pd.read_csv(epw,sep=',',skiprows = 7,
                             low_memory=False).columns[4]

# Finds if the simulation year is a leap year
year = int(pd.read_csv(epw,sep=',',skiprows = 8, low_memory=False).columns[0])
leapYear = leap_year(year)

# Makes the occupancy profile for the two main types of buildings.
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

"MULTIPROCESSING SIMULATION RUN FOR THE DATASET"


# Removes the output
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
        
        SIMULATIONOUTPUT = []
        ARCHETYPE = []
        for i in range (len(df)):           
            print ('Building',i,'/',len(df))
            try:
                buildDat = df.iloc[i:i+1].reset_index(drop=True)
                idx = i

                buildingType = buildDat.buildingType[0] # Detailed type of building
                mainType = Archetype.building_type(buildingType) # Main type of building
                buildingYear = buildDat.constructionYear[0] # Construction year of building
                arch = Archetype.archetype(mainType, buildingYear)
                ARCHETYPE.append(arch)


                floorHeight = 2.5
                buildingId = buildDat.buildingId[0]
                buildingPolygon= Polygon (buildDat.geometry[0])            
                basementInfo = buildDat.heatedBasement[0]    
                buildingFloor = buildDat.heatedFloors[0] #On ground floors              

                if buildingFloor != 0:
                    buildingHeight = (buildingFloor*floorHeight) + (1 if basementInfo!=0 else 0)
                    
                else:
                    buildingHeight = buildDat.buildingHeight[0]
                    buildingFloor = np.round(buildingHeight/2.8)  
                

                buildingArea = buildDat.area[0]
                propertyCode = buildDat.propertyCode[0]

                windowAreaBBR = np.round(buildingArea * buildingFloor * 0.1)
                perimeter = 0
                x,y = buildingPolygon.exterior.xy
                for j in range(len(x)-1):
                    line = LineString([(x[j],y[j]),(x[j+1],y[j+1])]).length
                    if line>2:
                        perimeter += line
                        
                wwr = windowAreaBBR/(perimeter * buildingFloor * floorHeight)
    
                
                material_idf = IDF("archetypesCalibrated/Archetype%d.idf" %arch)
                                   
                heatRecovery = 1 if buildDat.ventilationType[0] =='FTX' else 0
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
                
                SIMULATIONOUTPUT.append(Simulation.simulation (idf ,basementInfo))
    
                remove()
                
            except:
                SIMULATIONOUTPUT.append([0,0,0,0,0])
            
             
    t2 = time()
    print('SIMULATION IS DONE!')
    print('                   ')
    print("----- Running time:", (t2-t1)//60, ' minutes and', np.round((t2-t1)-60*(t2-t1)//60,2)*60, ' seconds')
    print("----- Running time per building:", np.round((t2-t1)/len(df),2), ' seconds')


# Analysis of the results

SIMULATIONOUTPUT = pd.DataFrame(SIMULATIONOUTPUT)

SH = []
DHW = []
El = []
annualSH = []
annualDHW = []
annualELHousehold = []

for i in range(len(SIMULATIONOUTPUT)):
    El.append(SIMULATIONOUTPUT[2][i])
    SH.append(SIMULATIONOUTPUT[3][i])
    DHW.append(SIMULATIONOUTPUT[4][i])
    annualDHW.append(np.sum(SIMULATIONOUTPUT[4][i]))
    annualSH.append(np.sum(SIMULATIONOUTPUT[3][i]))
    annualELHousehold.append(np.sum(SIMULATIONOUTPUT[2][i]))

    
    
df['archetype'] = ARCHETYPE  
df['annualSH'] = annualSH
df['annualDHW'] = annualDHW
df['annualELHousehold'] = annualELHousehold

df.to_csv('results/simulationResults.csv')
