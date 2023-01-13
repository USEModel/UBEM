# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 17:19:30 2021

@author: fatjo876
"""
import pandas as pd

class Archetype():
    def __init__(self, buildingType, buildingYear):
        self.buildingType = buildingType
        self.buildingYear = buildingYear
        
    def archetype(buildingType,buildingYear):
        """
        Reads information of pre-defined building archetypes and labels the buildings accordingly.
            
        parameters
        ----------
        buildingType: str
            Type of building given in the GIS file.
        
        buildingYear:int
            Construction year of the building
                
        output
        ------
        int
            Given category of the building based on its archetype. 
        """ 
        
        # Read the list of predefined archetypes. 
        listOfArchetypes = pd.read_csv('archetypesCalibrated.txt',sep = ",", 
                                       encoding = 'ANSI', header='infer')
        
        # Filter the list of archetypes based on type and construction year of the building.
        archetype = listOfArchetypes[(listOfArchetypes['buildingType'] == buildingType) &
                                     (listOfArchetypes['buildingYearFrom']< buildingYear) &
                                      (buildingYear <= listOfArchetypes['buildingYearTo'])]
        
        # Get the category of the building based on the filtered list 
        arch = archetype['archetype'].values[0]
       
        return arch
    
    def building_type (buildingType):
        """
        Returns the main type of buildings, i.e., Apartment or House.
            
        parameters
        ----------
        buildingType: str
            Type of building given in the GIS file.
                
        output
        ------
        str: 
            Given type of buildings: 'Apartment', 'House'
        """         
            
        #if buildingType == 'Residential;MultifamilyBuilding':
        if buildingType == 'Bostad; Flerfamiljshus':   
            return 'Apartment'
        else:
            return 'House'
            
            
            
