#-------------------------------------------------------------------------------
# Name:        Map Design Tool
# Purpose:     BSc (Hons) Geoinformatics Project
#
# Author:      Amy Wootton
#
# Created:     24/08/2017

# Copyright:   (c) Amy Wootton 2017
# License:     University of Pretoria
#-------------------------------------------------------------------------------
#	--Importing required modules--
import os,sys,arcpy, datetime, string 
from arcpy import env
from arcpy.sa import *

#	--Getting the time of day, and date for today--
i = datetime.datetime.now()
MyDate = "%s%s_%s%s%s_" % (i.hour, i.minute, i.day, i.month, i.year) 

#   --Set Parameters--
#	--Path name of input csv file--
ParmInTxt = arcpy.GetParameterAsText(0) 
#	--Name of map title (Such as "Risks and hazards in South Africa")--
ParmMapName = arcpy.GetParameterAsText(1)
#	--Name of Points to be mapped (Such as "Seismic Events")--
ParmPointsName = arcpy.GetParameterAsText(2)
#	--Type of Base map (Such as "Open Street Map")--
ParmBaseMapInfo = arcpy.GetParameterAsText(3)
#	--Projection ("Asks user what area they are mapping in, to apply the correct projection")--
ParmProjection = arcpy.GetParameterAsText(4)
#	--Interpolation ("Yes" or "No")--
ParmInterpolation = arcpy.GetParameterAsText(5)
#	--Author Info (Such as "Amy Wootton")--
ParmCredits = arcpy.GetParameterAsText(6)
#	--Name of Saved Layer (Such as "My New Map")--
ParmSaveLayerName = MyDate + arcpy.GetParameterAsText(7) + ".lyr"

#	--Setting the overwriting capabilities to allow the user to run the tool multiple times--
arcpy.env.overwriteOutput =  True

#   --
arcpy.AddMessage("Designing your map has begun...")
#   --

try:
    #   --Get map document--
    mxd = arcpy.mapping.MapDocument("current")

    #	--Create new folder for the workspace--
    arcpy.CreateFolder_management("C:/", "Temp")

    #   --Setting workspace and author--
    arcpy.env.workspace = r"C:\Temp\\"
    mxd.author = ParmCredits

    #   --List data frames--
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    #	--Removing all layers to create a blank starting point--
    for df in arcpy.mapping.ListDataFrames(mxd):
    		for lyr in arcpy.mapping.ListLayers(mxd, "", df):
           		arcpy.mapping.RemoveLayer(df, lyr)

    #   --Defining types of basemaps--
    if ParmBaseMapInfo == "Open Street Map":
        BaseMap = "BaseMap3 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "Topographic Map":
        BaseMap = "BaseMap4 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "Aerial Image (without labels)":
        BaseMap = "BaseMap1 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "National Geographic":
        BaseMap = "BaseMap2 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "None":
    	BaseMap = "None"
    else:
        BaseMap = "None"
    
    #   --Adding in basemap from root folder of the tool--
    if BaseMap == "None":
    	arcpy.AddMessage("No Base Map Selected...")
    else:
    	arcpy.AddMessage("Adding in Base Map...")
    	path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), BaseMap)
    	addBase = arcpy.mapping.Layer(path_to_layer)
    	arcpy.mapping.AddLayer(df, addBase, "BOTTOM")

    #   --Save layer into root folder of the tool--
    saved_Layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), ParmSaveLayerName)

    #   --Define types of projections--
    if ParmProjection == "Antarctica":
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
        WKID = 4717
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

    #   --Setting variables for making the XY event layer--
    in_Table = ParmInTxt
    x_coords = "Long(x)"
    y_coords = "Lat(y)"
    z_coords = ""
    out_Layer = ParmPointsName

    #   --Make the XY event layer using predefined variables--
    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer,sr, z_coords)

	#   --Save layer and add saved layer to current map--
    arcpy.SaveToLayerFile_management(out_Layer,saved_Layer)
    arcpy.AddMessage('Adding your map layer...')
    path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), ParmSaveLayerName)
    addPoints = arcpy.mapping.Layer(path_to_layer)
    arcpy.mapping.AddLayer(df,addPoints,"AUTO_ARRANGE")

    #   --Setting extent of map--
    lyr = arcpy.mapping.ListLayers(mxd, addPoints, df)[0]
    ext = lyr.getExtent()
    df.extent = ext
    
    #   --Changing Title Layout Element--
    elemTitle = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "title")[0]
    elemTitle.text = ParmMapName

    #   --Changing Credits Layout Element--
    elemCredits = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "credits")[0]
    elemCredits.text = "Credits: " + ParmCredits + "  Date: %s/%s/%s" % (i.day, i.month, i.year)

    #	--Interpolation--
    if ParmInterpolation == "Yes":
    	#	--Getting last row name in csv, in order to use for interpolation--
    	featureclass = addPoints
    	field_names = [f.name for f in arcpy.ListFields(featureclass)]
    	count = len(field_names)
    	QuantifyName = field_names[count - 2]
    	arcpy.AddMessage("Field that is being interpolated: " + QuantifyName)
    	
    	#	--Check if license required is installed--
    	arcpy.CheckOutExtension("Spatial")

    	#	--Set local variables for interpolation--
    	inPointFeatures = addPoints
    	zField = QuantifyName
    	power = 2

    	#	--Execute IDW Interpolation--
    	outIDW = Idw(inPointFeatures, zField, power=power, search_radius=RadiusVariable(12))
    	arcpy.AddMessage("Calculated IDW")
    	
    	#	--Save the output raster of interpolation into a temporary folder--
    	outIDW.save("C:/Temp/Int" + QuantifyName)
    	arcpy.AddMessage("Saved IDW layer")

    	#	--Adding in the interpolated raster--
    	newlayer = arcpy.mapping.Layer(r"C:\Temp\Int" + QuantifyName)
    	arcpy.mapping.AddLayer(df,newlayer,"AUTO_ARRANGE")
    	arcpy.AddMessage("Added in IDW raster layer")

    	# #	--Remove the csv point layer--
    	# for df in arcpy.mapping.ListDataFrames(mxd):
    	# 	for lyr in arcpy.mapping.ListLayers(mxd, "", df):
     #    		if lyr.name == ParmPointsName:
     #       			arcpy.mapping.RemoveLayer(df, lyr)

        #	--Adding in additional layers for Interpolation--
        arcpy.AddMessage("Adding in Base Map for Interpolation...")
        #	--Adding in world city points from root folder of the tool--
    	path_to_citylayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cities.shp")
    	addCityInfo = arcpy.mapping.Layer(path_to_citylayer)
    	arcpy.mapping.AddLayer(df, addCityInfo, "TOP")
    	#	--Adding in world country polygons from root folder of the tool--
    	path_to_polylayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Countries.shp")
    	addPolyInfo = arcpy.mapping.Layer(path_to_polylayer)
    	arcpy.mapping.AddLayer(df, addPolyInfo, "AUTO_ARRANGE")

    	#	--Updating the Legend to represent all the layers--
    	legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
    	legend.autoAdd = True
    	legend.adjustColumnCount(2)

    elif ParmInterpolation == "No":
    	arcpy.AddMessage("Interpolation not selected")
    else:
    	arcpy.AddMessage("Interpolation failed")

    #   --Change to Layout view--
    arcpy.mapping.MapDocument("current").activeView = "PAGE_LAYOUT"
    
    #	--
    arcpy.AddMessage("Your map has been designed!")
    arcpy.AddMessage("Thank you for using this tool!")
    #	--
except (Exception) as e:
    arcpy.AddMessage('Exception Message' + e.message)
