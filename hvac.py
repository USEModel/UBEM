# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:28:30 2021

@author: fatjo876
"""

from eppy.modeleditor import IDF
import io

class HVAC():  
    def __init__(self, idf, roomTemp, ventFlow, ventType, heatRecovery, heatRecoveryEffect,
                 Tamb,Tground,Troom, Q):
        self.idf = idf 
        self.roomTemp = roomTemp # Set temperature for heating
        self.ventFlow = ventFlow # Ventilation flow rate
        self.ventType = ventType # Type of ventilation system 
        self.heatRecovery = heatRecovery
        self.heatRecoverEffect = heatRecoveryEffect
        self.Tamb = Tamb
        self.Tground = Tground
        self.Troom = Troom
        self.Q = Q


    def ventilation (idf, ventFlow, ventType, zone):
        """
        Makes the model for the ventilation system.
        
        parameters
        ----------
        idf: idf
        
        ventFlow:float
            Ventilation flow rate(ACH).
            
        ventType: str
            Main type of the ventilation system.
            (exhaust, intake, balanced)
            
                    
        output
        ------
        idf
        """
        # EnergyPlus idf object for the ventilation system.
        idf.newidfobject('ZONEVENTILATION:DESIGNFLOWRATE',
                         Name = 'Ventilation'+zone,
                         Zone_or_ZoneList_Name = zone,
                         Schedule_Name = 'Always 1',
                         Design_Flow_Rate_Calculation_Method = 'AirChanges/Hour',
                         Air_Changes_per_Hour = ventFlow,
                         Ventilation_Type = ventType
                         )
        
       
        return idf
    
    def ventilation_schedule(idf):
        # The schedule for operation of the ventilation system.
        # Here, the ventilation is always on.
        idf.newidfobject('SCHEDULE:COMPACT',
                         Name = 'Always 1',
                         Schedule_Type_Limits_Name = 'Any Number',
                         Field_1 = 'Through: 12/31',
                         Field_2 = 'For: AllDays',
                         Field_3 = 'Until:24:00',
                         Field_4 = 1)
        
        # Schedule_Type_Limit
        idf.newidfobject('SCHEDULETYPELIMITS',
                         Name = 'Any Number')
        return idf
    
    def infiltration (idf, infFlow,zone):
        """
        Makes the model for infiltration losses.
        
        parameters
        ----------
        idf: idf
        
        infFlow:float
            Infiltration flow rate(ACH).
            
                    
        output
        ------
        idf
        """
        # EnergyPlus idf object for the ventilation system.
        idf.newidfobject('ZONEINFILTRATION:DESIGNFLOWRATE',
                         Name = 'Infiltration'+zone,
                         Zone_or_ZoneList_Name = zone,
                         Schedule_Name = 'Always 1',
                         Design_Flow_Rate_Calculation_Method = 'AirChanges/Hour',
                         Air_Changes_per_Hour = infFlow
                         )
        
        
        return idf

        
    
    def ideal (idf, heatRecovery, heatRecoveryEffect, zone):
        """
        Makes the model for the ideal heating system.
        
        parameters
        ----------
        idf

        roomTemp: float
            Indoor set temperature for heating.
        heatRecovery: int
            0 for no heat recovery
            1 for system with heat recovery
        heatRecoveryEffect: int
            Retio of heat recovery
            
                    
        output
        ------
        idf
        """
        
  
        
        # Define the thermostat settings.
        idf.newidfobject ('ZONECONTROL:THERMOSTAT',
                          Name = 'Thermostat'+zone,
                          Zone_or_ZoneList_Name = zone,
                          Control_Type_Schedule_Name = 'Always 4',
                          Control_1_Object_Type = 'ThermostatSetpoint:DualSetpoint',
                          Control_1_Name = 'DualSetpoint'
                          )        
        # Ideal system
        
        idf.newidfobject ('ZONEHVAC:IDEALLOADSAIRSYSTEM',
                          Name = str('PurchasedAir'+zone),
                          Zone_Supply_Air_Node_Name = str('SupplyInlet'+zone),
                          Heat_Recovery_Type = heatRecovery,
                          Sensible_Heat_Recovery_Effectiveness = heatRecoveryEffect
                          )
        # Ideal system equipment connections.
        idf.newidfobject ('ZONEHVAC:EQUIPMENTCONNECTIONS',
                  Zone_Name = zone,
                  Zone_Conditioning_Equipment_List_Name = str('Equipment'+zone),
                  Zone_Air_Inlet_Node_or_NodeList_Name = str('SupplyInlet'+zone),
                  Zone_Air_Node_Name = str('ZoneAirNode'+zone),
                  Zone_Return_Air_Node_or_NodeList_Name = str('ReturnOutlet'+zone)
                  )
 
        # Ideal system equipment.
        idf.copyidfobject( IDF( io.StringIO ('ZONEHVAC:EQUIPMENTLIST'+',\n'+
                                             'Equipment'+zone+',\n'+
                                              'SequentialLoad'+',\n'+
                                              'ZoneHVAC:IdealLoadsAirSystem'+',\n'+
                                              'PurchasedAir'+zone+',\n'+
                                              '1'+',\n'+
                                              '1'+';\n')
                               ).idfobjects['ZONEHVAC:EQUIPMENTLIST'][0]) 
    
        return idf
    
    
    
    def ideal_schedule(idf, roomTemp):
          # Define a dual setpoint control for thermostat.
        idf.newidfobject('THERMOSTATSETPOINT:DUALSETPOINT',
                         Name = 'DualSetpoint',
                         Heating_Setpoint_Temperature_Schedule_Name = 'HeatingON',
                         Cooling_Setpoint_Temperature_Schedule_Name = 'CoolingON'
                         )
        
        # Schedule for the heating set temperature of the thermostat
        idf.newidfobject ('SCHEDULE:COMPACT',
                          Name = 'HeatingON',
                          Schedule_Type_Limits_Name = 'Any Number',
                          Field_1 = 'Through: 12/31',
                          Field_2 = 'For: AllDays', 
                          Field_3 = 'Until: 24:00',
                          Field_4 = roomTemp
                          )
        
        # Schedule for the cooling set temperature of the thermostat                  
        idf.newidfobject ('SCHEDULE:COMPACT',
                    Name = 'CoolingON',
                    Schedule_Type_Limits_Name = 'Any Number',
                    Field_1 = 'Through: 12/31',
                    Field_2 = 'For: AllDays', 
                    Field_3 = 'Until: 24:00',
                    Field_4 = 45 # To limit the cooling demand in Swedish buildings.
                    ) 
        
        # Schedule for the dual Setpoint. 
        idf.newidfobject ('SCHEDULE:COMPACT',
                    Name = 'Always 4',
                    Schedule_Type_Limits_Name = 'Any Number',
                    Field_1 = 'Through: 12/31',
                    Field_2 = 'For: AllDays', 
                    Field_3 = 'Until: 24:00',
                    Field_4 = 4 
                    )
        
        return idf
        

    
    def GSHP(Tamb,Tground,Q):
        
        Tsink = 40 - Tamb
        COP = 10.29 - 0.21*(Tsink - Tground) + 0.0012 *(Tsink - Tground)**2
        E = Q/COP
        return E
    
    def XSHP(Tamb,Troom,Q):
        
        Tsink = 40 - Tamb
        COP = 6.08 - 0.09*(Tsink - Troom)+ 0.0005 *(Tsink - Troom)**2
        E = Q/COP
        return E
    
    def ASHP(Tamb,Q):
        
        Tsink = 40 - Tamb
        COP = 6.08 - 0.09*(Tsink - Tamb)+ 0.0005 *(Tsink - Tamb)**2
        E = Q/COP
        return E    



    """
    def ideal (idf,Tset,Vbuild):
        
        Makes an ideal system for heating, cooling and ventilation.
        
        input
        ----------
        idf: idf

        Tset: int
            Indoor set temperature for heating.
            
        Vbuild: int
            Volume of the building according to its geometry.
            
                    
        output
        ------
        idf: idf  
        
        
        idf.newidfobject('HVACTemplate:Thermostat',
                         Name = 'thermostat',
                         Constant_Heating_Setpoint = Tset,
                         # Set a high cooling setpoint to limit the cooling demand.
                         Constant_Cooling_Setpoint = 45 
                         )

        idf.newidfobject ('HVACTemplate:Zone:IdealLoadsAirSystem',
                          Zone_Name = 'ZONE',
                          Template_Thermostat_Name = 'thermostat',
                          Outdoor_Air_Method = 'Flow/Zone',
                          Outdoor_Air_Flow_Rate_per_Zone = 0.5/3600 * Vbuild
                          )

    
        return idf    
        """


