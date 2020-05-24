import re #To perform the search and replace.
from ..Script import Script
#from UM.Logger import Logger

class TemperatureTower(Script):
    version = "0.0.1"
    def getSettingDataString(self):
        return """{
            "name": "Temperature Tower """ + self.version + """ ",
            "key": "TemperatureTower",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "a_trigger":
                {
                    "label": "Trigger every",
                    "description": "Trigger every height or layer count",
                    "type": "enum",
                    "options": {"height":"Height","layer_cnt":"Layer Count"},
                    "default_value": "height"
                },
                "b_targetZ":
                {
                    "label": "Change Height",
                    "description": "Every additional Z height to change at",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.0,
                    "minimum_value": "0.0",
                    "enabled": "a_trigger == 'height'"
                },
                "b_targetL":
                {
                    "label": "Change Layer",
                    "description": "Every additional Layer count to change at",
                    "unit": "",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": "0",
                    "enabled": "a_trigger == 'layer_cnt'"
                },
                "c_temp":
                {
                    "label": "Change Temperature",
                    "description": "Temperature change at every step. This can also be negative.",
                    "unit": "°C",
                    "type": "int",
                    "default_value": "0"
                },
                "c_temp_min":
                {
                    "label": "Min Temp",
                    "description": "Minimum temperature limit.",
                    "unit": "°C",
                    "type": "int",
                    "default_value": 160,
                    "minimum_value": "0",
                    "minimum_value_warning": "160",
                    "maximum_value_warning": "250"
                },
                "c_temp_max":
                {
                    "label": "Max Temp",
                    "description": "Maximum temperature limit.",
                    "unit": "°C",
                    "type": "int",
                    "default_value": 250,
                    "minimum_value": "0",
                    "minimum_value_warning": "160",
                    "maximum_value_warning": "250"
                }
            }
        }"""
    
    def execute(self, data):
        layerStep = 0
        heightStep = 0.0
        if self.getSettingValueByKey("a_trigger") == "layer_cnt":
            layerStep = int(self.getSettingValueByKey("b_targetL"))
        else:
            heightStep = float(self.getSettingValueByKey("b_targetZ"))
        tempStep = int(self.getSettingValueByKey("c_temp"))
        tempMin = int(self.getSettingValueByKey("c_temp_min"))
        tempMax = int(self.getSettingValueByKey("c_temp_max"))

        #Logger.log('d', 'layerStep = %s' % layerStep)
        #Logger.log('d', 'heightStep = %s' % heightStep)
        #Logger.log('d', 'tempStep = %s' % tempStep)
        #Logger.log('d', 'tempMin = %s' % tempMin)
        #Logger.log('d', 'tempMax = %s' % tempMax)

        nextLayerStep = 0
        nextHeightStep = 0.0
        if layerStep > 0:
            nextLayerStep = layerStep
        elif heightStep > 0.0:
            nextHeightStep = heightStep
        
        layerHeight = 0.0
        nextLayerHeight = 0.0
        
        layer = 0
        lastLayer = 0
        temp = 0
        lastTemp = 0
        
        index = 0
        for active_layer in data:
            modified_gcode = ''
            lines = active_layer.split("\n")
            for line in lines[:-1]:
                if 'M104' in line:
                    temp = int(line.split(' S')[1].split()[0])
                    lastTemp = temp
                if ';LAYER:' in line:
                    layer = int(line.split(':')[1].split()[0])
                if 'G0' in line and ' Z' in line:
                    nextLayerHeight = float(line.split(' Z')[1].split()[0])
                if 'G1' in line and ' E' in line:
                    if float(line.split(' E')[1].split()[0]) > 0.0:
                        layerHeight = nextLayerHeight

            if layerStep > 0:
                if layer == nextLayerStep:
                    #Logger.log('d', 'Up Temp on layer in layer %s' % layer)
                    temp += tempStep
                    nextLayerStep += layerStep
            elif heightStep > 0.0 and layerHeight >= nextHeightStep:
                #Logger.log('d', 'Up Temp on height in layer %s and height %s' % (layer, layerHeight))
                temp += tempStep
                nextHeightStep += heightStep
            
            if temp != lastTemp:
                if temp <= tempMax and temp >= tempMin:
                    modified_gcode = lines[0] + '\n'
                    modified_gcode += ';TemperatureTower V%s: executed at Layer %s\n' % (self.version, layer)
                    modified_gcode += 'M117 Change heat: %s\n' % temp
                    modified_gcode += 'M104 S%s\n' % temp
                    modified_gcode += '\n'.join(lines[1:])
                    data[index] = modified_gcode
                lastTemp = temp
            
            index += 1
        
        return data