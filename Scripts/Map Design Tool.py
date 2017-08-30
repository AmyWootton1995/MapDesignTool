#-------------------------------------------------------------------------------
# Name:        Map Design Tool
# Purpose:     BSc (Hons) Geoinformatics Project
#
# Author:      Amy Wootton
#
# Created:     24/08/2017
# Copyright:   (c) Amy Wootton 2017
# Licence:     University of Pretoria
#-------------------------------------------------------------------------------
import os,sys,arcpy, pythonaddins
from arcpy import env

#   --Set Parameters--
# Name of input text file
ParmInTxt = arcpy.GetParameterAsText(0) 
# Name of map
ParmMapName = arcpy.GetParameterAsText(1)
# Name of Points
ParmPointsName = arcpy.GetParameterAsText(2)
# Type of Basemap
ParmBaseMapInfo = arcpy.GetParameterAsText(3)
#Projection
ParmProjection = arcpy.GetParameterAsText(4)
# Credit Info
ParmCredits = arcpy.GetParameterAsText(5)
# Name of Saved Layer
ParmSaveLayerName = arcpy.GetParameterAsText(6) + ".lyr"

#   --
arcpy.AddMessage("Designing your map has begun...")
#   --

try:
    #   --Get mxd--
    mxd = arcpy.mapping.MapDocument("current")

    #   --Setting workspace and author--
    arcpy.env.workspace = r"C:\Temp\\"
    mxd.author = "Amy Wootton"

    #   --List data frames--
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    #   --Defining types of basemaps--
    arcpy.AddMessage("Adding in Base Map...")
    if ParmBaseMapInfo == "Open Street Map":
        BaseMap = "OSM.lyr"
    elif ParmBaseMapInfo == "Topographic Map":
        BaseMap = "Topo.lyr"
    elif ParmBaseMapInfo == "Aerial Image (without labels)":
        BaseMap = "AWOL.lyr"
    elif ParmBaseMapInfo == "National Geopgraphic":
        BaseMap = "NatGeo.lyr"
    else:
        BaseMap = "OSM.lyr"
        pythonaddins.MessageBox("Open Street Map has been used as a default base map, because the selected base map could not be found!", "Welcome to Map Design Tool", 0)
    
    #   --Adding in basemap from root folder--
    path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), BaseMap)
    addBase = arcpy.mapping.Layer(path_to_layer)
    arcpy.mapping.AddLayer(df, addBase, "BOTTOM")

    #   --Setting variables--
    in_Table = ParmInTxt
    x_coords = "Long(x)"
    y_coords = "Lat(y)"
    z_coords = ""
    out_Layer = ParmPointsName

    #   --Save layer into root folder--
    saved_Layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), ParmSaveLayerName)

    #   --Define types of projections--
    if ParmProjection == "Antartica":
        WKID = 4636
    elif ParmProjection == "Asia & Middle East":
        WKID = 4667
    elif ParmProjection == "Australasia":
        WKID = 4202
    elif ParmProjection == "Central Africa":
        WKID = 4259
    elif ParmProjection == "Central America":
        WKID = 5451
    elif ParmProjection == "Europe":
        WKID = 104102
    elif ParmProjection == "Greenland":
        WKID = 4747
    elif ParmProjection == "North America":
        WKID = 37260
    elif ParmProjection == "North Eastern Africa":
        WKID = 4201
    elif ParmProjection == "North Western Africa":
        WKID = 4819
    elif ParmProjection == "Pacific Ocean":
        WKID = 104260
    elif ParmProjection == "South America":
        WKID = 4248
    elif ParmProjection == "Southern Africa":
        WKID = 4222
    elif ParmProjection == "World":
        WKID =104926
    else:
        WKID = 104926
    
    #   --Set up projection--
    sr = arcpy.SpatialReference()
    sr.factoryCode = WKID
    sr.create()
    env.outputCoordinateSystem = sr

    #   --Make the XY event layer--
    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer,sr, z_coords)

    #   --Save layer and add saved layer to current map--
    arcpy.SaveToLayerFile_management(out_Layer,saved_Layer)
    arcpy.AddMessage('Adding your map layer...')
    path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), ParmSaveLayerName)
    addPoints = arcpy.mapping.Layer(path_to_layer)
    arcpy.mapping.AddLayer(df,addPoints,"AUTO_ARRANGE")

    #   --Setting extent of map--
    lyr = arcpy.mapping.ListLayers(mxd, '**', df)[0]
    ext = lyr.getExtent()
    df.extent = ext
    
    #   --Changing Title Layout Element--
    elemTitle = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "title")[0]
    elemTitle.text = ParmMapName

    #   --Changing Credits Layout Element--
    elemCredits = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "Credits")[0]
    elemCredits = ParmCredits 

    #   --Change to Layout view--
    arcpy.mapping.MapDocument("current").activeView = "PAGE_LAYOUT"

except (Exception) as e:
    arcpy.AddMessage('Exception Message' + e.message)

arcpy.AddMessage("Your map has been designed!")
arcpy.AddMessage("Thank you for using this tool!")