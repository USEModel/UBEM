# -*- coding: utf-8 -*-
"""
Created on Fri May  7 16:25:09 2021

@author: fatjo876
"""

from eppy.modeleditor import IDF
import pandas as pd
from io import StringIO


class baseIDF:
    
    def __init__(self, epw, version): 
        self.epw = epw
        self.version = version

    def blank_idf(epw, version = 9.2):
        """
        Creates a blank IDF.
            
        parameters
        ----------
        epw: epw
            EnergyPlus weather file.
        version: float
            Version of the EnergyPlus software.
                
        output
        ------
        idf
            An empty idf file. 
        """
        
        idftxt = "" # Empty string.
        fhandle = StringIO(idftxt) # Handles the empty string.
        idf = IDF(fhandle, epw) # Converts the empty string to idf.
        
        # Specifies and adds the version of energyplus to the empty idf.
        idf.newidfobject('VERSION',
                         Version_Identifier = version) 
            
        return idf
    
  
        
    def simulation_parameters(idf, zoneSizing = 'No', systemSizing = 'No', 
                              plantSizing = 'No', epwRunPeriod = 'Yes'):
        """
        Sets up the simulation parameters for sizing systems 
        and modeling building.
        
        parametrs
        ----------
        idf
        zoneSizing: str
        systemSizing: str
        plantSizing: str
            
        output
        ------
        idf
        """
        
        idf.newidfobject("SIMULATIONCONTROL",
                         Do_Zone_Sizing_Calculation = zoneSizing,
                         Do_System_Sizing_Calculation = systemSizing,
                         Do_Plant_Sizing_Calculation = plantSizing,
                         Run_Simulation_for_Sizing_Periods = 'No',
                         Run_Simulation_for_Weather_File_Run_Periods = epwRunPeriod
                         ) 
        
        idf.newidfobject('BUILDING', 
                         Name = 'Building',
                         North_Axis = 0,
                         Terrain = 'City',
                         Solar_Distribution = 'FullExterior')
        
        return idf
    
    
    def simulation_period(idf, timeStep = 6, startMonth = 1, startDay = 1, 
                          endMonth = 12, endDay = 31, firstDayWeek = 'Monday'):
        
        """ 
        Sets the simulation time and time step.
        
        parameters
        ----------
        idf
        
        timeStep: 1< int <60
            Sub-hour simulation time steps. 
            
        startMont: 1< int <12
            Begin month of the simulation.
            
        startDay: 1< int <31
            Begin day of the simulation.
        
        endMonth: 1< int <12
            End month of the simulation.
        
        endDay: 1< int <31
            End day of the simulation.
        
        firstDayWeek: str
            Begin day of the week.
            
        output
        ------
        idf
        """     
        
        idf.newidfobject('RUNPERIOD',
                         Name = 'RUNPERIOD',
                         Begin_Month = startMonth,
                         Begin_Day_of_Month = startDay,
                         End_Month = endMonth,
                         End_Day_of_Month = endDay,
                         Day_of_Week_for_Start_Day = firstDayWeek
                         )
        
        idf.newidfobject('TIMESTEP',
                         Number_of_Timesteps_per_Hour = timeStep)
        return idf
        
    
    def site_location(idf, epw):
        """ 
        Sets up information of the location using the weather data file.
        
        parameters
        ----------
        idf
        
        epw:
            EnergyPlus weather data file.
            
        output
        ------
        idf
        """
        
        location = pd.read_csv(epw , nrows=0) # Reads the weather data file.
        
        city = location.columns[1] # City or location of the site.
        latitude = location.columns[6] # Latitude of the site.
        longitude = location.columns[7] # Longitude of the site.
        timeZone = location.columns[8] # Time zone.
        elevation = location.columns[9] # Elevation of the site.
        
        
        idf.newidfobject('SITE:LOCATION',
                        Name = city,
                        Latitude = latitude,
                        Longitude = longitude,
                        Time_Zone = timeZone,
                        Elevation = elevation)
            
        return idf
    
    

    
    def simulation_output(idf):
        """ 
        Chooses the simulation output parameters.
        
        parameters
        ----------
        idf   
        
        output
        ------
        html, csv:       
            Annual as well as hourly results for heat demand in buildings.
        """
    
        idf.newidfobject('OUTPUT:VARIABLEDICTIONARY',
                         Key_Field = 'Regular')
        
        idf.newidfobject('OUTPUT:TABLE:SUMMARYREPORTS',
                         Report_1_Name = 'AllSummary')
        
        idf.newidfobject('OUTPUTCONTROL:TABLE:STYLE',
                         Column_Separator= 'comma')
    
        idf.newidfobject('OUTPUT:METER',
                         Key_Name= 'Heating:DistrictHeating',
                         Reporting_Frequency = 'Hourly')  

        idf.newidfobject('OUTPUT:METER',
                         Key_Name= 'WaterSystems:DistrictHeating',
                         Reporting_Frequency = 'Hourly')  
        
        idf.newidfobject('OUTPUT:METER',
                         Key_Name= 'Electricity:Building',
                         Reporting_Frequency = 'Hourly') 
        
        idf.newidfobject('OUTPUT:VARIABLE',
                         Variable_Name= 'Zone Mean Air Temperature',
                         Reporting_Frequency = 'Hourly') 
        
        idf.newidfobject('OUTPUT:VARIABLE',
                         Variable_Name= 'Site Outdoor Air Drybulb Temperature',
                         Reporting_Frequency = 'Hourly')        
        
        return idf
      
