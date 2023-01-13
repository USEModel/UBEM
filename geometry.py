# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 09:57:15 2021

@author: fatjo876
"""

from shapely.geometry.polygon import Point, Polygon
import itertools

class Geometry:
    def __init__(self, polygon, idf):
        self.polygon = polygon
        self.idf = idf

    def global_geometry_rules(idf):
        
        """
        Defines the global geometry rule of the idf file.
        
        parameters
        -------
        idf
               
        output
        ------
        idf
        """        
        
        idf.newidfobject ('GLOBALGEOMETRYRULES',
                          Starting_Vertex_Position = 'LowerRightCorner',
                          Vertex_Entry_Direction = 'Counterclockwise',
                          Coordinate_System = 'Relative')
    
        return idf

        
    def global_geometry(polygon):
        
        """
        Reconstructs the polygon according to the geometry rules specified 
        by EnergyPlus. 
        
        parameters
        ----------
        polygon: shapely polygon
            Surfaces of the building.
        
        output
        ------
        polygon: shapely polygon
           Reconstructed surfaces of the building.
        """
        
        # Get x and y coordinates of the polygon.
        x, y = polygon.exterior.xy
        
        # Find the lowest point of a polygon, based on min (y).
        for a, b in zip(x,y):
            if b == min(y):
                firstVertex = Point(a,b)
            
                
        # Reconstruct the polygon counter clockwise starting from the lowest point.
        perimeter = polygon.exterior.coords
        newCoordinates = []
        twoRounds = itertools.chain(perimeter, perimeter)
        for v in twoRounds:
            if Point(v) == firstVertex:
                newCoordinates.append(v)
                while len(newCoordinates) < len(perimeter):
                    newCoordinates.append(next(twoRounds))
                break
            
        polygon = Polygon(newCoordinates)   
        
        # Simplify the polygon in case of repeated points.
        polygon = polygon.simplify(0.5, preserve_topology= True)
      
        return polygon
