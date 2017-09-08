#-------------------------------------------------------------------------------
# Name:        Map Design Tool
# Purpose:     BSc (Hons) Geoinformatics Project
#
# Author:      Amy Wootton, tferreira
#
# Created:     24/08/2017

# Copyright:   (c) Amy Wootton 2017
# Licence:     University of Pretoria
#-------------------------------------------------------------------------------
import os,sys,arcpy, pythonaddins, datetime, arcgisscripting, string
from arcpy import env

i = datetime.datetime.now()
MyDate = "%s%s_%s%s%s_" % (i.hour, i.minute, i.day, i.month, i.year) 

#   --Set Parameters--
# Path name of input csv file
ParmInTxt = arcpy.GetParameterAsText(0) 
# Name of map title
ParmMapName = arcpy.GetParameterAsText(1)
# Name of Points
ParmPointsName = arcpy.GetParameterAsText(2)
# Type of Base map
ParmBaseMapInfo = arcpy.GetParameterAsText(3)
#Projection
ParmProjection = arcpy.GetParameterAsText(4)
#Interpolation
ParmInterpolation = arcpy.GetParameterAsText(5)
#Styling
ParmStyling = arcpy.GetParameterAsText(6)
# Credit Info
ParmCredits = arcpy.GetParameterAsText(7)
# Name of Saved Layer
ParmSaveLayerName = MyDate + arcpy.GetParameterAsText(8) + ".lyr"

arcpy.env.overwriteOutput =  True

#   --
arcpy.AddMessage("Designing your map has begun...")
#   --

try:
    #   --Get map document--
    mxd = arcpy.mapping.MapDocument("current")

    #   --Setting workspace and author--
    arcpy.env.workspace = r"C:\Temp\\"
    mxd.author = "Amy Wootton"

    #   --List data frames--
    df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]

    #   --Defining types of basemaps--
    if ParmBaseMapInfo == "Open Street Map":
        BaseMap = "BaseMap3 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "Topographic Map":
        BaseMap = "BaseMap4 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "Aerial Image (without labels)":
        BaseMap = "BaseMap1 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "National Geopgraphic":
        BaseMap = "BaseMap2 (DO NOT DELETE).lyr"
    elif ParmBaseMapInfo == "None":
    	BaseMap = "None"
    else:
        BaseMap = "None"
        pythonaddins.MessageBox("No base map has been selected", "Welcome to Map Design Tool", 0)
    
    #   --Adding in basemap from root folder--
    if BaseMap == "None":
    	arcpy.AddMessage("No Base Map Selected...")
    else:
    	arcpy.AddMessage("Adding in Base Map...")
    	path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), BaseMap)
    	addBase = arcpy.mapping.Layer(path_to_layer)
    	arcpy.mapping.AddLayer(df, addBase, "BOTTOM")

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

    #   --Setting variables--
    in_Table = ParmInTxt
    x_coords = "Long(x)"
    y_coords = "Lat(y)"
    z_coords = ""
    out_Layer = ParmPointsName

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
    elemCredits = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "credits")[0]
    elemCredits.text = "Credits: " + ParmCredits + "  Date: %s/%s/%s" % (i.day, i.month, i.year)

    #	--Getting last row name in csv--
    featureclass = addPoints
    field_names = [f.name for f in arcpy.ListFields(featureclass)]
    count = len(field_names)
    QuantifyName = field_names[count - 2]
    arcpy.AddMessage(QuantifyName) 

    #	--Interpolation--

    if ParmInterpolation == "Yes":
    	gp = arcgisscripting.create() #geoprocessor object create
    	# Check out any necessary licenses
    	gp.checkoutextension("Spatial")
    	# Set the input feature dataset
    	inputFeatureDataset = addPoints
    	attributeName = QuantifyName
    	# Set the output raster name
    	outputRaster = "C:/data/final_1"
    	# Define the semivariogram
    	Model = "Spherical"         #(Remember the space at the end)
    	LagSize = "0.4496 "          #(Remember the space at the end)
    	MajorRange = "2.6185 "       #(Remember the space at the end)
    	PartialSill = "542.65 "      #(Remember the space at the end)
    	Nugget = "0"
    	Semivariogram = LagSize + MajorRange + PartialSill + Nugget
    	# Don't write out the variance raster
    	Output_variance_of_prediction_raster = ""
    	gp.Kriging_sa(inputFeatureDataset, attributeName, outputRaster, Model, Semivariogram, "1", "VARIABLE 12", Output_variance_of_prediction_raster)
    	arcpy.AddMessage("Completed IDW")

    	# Method 1
    	#arcpy.InterpolateFromPointCloud_management(addPoints, 'C:/data/dsm.crf', '10','IDW', 'GAUSS5x5', 'DSM')

    	# Method 2
    	# Inter = "Yes"
    	# inPoints = addPoints
    	# inField = QuantifyName
    	# outRaster = 'outImgServ'
    	# optimizeFor = 'SPEED'
    	# transform = 'False'
    	# subsetSize = 50
    	# numNeighbors = 8
    	# outCellSize = '10000 Meters'
    	# error = 'NO_OUTPUT_ERROR'
    	# arcpy.InterpolatePoints_ra(inPoints, inField, outRaster, optimizeFor, transform, subsetSize, numNeighbors, outCellSize, error)

    elif ParmInterpolation == "No":
    	Inter = "No"
    else:
    	arcpy.AddMessage("Interpolation failed")


    #	--Styling--
    if ParmStyling == "Yes":
    	Style = "Yes"
    elif ParmStyling == "No":
    	Style = "No"
    else:
    	arcpy.AddMessage("Styling failed")

    #   --Change to Layout view--
    arcpy.mapping.MapDocument("current").activeView = "PAGE_LAYOUT"

except (Exception) as e:
    arcpy.AddMessage('Exception Message' + e.message)

arcpy.AddMessage("Your map has been designed!")
arcpy.AddMessage("Thank you for using this tool!")