# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 08:44:00 2022

@author: fatjo876
"""

import pandas as pd
import numpy as np


from base_idf import baseIDF
from zoning import oneZone
from hvac import HVAC
from geometry import Geometry

from occupancy import Occupancy
from adjacency import Adjacency
from shading import Shading


class Simulation:
    def __init__(self, idf, buildingPolygon, buildingArea, buildingHeight, buildingId,
                 basementInfo, epw, wwr, 
                 material_idf,gis , hotWaterTemp, coldWaterTemp, 
                 maxFlowHotWater, buildingMainType, 
                 heatRecovery, heatRecoveryEffect, infFlow, df, idx, propertyCode):
        
        self.idf = idf
        self.buildingPolygon = buildingPolygon
        self.buildingArea = buildingArea
        self.buildingHeight = buildingHeight
        self.buildingId = buildingId
        self.epw = epw
        self.wwr = wwr
        self.material_idf = material_idf
        self.df = df
        self.hotWaterTemp =  hotWaterTemp
        self.coldWaterTemp = coldWaterTemp
        self.maxFlowHotWater = maxFlowHotWater
        self.buildingMainType = buildingMainType
        self.basementInfo = basementInfo
        self.heatRecovery = heatRecovery
        self.heatRecoveryEffect = heatRecoveryEffect 
        self.infFlow = infFlow
        self.gis = gis
        self.idx = idx
        self.propertyCode = propertyCode

        
    def building_idf (buildingPolygon, buildingArea, buildingHeight, buildingId, 
                      basementInfo,epw, wwr, material_idf, df,
                      hotWaterTemp, coldWaterTemp, maxFlowHotWater,
                      buildingMainType, heatRecovery, heatRecoveryEffect, infFlow, 
                      gis, idx, propertyCode):
        """Creates a complete IDF from all the input variables and functions.
            
        parameters
        ----------
        buildingPolygon: Shapely.Polygon
            Building footprint from GIS data.
            
        buildingArea: int
            Calculated area of the building.
            
        buildingHeight: int
            Estimated height of the building from GIS data.
            
        buildingId:str
            Unique ID that is given to each building found in the GIS data.
            
        epw: epw
            The energyPlus weather file.
            
        wwr: float
            Window oto wall ratio of buildings.
            
        material_idf: idf
            Building construction and material found for each archetype.
        
        basement_idf: idf
            Predefined specifications of the basement properties.
        
        gis: gpd.GeoDataFrame
            GIS dataset
            
        buildingMainType: str
            Main type of building, i.e., house or apartment.
            
        basementInfo: int
           Basement info from the EPC (number of underground floor).
           
        infFlow: int
            Infiltration flow rate (ACH)
                
        output
        ------
        idf
            Completed idf for simulation. 
        """    
        # Modify the geometry rules of the building polygon.
        buildingPolygon = Geometry.global_geometry(buildingPolygon)
        
        #Activate the idf of the basement.
        basement = 1 if basementInfo > 0 else 0

        # Initialize the idf file.
        idf = baseIDF.blank_idf(epw)
        
        # Add the main simulation parameters.
        baseIDF.simulation_parameters(idf)
        baseIDF.site_location(idf,epw)
        baseIDF.simulation_period(idf)
        baseIDF.simulation_output(idf)
        
        # Specify the geometry rules.
        Geometry.global_geometry_rules (idf)
        
        # Write the idf for a single-zone model.
        oneZone.zone (idf)
        
        # Find the adjacent buildings
        adj = Adjacency.adjacent_polygons(buildingPolygon, buildingId, df,gis)

        # Define the idf for construction and surfaces.
        surfaceidf = oneZone.onezone_building_surfaces(buildingPolygon, 
                                                       buildingHeight, 
                                                       basement, wwr, adj)
        

        
        # Copy the information from "surfaceidf" to the idf file.
        for s in range (len(surfaceidf.idfobjects["BUILDINGSURFACE:DETAILED"])):
            idf.copyidfobject(surfaceidf.idfobjects["BUILDINGSURFACE:DETAILED"][s])
      
        for w in range (len(surfaceidf.idfobjects["FENESTRATIONSURFACE:DETAILED"])):
            idf.copyidfobject(surfaceidf.idfobjects["FENESTRATIONSURFACE:DETAILED"][w])   
        

                    
        # Copy the construction and material from pre-defined archetype idfs.
        for m in range (len(material_idf.idfobjects["Material"])):
            idf.copyidfobject(material_idf.idfobjects["Material"][m]) 
            
        for ma in range (len(material_idf.idfobjects["MATERIAL:AIRGAP"])):
            idf.copyidfobject(material_idf.idfobjects["MATERIAL:AIRGAP"][ma])         
            
            
        for mgl in range (len(material_idf.idfobjects["WindowMaterial:SimpleGlazingSystem"])):
            idf.copyidfobject(material_idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][mgl])
            
        for c in range (len(material_idf.idfobjects["CONSTRUCTION"])):
            idf.copyidfobject(material_idf.idfobjects["CONSTRUCTION"][c])
            
            
        for mgl in range (len(material_idf.idfobjects["WINDOWMATERIAL:GLAZING"])):
            idf.copyidfobject(material_idf.idfobjects["WINDOWMATERIAL:GLAZING"][mgl])
       
        for mgs in range (len(material_idf.idfobjects["WINDOWMATERIAL:GAS"])):
            idf.copyidfobject(material_idf.idfobjects["WINDOWMATERIAL:GAS"][mgs])              
        
        # Add information of the HVAC system to the idf file.
        HVAC.ventilation(idf, 0.5, 'Exhaust', 'ZONE') 
        HVAC.infiltration(idf, infFlow,'ZONE')
        HVAC.ventilation_schedule(idf)
        
        # Activate the heat reacovery in the system
        heatRecovery = 'Sensible' if  heatRecovery == 1 else 'None'
        
        # Add the heating system
        HVAC.ideal(idf, heatRecovery, heatRecoveryEffect, 'ZONE')
        HVAC.ideal_schedule(idf, 21)

        
        # Copy the information from the predefined basement idf to the idf file.
        if basement == 1:
            oneZone.zone_basement (idf)
            HVAC.ventilation(idf, 0.5, 'Exhaust', 'BASEMENT') 
            HVAC.infiltration(idf, infFlow, 'BASEMENT')
            HVAC.ideal(idf, heatRecovery, heatRecoveryEffect, 'BASEMENT')            
            
            
        # Add the infomation of the occupancy, gain and DHW to the idf file
        Occupancy.people(idf,buildingArea, buildingHeight, buildingMainType)
        Occupancy.equipment (idf, buildingArea, buildingHeight, buildingMainType)
        Occupancy.dhw (idf, buildingArea, buildingHeight, hotWaterTemp, 
                       coldWaterTemp, maxFlowHotWater, buildingMainType)
        
        # Add shading surfaces in case there is a shading building
        shading = Shading.densification(df, propertyCode)
        if shading == 1:
            print('shading')
            gdf, d  = Shading.shading(df, gis)
            idfShading = Shading.shading_idf( gdf, d)
            for obj in range(len(idfShading.idfobjects['SHADING:BUILDING:DETAILED'])):
                idf.copyidfobject(idfShading.idfobjects['SHADING:BUILDING:DETAILED'][obj])
        
        return idf


    def simulation (idf, basementInfo):
        """
        Runs the idf file and reports the results in the output.
            
        parameter
        ----------
        idf:
            Completed idf file.
                
        output
        ------       
        spaceHeat: string
            Hourly space heating demand.
        
        hotWater:
            Hourly energy demand for DHW
        
        heatDemand:
            Total houlry heat demand . 
        """ 
        # Runs the idf file using eppy.run() function.        
        idf.run()
        
        b = 1 if basementInfo > 0 else 0

        # Reads hourly results of the space heating.
        fout = 'eplusout.eso'
        

        hourly = pd.read_csv(fout , sep = "[,\n]", skiprows=15+b,
                             skipfooter = 2, usecols=[0,1], header=None,
                             engine='python')
        
        ambientTemperature = np.array(hourly[hourly[0]==7][1])
        roomAirTemperature = np.array(hourly[hourly[0]==81][1])
        
        electricity = np.array(hourly[hourly[0]==22][1])
        electricity  = electricity /3600000  # kWh/h       
        
        spaceHeat = np.array(hourly[(hourly[0]==295)|(hourly[0]==231)][1])
        spaceHeat = spaceHeat/3600000  # kWh/h
        
        # Reads the hourly hot water use.
        hotWater = np.array(hourly[(hourly[0]==457)|(hourly[0]==391)][1])
        hotWater = hotWater/3600000  # kWh/h       
        
        
        return ambientTemperature, roomAirTemperature, electricity, spaceHeat, hotWater

