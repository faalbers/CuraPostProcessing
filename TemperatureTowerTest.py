gcodeFile = open('CUTS.gcode', 'r')
data = gcodeFile.read().split('CURALAYERCUT\n')
gcodeFile.close()

if True:
    if True:
        layerStep = 0
        heightStep = 5.0
        tempStep = 5
        
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
                    print('Up Temp on layer in layer %s' % layer)
                    temp += tempStep
                    nextLayerStep += layerStep
            elif heightStep > 0.0 and layerHeight >= nextHeightStep:
                print('Up Temp on height in layer %s and height %s' % (layer, layerHeight))
                temp += tempStep
                nextHeightStep += heightStep
            
            if temp != lastTemp:
                modified_gcode = lines[0] + '\n'
                modified_gcode += 'M117 Change heat: %s\n' % temp
                modified_gcode += 'M104 S%s\n' % temp
                modified_gcode += '\n'.join(lines[1:])
                data[index] = modified_gcode
                lastTemp = temp
            
            index += 1

gcodeFile = open('CUTS_RESULT.gcode', 'w')
gcodeFile.write(''.join(data))
gcodeFile.close()
