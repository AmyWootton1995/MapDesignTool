#-------------------------------------------------------------------------------
# Name:        Masking Tool
# Purpose:     BSc (Hons) Geoinformatics Project
#
# Author:      Amy Wootton
#
# Created:     22/09/2017

# Copyright:   (c) Amy Wootton 2017
# License:     University of Pretoria
#-------------------------------------------------------------------------------
import os,sys,arcpy
from arcpy import env
from arcpy.sa import *

#   --Set Parameters--
#	--Name of Province the user wishes to mask to--
ParmProvince = arcpy.GetParameterAsText(0) 

#	--Setting the overwriting capabilities to allow the user to run the tool multiple times--
arcpy.env.overwriteOutput =  True

#   --
arcpy.AddMessage("Masking your map has begun...")
#   --

try:
    #   --Get map document--
    mxd = arcpy.mapping.MapDocument("current")

    #	--Create new folder for the workspace--
    arcpy.CreateFolder_management("C:/", "Temp")

    #   --Setting workspace and author--
    arcpy.env.workspace = r"C:\Temp\\"
    mxd.author = "Amy Wootton"

    #   --List data frames--
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    #	--Getting the interpolated raster layer and name, as well as removing any provincial layers--
    for df in arcpy.mapping.ListDataFrames(mxd):
    	for lyr in arcpy.mapping.ListLayers(mxd, "Int*", df):
           	rasterlyr = lyr
           	rastername = lyr.longName
		for lyr in arcpy.mapping.ListLayers(mxd, "*Prov*", df):
			arcpy.mapping.RemoveLayer(df, lyr)

    #   --Setting extent of map--
    ext = rasterlyr.getExtent()
    df.extent = ext
   
    #	--Adding in additional layers for masking--
    arcpy.AddMessage("Adding in provincial data...")
    #	--Adding in South African Provinces from root folder of the tool--
    path_to_provlayer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Provinces.shp")
    addProvInfo = arcpy.mapping.Layer(path_to_provlayer)
    arcpy.mapping.AddLayer(df, addProvInfo, "TOP")

    #	--Searching for the province that the user specified to mask to--
    if ParmProvince == "ALL":
    	selected = arcpy.SelectLayerByAttribute_management ("Provinces", "NEW_SELECTION")
    else:
    	selected = arcpy.SelectLayerByAttribute_management ("Provinces", "NEW_SELECTION", "\"PR_NAME\" = " + "'" + ParmProvince + "'")

    #	--Saving the selected layer to the temporary folder--
    arcpy.CopyFeatures_management(selected, "SelectedProvince")

    #	--Adding in the saved selected layer--
    provlayermask = arcpy.mapping.Layer(r"C:\Temp\SelectedProvince.shp")
    arcpy.mapping.AddLayer(df,provlayermask,"AUTO_ARRANGE")
    arcpy.AddMessage("Added in Province layer")

    #	--Clearing the selection--
    arcpy.SelectLayerByAttribute_management ("Provinces", "CLEAR_SELECTION")

    #	--Setting the local variables for masking--
    inRaster = rasterlyr
    inMaskData = provlayermask

    #	--Execute Masking using predefined variables--
    outExtractByMask = ExtractByMask(inRaster, inMaskData)

    #	--Saving the output raster--
    outExtractByMask.save("C:/Temp/" + rastername)
    MaskedRaster = arcpy.mapping.Layer(rastername)
    arcpy.mapping.AddLayer(df,MaskedRaster,"AUTO_ARRANGE")
    arcpy.AddMessage("Added in Masked layer")

    #	--Updating the Legend to represent all the layers--
    legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", "Legend")[0]
    legend.autoAdd = True
    legend.adjustColumnCount(3)

    #	--Removing the selected province layer--
    for df in arcpy.mapping.ListDataFrames(mxd):
		for lyr in arcpy.mapping.ListLayers(mxd, "SelectedProvince", df):
			arcpy.mapping.RemoveLayer(df, lyr)

except (Exception) as e:
    arcpy.AddMessage('Exception Message' + e.message)

#	--
arcpy.AddMessage("Your map has been masked!")
arcpy.AddMessage("Thank you for using this tool!")
#	--