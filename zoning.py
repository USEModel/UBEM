# -*- coding: utf-8 -*-
"""
Created on Sun May  9 17:40:52 2021

@author: fatjo876
"""

from shapely.geometry.polygon import Polygon
import math
from eppy.modeleditor import IDF
from shapely.geometry import Point, LineString
import io
import numpy as np


def external_wall(x0,x1,y0,y1,z0,z1, i):
    """
    Writes the information of the external walls.
    
    parameters
    ----------
    x0,x1,y0,y1,z0,z1: int
        The vertices of the wall as illustrated below:
    
          (x1,y1,z1)                (x0,y0,z1)
                    * * * *  * * * *
                    *              *
                    *              *
                    *              *
                    * * * *  * * * *
          (x1,y1,z0)                (x0,y0,z0)
  
    i: int
        Number of external wall in the building
     
    output
    ------
    str
    """
    
    wallVertices = 4
    wall = ""        
    wall += ('BUILDINGSURFACE:DETAILED,'+'\n'+
             'Wall'+str(i)+',\n'+              #!- Name
             'Wall, \n'+                       #!- Surface Type
             'Exterior Wall, \n'+              #!- Construction Name
             'ZONE'+',\n'+                     #!- Zone Name
             'Outdoors, \n'+                   #!- Outside Boundary Condition
             ', \n'+                           #!- Outside Boundary Condition Object
             'SunExposed, \n'+                 #!- Sun Exposure
             'WindExposed, \n'+                #!- Wind Exposure
             ',\n' +                           #!- View Factor to Ground
             str(wallVertices)+',\n')         #!- Number of Vertices
    
    # Vertices of the wall.
    wall += (str(x0)+',\n' + str(y0) + ',\n' + str(z0) + ',\n' +
             str(x0)+',\n' + str(y0) + ',\n' + str(z1) + ',\n' +
             str(x1)+',\n' + str(y1) + ',\n' + str(z1) + ',\n' +
             str(x1)+',\n' + str(y1) + ',\n' + str(z0) + ';\n' )
    
    return wall 

def adiabatic_wall(x0,x1,y0,y1,z0,z1, i):
    """
    Writes the information of the adjacent walls.
    Assumed to be adiabatic.
    
    parameters
    ----------
    x0,x1,y0,y1,z0,z1: int 
        The vertices of the external walls.
    i: int
        Number of external walls in the building
      
    output
    ------
    str
    """
    
    wallVertices = 4
    wall = ""        
    wall += ('BUILDINGSURFACE:DETAILED,'+'\n'+
             'Wall'+str(i)+',\n'+              #!- Name
             'Wall, \n'+                       #!- Surface Type
             'Exterior Wall, \n'+              #!- Construction Name
             'ZONE'+',\n'+                     #!- Zone Name
             'Adiabatic, \n'+                   #!- Outside Boundary Condition
             ', \n'+                           #!- Outside Boundary Condition Object
             'NoSun, \n'+                 #!- Sun Exposure
             'NoWind, \n'+                #!- Wind Exposure
             ',\n' +                           #!- View Factor to Ground
             str(wallVertices)+',\n')         #!- Number of Vertices
    # Vertices of the wall.
    wall += (str(x0)+',\n' + str(y0) + ',\n' + str(z0) + ',\n' +
             str(x0)+',\n' + str(y0) + ',\n' + str(z1) + ',\n' +
             str(x1)+',\n' + str(y1) + ',\n' + str(z1) + ',\n' +
             str(x1)+',\n' + str(y1) + ',\n' + str(z0) + ';\n' )
    
    return wall 

