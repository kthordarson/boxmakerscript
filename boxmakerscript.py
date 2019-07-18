# Author-kth
# Description-test the box

import adsk.cam
import adsk.core
import adsk.fusion
import traceback


def boxbuilder(height, width, depth, plane, shell_thickness):
    # todo add constrains and dimensions to all sketches....
    mm0 = adsk.core.ValueInput.createByString("0 mm")
    mm10neg = adsk.core.ValueInput.createByString("-10 mm")
    deg0 = adsk.core.ValueInput.createByString("0 deg")

    app = adsk.core.Application.get()
    #    ao = AppObjects()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    rootComp = design.rootComponent
    sketches = rootComp.sketches
    extrudes = rootComp.features.extrudeFeatures
    #    combiner = rootComp.features.combineFeatures
    features = rootComp.features
    units_manager = design.unitsManager

    # Add sketch to selected plane
    sketch = sketches.add(plane)
    sketch.name = "mainoutline"

    sketch.areDimensionsShown = True
    sketch.isVisible = True
    sketchLines = sketch.sketchCurves.sketchLines

    # height = adsk.core.ValueInput.createByString(height)
    # width = adsk.core.ValueInput.createByString(width)
    # depth = adsk.core.ValueInput.createByString(depth)
    # shell_thickness = adsk.core.ValueInput.createByString(shell_thickness)

    height = float(units_manager.formatInternalValue(height, '', False))
    #    variable_message(height)
    width = float(units_manager.formatInternalValue(width, '', False))
    depth = float(units_manager.formatInternalValue(depth, '', False))
    shell_thickness = float(units_manager.formatInternalValue(shell_thickness, '', False))
    # todo get thos from userinput hinge_width
    hinge_widrh = 2
    hinge_distance = 1

    sketchlines = sketch.sketchCurves.sketchLines

    bottomCenter = adsk.core.Point3D.create(0, 0, 0)
    endPt = bottomCenter.copy()  # start from bottomCenter
    endPt.y = bottomCenter.y + height

    sideLine1 = sketchlines.addByTwoPoints(bottomCenter, endPt)

    endPt.x = endPt.x + width
    BottomLine = sketchlines.addByTwoPoints(sideLine1.endSketchPoint, endPt)

    endPt.y = bottomCenter.y
    sideLine2 = sketchlines.addByTwoPoints(BottomLine.endSketchPoint, endPt)

    # endPt.x = BottomLine.endSketchPoint
    endPt.x = bottomCenter.x + width
    topLine = sketchLines.addByTwoPoints(bottomCenter, endPt)

    # constrain sketch
    sideLine1.startSketchPoint.isFixed = True
    sketchConstrains = sketch.geometricConstraints
    sketchConstrains.addHorizontal(topLine)
    sketchConstrains.addCoincident(topLine.startSketchPoint, sideLine1.startSketchPoint)
    sketchConstrains.addCoincident(topLine.endSketchPoint, sideLine2.endSketchPoint)
    sketchConstrains.addHorizontal(BottomLine)
    sketchConstrains.addVertical(sideLine1)
    sketchConstrains.addVertical(sideLine2)

    # dimension lines
    sketchDims = sketch.sketchDimensions

    startPt = sideLine1.startSketchPoint.geometry
    endPt = sideLine1.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.x = textPos.x - 1
    sketchDims.addDistanceDimension(sideLine1.startSketchPoint, sideLine1.endSketchPoint,
                                    adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = topLine.startSketchPoint.geometry
    endPt = topLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.x = textPos.x - 1
    sketchDims.addDistanceDimension(topLine.startSketchPoint, topLine.endSketchPoint,
                                    adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    # get profile for extrude
    profile = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(depth)
    extrude1 = extrudes.addSimple(profile, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body1 = extrude1.bodies.item(0)
    body1.name = 'boxtest1'

    # construction plane to split box horizontally
    # face = body1.faces.item(0)
    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    planeInput.setByTwoPlanes(body1.faces.item(0), body1.faces.item(2))
    split_plane = planes.add(planeInput)
    split_plane.name = 'splitplane'

    # construction plane in middle of box vertical
    planeInput.setByTwoPlanes(body1.faces.item(5), body1.faces.item(4))
    hinge_plane = planes.add(planeInput)
    hinge_plane.name = 'hinge_plane'

    # Create SplitBodyFeatureInput
    splitBodyFeats = rootComp.features.splitBodyFeatures
    splitBodyInput = splitBodyFeats.createInput(body1, split_plane, True)

    # Create split body feature
    split = splitBodyFeats.add(splitBodyInput)
    splitbodies = split.bodies
    lid_body = splitbodies.item(0)
    bottom_body = splitbodies.item(1)
    lid_body.name = "lid"
    bottom_body.name = "bottom"

    # shell bodies
    entities1 = adsk.core.ObjectCollection.create()
    entities1.add(lid_body.faces.item(5))
    entities1.add(bottom_body.faces.item(0))
    shellFeats = features.shellFeatures
    isTangentChain = False
    shellFeatureInput = shellFeats.createInput(entities1, isTangentChain)
    thickness = adsk.core.ValueInput.createByReal(shell_thickness)
    shellFeatureInput.insideThickness = thickness
    shellFeats.add(shellFeatureInput)

    # sketch for hinges on lid
    # todo get 10mm and other from userinput
    hinge_sketch = sketches.add(hinge_plane)
    hinge_sketch.name = "lidhinges"
    lid_projection = hinge_sketch.project(lid_body.faces.item(8))
    sketchlines = hinge_sketch.sketchCurves.sketchLines
    point1 = lid_projection.item(0).geometry.x
    point2 = lid_projection.item(0).geometry.y
    hinge_firstPoint = adsk.core.Point3D.create(point1, point2, 0)
    endPt = hinge_firstPoint.copy()
    endPt.y = hinge_firstPoint.y + 2.5
    hinge_line1 = sketchlines.addByTwoPoints(hinge_firstPoint, endPt)

    hinge_nextpoint = hinge_firstPoint
    hinge_nextpoint.x -= 1
    hinge_line2 = sketchlines.addByTwoPoints(hinge_nextpoint, endPt)
    hinge_nextpoint = hinge_firstPoint
    endPt.y = 0
    hinge_line2 = sketchlines.addByTwoPoints(hinge_nextpoint, endPt)

    # extrude hinges
    mm10 = adsk.core.ValueInput.createByString("-10 mm")
    profile = hinge_sketch.profiles.item(0)
    extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent_distance = adsk.fusion.DistanceExtentDefinition.create(mm10)

    start_from = adsk.fusion.FromEntityStartDefinition.create(lid_body.faces.item(5), mm10)
    extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    extrudeInput.startExtent = start_from
    # Create the extrusion
    extrude3 = extrudes.add(extrudeInput)
    hinge1_body = extrude3.bodies.item(0)
    hinge1_body.name = "hingetop1"

    # extrude second hinge from hinge1 face4
    mm10 = adsk.core.ValueInput.createByString("10 mm")
    start_from = adsk.fusion.FromEntityStartDefinition.create(hinge1_body.faces.item(4), mm10)
    extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    extrudeInput.startExtent = start_from
    # Create the extrusion
    extrude3 = extrudes.add(extrudeInput)
    hinge2_body = extrude3.bodies.item(0)
    hinge2_body.name = "hingetop2"

    # todo maybe create hinges with pattern on path ?

    # Create input entities for mirror feature
    inputEntites = adsk.core.ObjectCollection.create()
    for all_bodies in rootComp.bRepBodies:
        if "hingetop" in all_bodies.name:
            inputEntites.add(all_bodies)

    # Create the input for mirror feature
    mirrorFeatures = features.mirrorFeatures
    mirrorInput = mirrorFeatures.createInput(inputEntites, hinge_plane)

    # Create the mirror feature
    mirrorFeature = mirrorFeatures.add(mirrorInput)
    hinge3_body = mirrorFeature.bodies.item(0)
    hinge3_body.name = "hingetop3"
    hinge4_body = mirrorFeature.bodies.item(1)
    hinge4_body.name = "hingetop4"

    # sketch for hinges on bottom
    # todo get offset and size from userinput
    hinge_sketch = sketches.add(bottom_body.faces.item(9))
    hinge_sketch.name = "bottomhinges"
    # hinge1face4, hinge2face3
    hinge_projection1 = hinge_sketch.project(hinge1_body.faces.item(4))
    hinge_projection2 = hinge_sketch.project(hinge2_body.faces.item(3))
    sketchlines = hinge_sketch.sketchCurves.sketchLines
    point1 = hinge_projection1.item(0).geometry.x + 1
    point2 = hinge_projection1.item(0).geometry.y
    hinge_firstPoint = adsk.core.Point3D.create(point1, point2, 0)
    point1 = hinge_projection2.item(0).geometry.x + 1
    point2 = hinge_projection2.item(0).geometry.y
    hinge_nextpoint = adsk.core.Point3D.create(point1, point2, 0)
    # endPt = hinge_firstPoint.copy()
    # endPt.y = hinge_firstPoint.y +2
    hinge_topline = sketchlines.addByTwoPoints(hinge_firstPoint, hinge_nextpoint)

    point1 = hinge_projection1.item(0).geometry.x - 1
    point2 = hinge_projection1.item(0).geometry.y
    hinge_firstPoint = adsk.core.Point3D.create(point1, point2, 0)
    point1 = hinge_projection2.item(0).geometry.x - 1
    point2 = hinge_projection2.item(0).geometry.y
    hinge_nextpoint = adsk.core.Point3D.create(point1, point2, 0)
    # endPt = hinge_firstPoint.copy()
    # endPt.y = hinge_firstPoint.y +2
    hinge_bottomline = sketchlines.addByTwoPoints(hinge_firstPoint, hinge_nextpoint)

    # hinge sideline1
    # todo get "-1" from userinput, this is distance offset from side
    point1 = hinge_projection1.item(0).geometry.x - 1
    hinge_firstPoint = adsk.core.Point3D.create(point1, hinge_topline.endSketchPoint.geometry.y, 0)

    point1 = hinge_topline.endSketchPoint.geometry.x
    point2 = hinge_topline.endSketchPoint.geometry.y
    hinge_nextpoint = adsk.core.Point3D.create(point1, point2, 0)
    hinge_sideline1 = sketchlines.addByTwoPoints(hinge_firstPoint, hinge_nextpoint)

    # hinge sideline2
    point1 = hinge_projection1.item(0).geometry.x
    hinge_firstPoint = adsk.core.Point3D.create(point1, hinge_topline.startSketchPoint.geometry.y, 0)

    point1 = hinge_bottomline.startSketchPoint.geometry.x
    point2 = hinge_bottomline.startSketchPoint.geometry.y
    hinge_nextpoint = adsk.core.Point3D.create(point1, point2, 0)
    hinge_sideline2 = sketchlines.addByTwoPoints(hinge_firstPoint, hinge_nextpoint)

    # extrude bottom hinges
    profile_collection = adsk.core.ObjectCollection.create()
    profile_collection.add(hinge_sketch.profiles.item(1))
    profile_collection.add(hinge_sketch.profiles.item(2))

    ext_input = extrudes.createInput(profile_collection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # todo get distance from userinput
    distance_input = adsk.core.ValueInput.createByReal(1.0)
    ext_input.setDistanceExtent(False, distance_input)
    hinge_bottom1 = extrudes.add(ext_input)
    hinge_bottom1_body = hinge_bottom1.bodies.item(0)
    hinge_bottom1_body.name = "hingebottom1"

    # mirror bottom hinge around hinge_plane
    # Create input entities for mirror feature
    inputEntites = adsk.core.ObjectCollection.create()
    inputEntites.add(hinge_bottom1_body)

    # Create the input for mirror feature
    mirrorFeatures = features.mirrorFeatures
    mirrorInput = mirrorFeatures.createInput(inputEntites, hinge_plane)

    # Create the mirror feature
    mirrorFeature = mirrorFeatures.add(mirrorInput)
    hinge_bottom2 = mirrorFeature.bodies.item(0)
    hinge_bottom2.name = "hingebottom2"

    # join hinges 1 -4 with lid_body
    # todo fix this somehow....
    ToolBodies = adsk.core.ObjectCollection.create()
    for all_bodies in rootComp.bRepBodies:
        if "hingetop" in all_bodies.name:
            ToolBodies.add(all_bodies)
    combineInput = features.combineFeatures.createInput(lid_body, ToolBodies)
    combineInput.isNewComponent = False
    lidcombined = features.combineFeatures.add(combineInput)

    #  join hinges on bottom with bottom_body
    ToolBodies = adsk.core.ObjectCollection.create()
    for all_bodies in rootComp.bRepBodies:
        if "hingebottom" in all_bodies.name:
            ToolBodies.add(all_bodies)
    combineInput = features.combineFeatures.createInput(bottom_body, ToolBodies)
    combineInput.isNewComponent = False
    lidcombined = features.combineFeatures.add(combineInput)

    #  make hole through all hinges...sketch on lid_body face index 10....
    pinsketch = sketches.add(lid_body.faces.item(10))
    pinsketch.name = "pinsketch"
    projection = pinsketch.project(lid_body.faces.item(10))

    # todo fix coordinates and size
    point1 = projection.item(0).startSketchPoint.geometry.x
    point2 = projection.item(0).endSketchPoint.geometry.x
    point3 = point1 - point2
    circles = pinsketch.sketchCurves.sketchCircles
    circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(point2, -0.4, 0), 0.3)

    # todo create collection for profile to extrude....
    profile_collection = adsk.core.ObjectCollection.create()
    profile_collection.add(pinsketch.profiles.item(1))
    profile_collection.add(pinsketch.profiles.item(0))

    #    extrude_circle_input = extrudes.createInput(pinsketch.profiles.item(1), adsk.fusion.FeatureOperations.CutFeatureOperation)
    #    extrude_circle_input = extrudes.createInput(pinsketch.profiles.item(1), adsk.fusion.FeatureOperations.CutFeatureOperation)
    extrude_circle_input = extrudes.createInput(profile_collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    extent_all = adsk.fusion.ThroughAllExtentDefinition.create()
    extrude_circle_input.setOneSideToExtent(lid_body.faces.item(4), False)
    # extrude_circle_input.setAllExtent( adsk.fusion.ExtentDirections.NegativeExtentDirection)
    # extrude_circle_input.setDistanceExtent(False, mm10neg)

    circle_cut = extrudes.add(extrude_circle_input)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # app = adsk.core.Application.get()
        product = app.activeProduct

        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent

        # ui.messageBox('Select plane')

        # planeSelection = ui.selectEntity('Select plane', 'ConstructionPlanes')
        # print(planeSelection)
        # inputs.addSelectionInput('plane', 'Plane Selection', 'Select starting plane')
        boxbuilder(12, 15, 30, rootComp.xZConstructionPlane, 0.5)

    except Exception as E:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    finally:
        pass
