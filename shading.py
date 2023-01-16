# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 13:00:38 2022

@author: fatjo876
"""

from shapely import affinity
from shapely.geometry import LineString
import io
from eppy.modeleditor import IDF
import numpy as np
import geopandas as gpd

class Shading:
    def __init__(self, propertyCode, df, gis, idx):
        self.propertyCode = propertyCode
        self.df = df
        self.gis = gis
        self.idx = idx


    def densification(df, propertyCode):

        building = df[df['propertyCode'] == propertyCode].reset_index(drop=True)
        
        propertyArea = building['propertyArea']
        
        if propertyArea[0]>0:
            buildingArea = building.area
            buildingHeight = building['buildingHeight']
            bcr = np.sum(buildingArea)/np.sum(propertyArea)
            far = np.sum( buildingArea* np.round(buildingHeight/2.8))/np.sum(propertyArea)
            
            if far>1 and bcr>0.3:
                return 1
            else:
                return 0
        else:
            return 0
             
        
    def shading(df, gis):
        

        
        #shadingDistance = df['modifiedHeight'][0]/np.tan(np.radians(15))
        shadingDistance = 100
        building = df
        gdf = building.geometry.values
        line = LineString([(gdf.centroid.x[0],gdf.centroid.y[0]),
                           (gdf.centroid.x[0]+shadingDistance,gdf.centroid.y[0])])
        
        # Rotate i degrees CCW from origin at point (step 10°)
        radii= [affinity.rotate(line, i, (gdf.centroid.x[0],
                                          gdf.centroid.y[0])) for i in range(0,360,5)]
        #mergedradii = cascaded_union(radii)
        radius = gpd.GeoDataFrame()
        radius['geometry']= radii
        radius = radius.set_crs('EPSG:3006')

        
        shading = gpd.GeoDataFrame()
        for i in range(len(radius)):
            
            intersect = gpd.overlay(radius.iloc[i:i+1],gis,how='intersection')           
            intersect = intersect.drop_duplicates(subset = 'buildingId')
            
            
            shadingObstacle = gpd.GeoDataFrame()
            for b in intersect.index:
                a = gis[gis['buildingId'] == intersect.buildingId[b]]
                shadingObstacle = shadingObstacle.append(a)
            

            distance = []
            for k in shadingObstacle.index:
               distance.append( building.geometry[0].distance(shadingObstacle.geometry[k]))
   
            shadingObstacle['distance']=distance
            shadingObstacle = shadingObstacle[shadingObstacle['distance']>=0.2]
            
            if len(shadingObstacle)>0:

                shadingObstacle = shadingObstacle[shadingObstacle['distance']==np.min(shadingObstacle['distance'])]
                shadingObstacle = shadingObstacle.reset_index(drop=True)
                
                shading = shading.append(shadingObstacle)
                
        shading = shading.drop_duplicates(subset=['buildingId'])    
        shading = shading.reset_index(drop=True)
        
        
        
        for i in shading.index:
            shadingGeo = shading.geometry[i]
            shadingHeight = shading.buildingHeight[i]
            shadingPolygon =str("shadingPolygon%d"%i)
            shadingH = str("shadingHeight%d"%i)
        
            building[shadingPolygon] = shadingGeo
            building[shadingH]= shadingHeight
                
        return building, len(shading)



    def shading_idf(building, d):
        shade = "" 
        for i in range(d):
            x,y = building['shadingPolygon%d'%i][0].exterior.xy
            z0 = 0
            z1 = building['shadingHeight%d'%i][0]
            
            
            shade += ('SHADING:BUILDING:DETAILED,'+'\n'+
                      str('shadingBuilding%d'%i)+',\n'+
                      ', \n'+ 
                      'autocalculate,'+'\n')
            
            for j in range(len(x)-2):

                                      
                shade+= (str(x[j])+',\n' + str(y[j]) + ',\n' + str(z0) + ',\n' +
                         str(x[j+1])+',\n' + str(y[j+1]) + ',\n' + str(z1) + ',\n' +
                         str(x[j+1])+',\n' + str(y[j+1]) + ',\n' + str(z1) + ',\n' +
                         str(x[j])+',\n' + str(y[j]) + ',\n' + str(z0) + ',\n' )
                
            shade+= (str(x[-2])+',\n' + str(y[-2]) + ',\n' + str(z0) + ',\n' +
                    str(x[-1])+',\n' + str(y[-1]) + ',\n' + str(z1) + ',\n' +
                    str(x[-1])+',\n' + str(y[-1]) + ',\n' + str(z1) + ',\n' +
                    str(x[-2])+',\n' + str(y[-2]) + ',\n' + str(z0) + ';\n' )               
                
            fhandle = io.StringIO(shade) 
            idfShading = IDF(fhandle) 
       
        return idfShading