def external_win(x0, x1, y0, y1, z0, z1, i, basement):
    """
    Writes the information of the external windows.
    
    parameters
    ----------
    x0,x1,y0,y1,z0,z1: int
        The vertices of the windows on external walls.
 
    i: int
        Number of external windows in the building.
       
    output
    ------
    str
    """
    
    winVertices = 4
    win = ""        
    win += ('FENESTRATIONSURFACE:DETAILED,'+'\n'+
            'Window'+basement+str(i)+',\n'+                  #!- Name
            'Window, \n'+                           # !- Surface Type
            'Exterior Window, \n'+                  # !- Construction Name
            'Wall'+basement+ str(i)+',\n'+                   # !-Building Surface Name
            ', \n'+
            ', \n'+
            ', \n'+
            ', \n'+
            str(winVertices)+',\n')

    win += (str(x0) + ',\n' + str(y0) + ',\n' + str(z0) + ',\n' +
            str(x0) + ',\n' + str(y0) + ',\n' + str(z1) + ',\n' +
            str(x1) + ',\n' + str(y1) + ',\n' + str(z1) + ',\n' +
            str(x1) + ',\n' + str(y1) + ',\n' + str(z0) + ';\n' )
    
    return win 



def roof(x,y,z):
    """
    Writes information of the external roof.
    
    Parameters
    ----------
    x,y,z: int
        The vertices of the external roof.
              
    output
    ------
    str
    """
    
    roofVertices = len(x)-1
    roof = ""
    roof += ('BUILDINGSURFACE:DETAILED,'+'\n'+
             'Roof'+',\n'+                      #!- Name
             'Roof, \n'+                        #!- Surface Type
             'Exterior Roof, \n'+               #!- Construction Name
             'ZONE'+',\n'+                      #!- Zone Name
             'Outdoors, \n'+                    #!- Outside Boundary Condition
             ', \n'+                            #!- Outside Boundary Condition Object
             'SunExposed, \n'+                  #!- Sun Exposure
             'WindExposed, \n'+                 #!- Wind Exposure
             ',\n' +                            #!- View Factor to Ground
             str(roofVertices)+',\n')          #!- Number of Vertices
       

    for i in range(roofVertices-1):
        roof += (str(x[i]) + ',\n '+
                 str(y[i]) + ',\n' +
                 str(z) + ',\n' )

    roof += (str(x[-2]) + ',\n' +
             str(y[-2]) + ',\n' +
             str(z) + ';\n' )
    
    return roof


def floor(x,y,z0,basement):
    """
    Writes information of the floor. 
    It is an external floor unless the building has a basement. 
    Then, the floor is regarded as the internal floor. 
    
    parameters
    ----------
    x,y: nd.array
    z: int
        The vertices of the floor.
              
    output
    ------
    str
    """
    
    floorVertices = len(x)-1
    
    floor = ""
    
    if basement == 1:
        
        floor += ('BUILDINGSURFACE:DETAILED,'+'\n'+
                  'Interior Floor'+ ',\n'+              #!- Name
                  'Floor, \n'+                          #!- Surface Type
                  'Interior Floor, \n'+                 #!- Construction Name
                  'ZONE'+',\n'+                         #!- Zone Name
                  'Surface, \n'+                        #!- Outside Boundary Condition
                  'Interior Ceiling'+',\n'+    #!- Outside Boundary Condition Object
                  'NoSun, \n'+                          #!- Sun Exposure
                  'NoWind, \n'+                         #!- Wind Exposure
                  ',\n' +                               #!- View Factor to Ground
                  str(floorVertices)+',\n')            #!- Number of Vertices      
        
        
    else:    
        floor += ('BUILDINGSURFACE:DETAILED,'+'\n'+
                  'Floor'+',\n'+                        #!- Name
                  'Floor, \n'+                          #!- Surface Type
                  'Exterior Floor, \n'+                 #!- Construction Name
                  'ZONE'+',\n'+                         #!- Zone Name
                  'Ground, \n'+                         #!- Outside Boundary Condition
                  ', \n'+                               #!- Outside Boundary Condition Object
                  'NoSun, \n'+                          #!- Sun Exposure
                  'NoWind, \n'+                         #!- Wind Exposure
                  ',\n' +                               #!- View Factor to Ground
                  str(floorVertices)+',\n')            #!- Number of Vertices     

        
    for i in range(floorVertices-1):
        floor += (str(x[i]) + ',\n' +
                  str(y[i]) + ',\n' +
                  str(z0) + ',\n')

    floor += (str(x[-2]) + ',\n' +
              str(y[-2]) + ',\n' +
              str(z0) + ';\n' )
    

    return floor


