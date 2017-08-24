import os
import sys
import arcpy
from arcpy import env
import pythonaddins
with pythonaddins.ProgressDialog as dialog:
    dialog.title = "Progress Dialog"
    dialog.description = "Copying a large feature class."
    dialog.animation = "File"
    for i in xrange(100):
        dialog.progress = i
        if dialog.cancelled:
            raise Exception("Ooops")

print "Welcome to Map Design Tool!"
print "To start, please click on the button"

class MyValidator(object):
    def __str__(self):
        return "Text files(*.txt)"
    def __call__(self, filename):
        if os.path.isfile(filename) and filename.lower().endswith(".txt"):
            return True
        return False



class btnDesign(object):
    """Implementation for Tool_addin.button5 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.MessageBox("Please import a textfile (txt) that satisfies the requirements of this tool...", "Welcome to Map Design Tool", 0)
        layer_files = pythonaddins.OpenDialog("Select a txt file",r"c:\files", filter=MyValidator())
                 
        try:
            
            # Moving views to Layout view
            mxd = arcpy.mapping.MapDocument("current")
            
            #Setting workspace and author
            arcpy.env.workspace = r"C:\Temp\\"
            mxd.author = "GIS Department"
                
            df = arcpy.mapping.ListDataFrames(mxd,"Layers")[0]
            if not isinstance(df, arcpy.mapping.Layer):
                for layer_file in layer_files:
                    layer = arcpy.mapping.TableView(layer_file)
                    arcpy.mapping.AddTableView(df, layer)
            else:
                pythonaddins.MessageBox('Select a data frame', 'INFO', 0)
            
            for table in arcpy.mapping.ListTableViews(mxd):
                NameofTable = table.name
            
            
        
            #Adding in basemap rom instal folder
            path_to_layer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OSM.lyr')
            
            addBase = arcpy.mapping.Layer(path_to_layer)  
            arcpy.mapping.AddLayer(df, addBase, "BOTTOM") 
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
        except Exception as err:
                pythonaddins.MessageBox("No textfile was imported, or the format of the textfile is incorrect!","Error")
        pass

class btnHelp(object):
    """Implementation for Tool_addin.button8 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.MessageBox("Welcome to the Help section","Help")
        pass