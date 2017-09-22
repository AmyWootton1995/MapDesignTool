#-------------------------------------------------------------------------------
# Name:        Clipping Tool
# Purpose:     BSc (Hons) Geoinformatics Project
#
# Author:      Amy Wootton
#
# Created:     22/09/2017

# Copyright:   (c) Amy Wootton 2017
# Licence:     University of Pretoria
#-------------------------------------------------------------------------------
import os,sys,arcpy, pythonaddins, datetime, arcgisscripting, string
from arcpy import env
from arcpy.sa import *

#   --Set Parameters--
# Province
ParmProvince = arcpy.GetParameterAsText(0) 

arcpy.env.overwriteOutput =  True

#   --
arcpy.AddMessage("Clipping your map has begun...")
#   --

try:
    #   --Get map document--
    mxd = arcpy.mapping.MapDocument("current")

    #   --Setting workspace and author--
    arcpy.env.workspace = r"C:\Temp\\"
    mxd.author = "Amy Wootton"

    #   --List data frames--
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    for df in arcpy.mapping.ListDataFrames(mxd):
    	for lyr in arcpy.mapping.ListLayers(mxd, "Int*", df):
           	rasterlyr = lyr
           	rastername = lyr.longName
           	arcpy.AddMessage(rasterlyr)
		for lyr in arcpy.mapping.ListLayers(mxd, "*Prov*", df):
			arcpy.mapping.RemoveLayer(df, lyr)

    #   --Setting extent of map--
    ext = rasterlyr.getExtent()
    df.extent = ext

    # Set layer that output symbology will be based on
    path_to_Polysymbologylayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Symbology_Layer_Polygon.lyr")
    symbologyPolygonLayer = arcpy.mapping.Layer(path_to_Polysymbologylayer)
    path_to_Rastersymbologylayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Symbology_Layer_Raster.lyr")
    symbologyRasterLayer = arcpy.mapping.Layer(path_to_Rastersymbologylayer)
   
    arcpy.AddMessage("Adding in provincial data...")
    path_to_provlayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "New_SAProv.shp")
    addProvInfo = arcpy.mapping.Layer(path_to_provlayer)
    # Apply the symbology from the symbology layer to the input layer
    arcpy.ApplySymbologyFromLayer_management (addProvInfo, symbologyPolygonLayer)
    arcpy.mapping.AddLayer(df, addProvInfo, "TOP")
    addProvInfo.showLabels = True

    legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
    legend.autoAdd = True
    legend.adjustColumnCount(4)

    selected = arcpy.SelectLayerByAttribute_management ("New_SAProv", "NEW_SELECTION", "\"PR_NAME\" = " + "'" + ParmProvince + "'")

    # Write the selected features to a new featureclas
    arcpy.CopyFeatures_management(selected, "ProvinceClipped")
    provlayermask = arcpy.mapping.Layer(r"C:\Temp\ProvinceClipped.shp")
    arcpy.mapping.AddLayer(df,provlayermask,"AUTO_ARRANGE")
    arcpy.AddMessage("Added in Province layer")
    arcpy.SelectLayerByAttribute_management ("New_SAProv", "CLEAR_SELECTION")

    # Set local variables
    inRaster = rasterlyr
    inMaskData = provlayermask

    # Execute ExtractByMask
    outExtractByMask = ExtractByMask(inRaster, inMaskData)

    # Save the output
    outExtractByMask.save("C:/Temp/" + rastername)
    newlayerB = arcpy.mapping.Layer(rastername)
    # Apply the symbology from the symbology layer to the input layer
    arcpy.ApplySymbologyFromLayer_management (newlayerB, symbologyRasterLayer)
    arcpy.mapping.AddLayer(df,newlayerB,"AUTO_ARRANGE")
    arcpy.AddMessage("Added in Clipped layer")



    for df in arcpy.mapping.ListDataFrames(mxd):
		for lyr in arcpy.mapping.ListLayers(mxd, "ProvinceClipped", df):
			arcpy.mapping.RemoveLayer(df, lyr)
		# for lyr in arcpy.mapping.ListLayers(mxd, "Int*", df):
		# 	arcpy.mapping.RemoveLayer(df, lyr)

except (Exception) as e:
    arcpy.AddMessage('Exception Message' + e.message)


arcpy.AddMessage("Your map has been designed!")
arcpy.AddMessage("Thank you for using this tool!")