def basement_ceiling(x,y,z0):
    """
    Writes information of the basement ceiling.
    
    parameters
    ----------
    x,y: nd.array
    z0: int
        The vertices of the ceiling of the basement.
        
    output
    ------
    str
    """
    basementCeilingVertices = len(x)-1
    
    basementCeiling = ""    
    basementCeiling += ('BUILDINGSURFACE:DETAILED,'+'\n'+
                        'Interior Ceiling'+',\n'+       #!- Name
                        'Ceiling, \n'+                           #!- Surface Type
                        'Interior Ceiling, \n'+                  #!- Construction Name
                        'BASEMENT,\n'+                           #!- Zone Name
                        'Surface, \n'+                           #!- Outside Boundary Condition
                        'Interior Floor'+', \n'+                 #!- Outside Boundary Condition Object
                        'NoSun, \n'+                             #!- Sun Exposure
                        'NoWind, \n'+                            #!- Wind Exposure
                        ',\n' +                                  #!- View Factor to Ground
                        str(basementCeilingVertices)+',\n')               #!- Number of Vertices
        
    for i in range(basementCeilingVertices-1):
        basementCeiling += (str(x[i]) + ',\n' +
                            str(y[i]) + ',\n' +
                            str(z0) + ',\n' )

    basementCeiling += (str(x[-2]) + ',\n' +
                        str(y[-2]) + ',\n' +
                        str(z0) + ';\n' )
    
    return basementCeiling

    
def basement_floor(x,y,zb):
    """
    Writes information of the basement external floor.
    
    parameters
    ----------
    x,y: nd.array
    zb: int
        The vertices of the ceiling of the basement.
              
    output
    ------
    str
    """
    basementFloorVertices = len(x)-1
    
    basementFloor = ""
    basementFloor += ('BUILDINGSURFACE:DETAILED,'+'\n'+
                       'Exterior Floor, \n'+                #!- Name
                       'Floor, \n'+                         #!- Surface Type
                       'Exterior Floor Basement, \n'+                #!- Construction Name
                       'BASEMENT, \n'+                      #!- Zone Name
                       'Adiabatic, \n'+         #!- Outside Boundary Condition
                       ',\n'+                        #!- Outside Boundary Condition Object
                       'NoSun, \n'+                         #!- Sun Exposure
                       'NoWind, \n'+                        #!- Wind Exposure
                       ',\n' +                              #!- View Factor to Ground
                       str(basementFloorVertices)+',\n')           #!- Number of Vertices
    
    for i in range(basementFloorVertices-1):
        basementFloor += (str(x[i]) + ',\n' +
                          str(y[i]) + ',\n' +
                          str(zb) + ',\n' )

    basementFloor += (str(x[-2]) + ',\n' +
                       str(y[-2]) + ',\n' +
                       str(zb) + ';\n' ) 
    
    return basementFloor


def basement_adiabatic_wall(x0,x1,y0,y1,z0,zb,i):  
    """
    Writes the information of the basement external floor.
    
    parameters
    ----------
    x0,x1,y0,y1,z0,zb: int
        The vertices of the external walls of the basement.
    
    i: int
        Number of the walls.
              
    output
    ------
    str
    """

    basementWall = ""
    basementWall =('BUILDINGSURFACE:DETAILED,'+'\n'+
                    str('WallBasementAdiabatic'+ str(i))+ ',\n'+    #!- Name
                    'Wall, \n'+                             #!- Surface Type
                    'Exterior Wall Basement, \n'+                    #!- Construction Name
                    'BASEMENT, \n'+                         #!- Zone Name
                    'Adiabatic, \n'+            #!- Outside Boundary Condition
                    ',\n'+                            #!- Outside Boundary Condition Object
                    'NoSun, \n'+                            #!- Sun Exposure
                    'NoWind, \n'+                           #!- Wind Exposure
                    ',\n' +                                 #!- View Factor to Ground
                    '4,\n')                                 #!- Number of Vertices

    basementWall += (str(x0) + ',\n' + str(y0) + ',\n' + str(zb) + ',\n' +
                      str(x0) + ',\n' + str(y0) + ',\n' + str(z0) + ',\n' +
                      str(x1) + ',\n' + str(y1) + ',\n' + str(z0) + ',\n' +
                      str(x1) + ',\n' + str(y1) + ',\n' + str(zb) + ';\n' )
    
    return basementWall 
    
