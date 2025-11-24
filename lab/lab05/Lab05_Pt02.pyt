# -*- coding: utf-8 -*-

import arcpy
import os


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [BuildingProximity]


class BuildingProximity:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Building Proximity"
        self.category = "Building Tools"
        self.description = "Determine which buildings on ASU's campus are near a targeted building."

    def getParameterInfo(self):
        """Define the tool parameters."""
        folder = arcpy.Parameter(
            displayName="Workspace Folder",
            name="workspace_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        gdb_name = arcpy.Parameter(
            displayName="Geodatabase Name",
            name="gdb_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        garage_csv = arcpy.Parameter(
            displayName="Garage CSV File",
            name="garage_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        garage_layer = arcpy.Parameter(
            displayName="Garage Layer Name",
            name="garage_layer",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        selected_garage = arcpy.Parameter(
            displayName="Selected Garage",
            name="selected_garage",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        buffer_distance = arcpy.Parameter(
            displayName="Buffer Distance",
            name="buffer_distance",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )

        params = [folder, gdb_name, garage_csv, garage_layer, selected_garage, buffer_distance]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        gdb_folder = parameters[0].valueAsText
        gdb_name = parameters[1].valueAsText
        garage_csv = parameters[2].valueAsText
        garage_layer = parameters[3].valueAsText
        selected_garage = parameters[4].valueAsText
        buffer_distance = parameters[5].valueAsText

        gdb_name_full = f"{gdb_name}.gdb"
        gdb_folder_path = os.path.join(gdb_folder, gdb_name_full)

        arcpy.env.workspace = gdb_folder_path

        arcpy.management.MakeXYEventLayer(
            garage_csv,
            "X",
            "Y",
            garage_layer
        )
        
        buildingsLayer = gdb_folder_path + r"\BuildingsLayer"
        where = "NAME = '{}'".format(selected_garage)

        cursor = arcpy.da.SearchCursor(buildingsLayer, ["NAME"], where)
        shouldProceed = False

        for row in cursor:
            if row[0] == selected_garage:
                shouldProceed = True
                break

        if shouldProceed:
            selected_garage_layer = gdb_folder_path + r"\Selected_Garage_Layer"
            garage_feature = arcpy.analysis.Select(
                buildingsLayer,
                selected_garage_layer,
                where
            )
            garage_buffer = gdb_folder_path + r"\Garage_Buffer".format(buffer_distance)
            arcpy.analysis.Buffer(
                garage_feature,
                garage_buffer,
                "{} Feet".format(buffer_distance)
            )
            arcpy.analysis.Clip(
                buildingsLayer,
                garage_buffer,
                gdb_folder_path + r"\Nearby_Buildings"
            )
            messages.addMessage("Success!")
        else:
            messages.addMessage("Garage name not found.")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class Tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""