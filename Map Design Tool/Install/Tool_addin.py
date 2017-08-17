import os
import sys
import arcpy
from arcpy import env
def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    try:
        #TODO: Add analysis here
        pass
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]
# End do_analysis function
 
# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE, 
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments are optional
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv)


print "Welcome to Map Design Tool!"
print "To start, please import a txt file using ArcMap's import functionality..."
print "Once you have uploaded, click on the gear button to design your map!"
global NameofTable

class btnDesign(object):
    """Implementation for Tool_addin.button5 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        # Moving views to Layout view
        mxd = arcpy.mapping.MapDocument("current")
        
        #Setting workspace and author
        arcpy.env.workspace = r"C:\Temp\\"
        mxd.author = "GIS Department"
        df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
        for table in arcpy.mapping.ListTableViews(mxd):
            print "Table Name: " + table.name
            NameofTable = table.name
        
        if NameofTable == "":
            print "Please import data using the ArcMap import functionality!"
        
        else:
        
            #Adding in basemap rom instal folder
            path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OSM.lyr')
            addLayer = arcpy.mapping.Layer(path_to_layer)  
            arcpy.mapping.AddLayer(df, addLayer, "BOTTOM") 
            arcpy.mapping.MapDocument("current").activeView = "PAGE_LAYOUT"
            
            
            try:
                # Set the local variables
                in_Table = NameofTable
                x_coords = "Long(x)"
                y_coords = "Lat(y)"
                z_coords = ""
                out_Layer = "Points"
                  
                WKID = 4326 # WGS-1984
                sr = arcpy.SpatialReference()
                sr.factoryCode = WKID
                sr.create()
                env.outputCoordinateSystem = sr
                
                # Make the XY event layer...
                arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer,sr, z_coords)
                
            except Exception as err:
                print(err.args[0])
            
            #Setting extent
            lyr = arcpy.mapping.ListLayers(mxd, 'Points*', df)[0]  
            ext = lyr.getExtent()  
            df.extent = ext 
            
            #Changing title to user input
            elemTitle=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "title")[0]
            elemTitle.text = "Title"
            #elemTitle.elementPositionX = 0.6046
            print "Change Title name works"
            
            #raw_input is not supported by arcmap???
            #userInput = raw_input('Give me a value');
            #print 'The square of your number is: ' + str(userInput)
            
            
            del mxd
        
        pass

class btnHelp(object):
    """Implementation for Tool_addin.button8 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):

        pass