def basement_external_wall(x0,x1,y0,y1,z0,z1,i):  
    """
    Writes the information of the basement external floor.
    
    parameters
    ----------
    x0,x1,y0,y1,z0,zb: int
        The vertices of the external walls of the basement.
    
    i: int
        Number of the walls.
              
    output
    ------
    str
    """

    basementWall = ""
    basementWall =('BUILDINGSURFACE:DETAILED,'+'\n'+
                    str('WallBasement'+ str(i))+ ',\n'+    #!- Name
                    'Wall, \n'+                             #!- Surface Type
                    'Exterior Wall Basement, \n'+                    #!- Construction Name
                    'BASEMENT, \n'+                         #!- Zone Name
                    'Outdoors, \n'+            #!- Outside Boundary Condition
                    ',\n'+                            #!- Outside Boundary Condition Object
                    'SunExposed, \n'+                            #!- Sun Exposure
                    'WindExposed, \n'+                           #!- Wind Exposure
                    ',\n' +                                 #!- View Factor to Ground
                    '4,\n')                                 #!- Number of Vertices

    basementWall += (str(x0) + ',\n' + str(y0) + ',\n' + str(z0) + ',\n' +
                      str(x0) + ',\n' + str(y0) + ',\n' + str(z1) + ',\n' +
                      str(x1) + ',\n' + str(y1) + ',\n' + str(z1) + ',\n' +
                      str(x1) + ',\n' + str(y1) + ',\n' + str(z0) + ';\n' )
    
    return basementWall 


class oneZone:
    def __init__(self, buildingPolygon, buildingHeight, basement, wwr, adjacency):
        self.buildingPolygon = buildingPolygon
        self.buildingHeight= buildingHeight
        self.basement = basement
        self.wwr = wwr
        self.adjacency = adjacency

    def zone (idf):
        """
        Initializes the calculations of the thermal zone in EnergyPlus.
        
        parameters
        ----------
        idf
        
        output
        ----------
        idf  
        """
        idf.newidfobject('ZONE',
                         Name = 'ZONE',
                         Ceiling_Height = 'autocalculate',
                         Volume = 'autocalculate',
                         Floor_Area = 'autocalculate',
                         Part_of_Total_Floor_Area = 'yes')
        return idf
    
    def zone_basement(idf):
        """
        Initializes the calculations of the thermal zone of the basement in EnergyPlus.
        
        parameters
        ----------
        idf
        
        output
        ----------
        idf  
        """
        idf.newidfobject('ZONE',
                         Name = 'BASEMENT',
                         Ceiling_Height = 'autocalculate',
                         Volume = 'autocalculate',
                         Floor_Area = 'autocalculate',
                         Part_of_Total_Floor_Area = 'yes')
        return idf
        
        return idf
    
    def onezone_building_surfaces(buildingPolygon, buildingHeight, basement, wwr, adjacency):
        """
        Gets the geometry of the building and write in idf file for the building surfaces.
        
        parameters
        ----------
        buildingPolygon: shapely polygon
            Building footprint.
            
        buildingHeight: int
            Height of the building.
            
        basement: int
            Number of under ground floors from the EPC.
            
        wwr: int
            Window to wall ratio.
                  
        output
        ------
        idf
            An idf for building surfaces. 
        """
    
        height0 = 0 # Height of the ground level
        heightbExposed = 1 # height of basement exposed walls on ground
        heightbAdiabatic = -1.3 # height of the under ground floors.
        wwrb = wwr
        
        # Convert the geometry of the building polygon to arrays of x and y.
        x,y = buildingPolygon.exterior.xy 
            
        # Reverse the order for adjacent floor and ceiling
        xx,yy = x[::-1],y[::-1] 
        
        idftxt = ""   
        
        # If there is one or more adjacent walls.
        if len(adjacency) > 0:
            
            for i in range(len(x)-1):

                # Find the center of the walls.
                point = LineString([(x[i],y[i]),(x[i+1],y[i+1])]).centroid
                
                adj = []
                for j in range (len(adjacency)):
                    
                    p = Polygon(adjacency.geometry[j])
                    
                    # Calculate the distance of adjacency.
                    adj.append( point.distance(p) )
                    
                # If the distance of adjacency is less than 20 cm, it is an adiabatic wall,
                # otherwise a a normal heat transmittance external wall. 
                if np.array(adj).any() < 0.2:
                    print('adj')
                    
                    # Adiabatic walls with no windows.
                    idftxt += (adiabatic_wall(x[i],x[i+1],y[i],y[i+1],height0,buildingHeight,i))
                    
                
                else:
                    # External Walls
                    idftxt += (external_wall(x[i],x[i+1],y[i],y[i+1],height0,buildingHeight,i)) 
                    
                    # Get the length of a wall
                    line = LineString([Point((x[i],y[i])), Point((x[i+1],y[i+1]))])
            
                    # Add windows if the length of the wall is greater than 2 meters.
                    # Avoid having windows on smaller walls of complex building shapes.
                    if line.length > 2:
                        
                        # Calculate the geometry of windows based on the geometry of the walls and WWR.
                        a = line.interpolate(wwr, normalized=True)
                        b = line.interpolate(1-wwr, normalized=True)
                        R = (buildingHeight - buildingHeight * math.sqrt(wwr))/2
            
                        # External Windows
                        idftxt += (external_win(a.x,b.x,a.y,b.y, height0+R, buildingHeight-R, i,''))

        # If there is NO adjacent walls.        
        if len(adjacency) == 0:
            for i in range(len(x)-1):
                # External Walls
                idftxt += (external_wall(x[i],x[i+1],y[i],y[i+1],height0,buildingHeight,i)) 
                
                # Get the length of a wall
                line = LineString([Point((x[i],y[i])), Point((x[i+1],y[i+1]))])
                
                # Add windows if the length of the wall is greater than 2 meters.
                # Avoid having windows on smaller walls of complex building shapes.
                if line.length>2:
                    
                    # Calculates the geometry of windows based on the geometry of the walls and WWR
                    a = line.interpolate(wwr, normalized=True)
                    b = line.interpolate(1-wwr, normalized=True)
                    R = (buildingHeight - buildingHeight * math.sqrt(wwr))/2
        
                    # External Windows
                    idftxt += (external_win(a.x,b.x,a.y,b.y, height0+R, buildingHeight-R, i,''))
    
        # External Floor
        idftxt += floor(x, y, height0, basement)
        
        # External Roof
        idftxt += roof(xx, yy, buildingHeight)
        
        # If the building has a basement floor.
        if basement == 1:
            for i in range(len(x)-1):
                
                # Basement adiabatic walls (underground walls)
                idftxt += basement_adiabatic_wall(x[i], x[i+1], y[i], y[i+1], height0, heightbAdiabatic, i)
                
                # Basement exposed walls (onground walls)
                idftxt += basement_external_wall(x[i], x[i+1], y[i], y[i+1], height0, heightbExposed, i)
                
                # Get the length of a wall
                line = LineString([Point((x[i],y[i])), Point((x[i+1],y[i+1]))])
        
                # Add windows if the length of the wall is greater than 2 meters.
                # Avoid having windows on smaller walls of complex building shapes.
                if line.length > 2:
                    
                    # Calculate the geometry of windows based on the geometry of the walls and WWR.
                    a = line.interpolate(wwrb, normalized=True)
                    b = line.interpolate(1-wwrb, normalized=True)
                    Rb = (heightbExposed - heightbExposed * math.sqrt(wwrb))/2
        
                    # External Windows
                    idftxt += (external_win(a.x,b.x,a.y,b.y, height0+Rb, heightbExposed-Rb, i,'Basement'))
            
            # Basement ceiling and floor.
            idftxt += basement_ceiling(xx, yy, heightbExposed)
            idftxt += basement_floor(x, y, heightbAdiabatic)    
        
        # Convert the text file to an idf.
        fhandle = io.StringIO(idftxt) 
        idf = IDF(fhandle) 
        
        return idf
