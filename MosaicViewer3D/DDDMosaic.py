import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# DDDMosaic
#

class DDDMosaic:
  def __init__(self, parent):
    parent.title = "DDD Mosaic"
    parent.categories = ["Wizards"]
    parent.dependencies = []
    parent.contributors = ["Sebastian Rubio (ID:450274473 - USydney)"]
    parent.helpText = """Assignment COMP5424 S1 2015 - This module create a 3D Mosaic Viewer 
    for Volumes (NRRD files) and Models (VTK files) """
    parent.acknowledgementText = """
        """ 

    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['DDDMosaic'] = self.runTest

  def runTest(self):
    tester = DDDMosaicTest()
    tester.runTest()

#
# DDDMosaicWidget
#
class DDDMosaicWidget:

  def __init__(self, parent = None):
    settings = qt.QSettings()
    self.developerMode = settings.value('Developer/DeveloperMode').lower() == 'true'
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.layerReveal = None

  def setup(self):
    if self.developerMode:
      #
      # Reload and Test area
      #
      reloadCollapsibleButton = ctk.ctkCollapsibleButton()
      reloadCollapsibleButton.text = "Reload && Test"
      self.layout.addWidget(reloadCollapsibleButton)
      reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

      # reload button
      self.reloadButton = qt.QPushButton("Reload")
      self.reloadButton.toolTip = "Reload this module"
      self.reloadButton.name = "DDDMosaic Reload"
      reloadFormLayout.addWidget(self.reloadButton)
      self.reloadButton.connect('clicked()', self.onReload)

      # reload and test button
      # reload and run specific tests
      scenarios = ('Volume','Model')#'SceneView','All'

      for scenario in scenarios:
        button = qt.QPushButton("Reload and Test %s" % scenario)
        button.toolTip = "Reload this module and then run the self test on %s." % scenario
        reloadFormLayout.addWidget(button)
        button.connect('clicked()', lambda s = scenario: self.onReloadAndTest(scenario = s))

    #
    # Mosaic Area
    #
    mosaicCollapsibleButton = ctk.ctkCollapsibleButton()
    mosaicCollapsibleButton.text = 'Mosaic Viewer 3D'
    self.layout.addWidget(mosaicCollapsibleButton)
    mosaicLayout = qt.QFormLayout(mosaicCollapsibleButton)

    self.applyButtonV = qt.QPushButton("Apply 3D Mosaic Volume")
    self.applyButtonV.toolTip = "Apply Volume"
    mosaicLayout.addRow(self.applyButtonV)
    self.applyButtonV.connect('clicked()', self.onApplyVolume)

    self.applyButtonM = qt.QPushButton("Apply 3D Mosaic Model")
    self.applyButtonM.toolTip = "Apply Model"
    mosaicLayout.addRow(self.applyButtonM)
    self.applyButtonM.connect('clicked()', self.onApplyModel)

    self.applyButtonA = qt.QPushButton("Apply All 3D Mosaic")
    self.applyButtonA.toolTip = "Apply Model-Volume"
    mosaicLayout.addRow(self.applyButtonA)
    self.applyButtonA.connect('clicked()', self.onApplyAll)

    """self.applyButtonS = qt.QPushButton("Apply Mosaic 3D SceneView")
    self.applyButtonS.toolTip = "Apply SceneView"
    mosaicLayout.addRow(self.applyButtonS)
    self.applyButtonS.connect('clicked()', self.onApplyScene)"""

    # Add vertical spacer
    self.layout.addStretch(1)

  def onApplyVolume(self):
    volumes = slicer.util.getNodes('*VolumeNode*')
    volumeNames = [n.GetName() for n in volumes.values()]
    #print "volume",volumes.values()
    logic = DDDMosaicLogic()
    logic.viewerPerVolume(nodes = volumes, sceneviewNames = volumeNames)

  def onApplyModel(self):
    models = slicer.util.getNodes('*ModelNode*')
    del models['Red Volume Slice'];
    del models['Yellow Volume Slice'];
    del models['Green Volume Slice'];
    #print "models",models.values()
    modelNames = [n.GetName() for n in models.values()]
    #print "models",modelNames
    logic = DDDMosaicLogic()
    logic.viewerPerModel(nodes = models, sceneviewNames = modelNames)

  #Render Volumes and Models in a 3D mosaic
  def onApplyAll(self):
    volumes = slicer.util.getNodes('*VolumeNode*')
    models = slicer.util.getNodes('*ModelNode*')
    del models['Red Volume Slice'];
    del models['Yellow Volume Slice'];
    del models['Green Volume Slice'];
    volumeNames = [n.GetName() for n in volumes.values()]
    modelNames = [n.GetName() for n in models.values()]
    volumes.update(models)
    namesVM=volumeNames+modelNames
    #print "volumes",volumes
    #print "Names",names
    logic = DDDMosaicLogic()
    #logic.makeViewer(nodes = volumes, sceneviewNames = names)
    logic.viewerPerAll(nodes = volumes, sceneviewNames = namesVM)

  """def onApplyScene(self):
    scenes = slicer.util.getNodes('*SceneView*')
    sceneNames = [n.GetName() for n in volumes.values()]
    #print "volume",volumes
    logic = DDDMosaicLogic()
    logic.viewerPerScene(nodes = scenes, sceneviewNames = sceneNames)"""

  def onReload(self,moduleName="DDDMosaic"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    print moduleName," has been reloaded"
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="DDDMosaic",scenario=None):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario=scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),"Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

#
# DDDMosaicLogic
#

class DDDMosaicLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
#vtkMRMLSliceNode - (CompareVolumes) 
  def __init__(self):
    self.DDDViewPattern = """
      <item><view class="vtkMRMLViewNode" singletontag="{viewName}">
        <property name="viewlabel" action="default">{viewName}</property>
      </view></item>
     """

  def assignLayoutDescription(self,layoutDescription):
    """assign the xml to the user-defined layout slot"""
    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

  def makeViewer(self, nodes = None, sceneviewNames = []):

    # make an array with wide screen aspect ratio
    import math

    row = 0
    column = 0

    c = 1.0 * math.sqrt(len(nodes))
    column = math.floor(c)
    if c != column:
      column += 1
    if column > len(nodes):
      columns = len(nodes)
    r = len(nodes)/column
    row = math.floor(r)
    if r != row:
      row += 1

    #
    # construct the XML for the layout
    # - one viewer per volume
    # - default orientation as specified
    #
    actualSceneView = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    for ro in range(int(row)):
      layoutDescription += ' <item> <layout type="horizontal">\n'
      for col in range(int(column)):
        try:
          viewName = sceneviewNames[index - 1]
        except IndexError:
          viewName = '%d_%d' % (ro,col)
        layoutDescription += self.DDDViewPattern.format(viewName = viewName)
        actualSceneView.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)
    # let the widgets all decide how big they should be
    slicer.app.processEvents()
    return actualSceneView

  def viewerPerVolume(self, nodes = None, sceneviewNames = []):

    if not nodes:
      nodes = slicer.util.getNodes('*VolumeNode*')

    if len(nodes) == 0 :
      print "No files charged!"
      return 

    layoutManager = slicer.app.layoutManager()
    actualSceneView = self.makeViewer(nodes, sceneviewNames)

    for index in range(len(nodes)):
      viewName = actualSceneView[index]
      try:
        nodeID = slicer.util.getNode(viewName)
      except IndexError:
        nodeID = ""

      threeDWidget = layoutManager.threeDWidget(index+1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      # Volume Rendering module is used
      logic = slicer.modules.volumerendering.logic()
      displayNode = logic.CreateVolumeRenderingDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      displayNode.UnRegister(logic)
      displayNode.AddViewNodeID(viewNode.GetID())
      logic.UpdateDisplayNodeFromVolumeNode(displayNode, nodeID)
      displayNode.SetVisibility(True)
      nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())

      print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewName,'\n'

  def viewerPerModel(self, nodes = None, sceneviewNames = []):

    if len(nodes) == 0 :
      print "No files charged!"
      return 

    layoutManager = slicer.app.layoutManager()
    actualSceneView = self.makeViewer(nodes, sceneviewNames)
	
    for index in range(len(nodes)):
      viewName = actualSceneView[index]
      try:
        nodeID = slicer.util.getNode(viewName)
      except IndexError:
        nodeID = ""

      threeDWidget = layoutManager.threeDWidget(index+1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      displayNode = nodeID.GetDisplayNode()
      nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
      displayNode.AddViewNodeID(viewNode.GetID())
      displayNode.SetVisibility(True)

      print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewName,'\n'

  def viewerPerAll(self, nodes = None, sceneviewNames = []):

    if len(nodes) == 0 :
      print "No files charged!"
      return 

    layoutManager = slicer.app.layoutManager()
    actualSceneView = self.makeViewer(nodes, sceneviewNames)
    #print "model: ",nodes[0]
    for index in range(len(nodes)):
      viewName = actualSceneView[index]
      threeDWidget = layoutManager.threeDWidget(index+1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      if "ModelNode" in nodes[viewName].GetID():
        viewN = viewName
        #print "model: ",viewN
        try:
          nodeID = slicer.util.getNode(viewN)
        except IndexError:
          nodeID = ""

        displayNode = nodeID.GetDisplayNode()
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.AddViewNodeID(viewNode.GetID())
        displayNode.SetVisibility(True)
        print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewN,'\n'

      if "VolumeNode" in nodes[viewName].GetID():
        viewN = viewName
        #print "volume: ",viewN
        try:
          nodeID = slicer.util.getNode(viewN)
        except IndexError:
          nodeID = ""

        # Volume Rendering module is used
        logic = slicer.modules.volumerendering.logic()
        displayNode = logic.CreateVolumeRenderingDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        displayNode.UnRegister(logic)
        displayNode.AddViewNodeID(viewNode.GetID())
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, nodeID)
        displayNode.SetVisibility(True)
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())

        print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewN,'\n'

  #method to test all files----------------Doesn't work!! ??
  def T_viewerPerAll(self, nodes = None, sceneviewNames = [],files=[]):

    if len(files) == 0 :
      print "No files charged!"
      return 

    layoutManager = slicer.app.layoutManager()
    actualSceneView = self.makeViewer(nodes, sceneviewNames)

    index=0
    for n in files: 
      threeDWidget = layoutManager.threeDWidget(index+1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      if ".vtk" in n:
        viewN = n[:len(n)-4]
        #print "T_viewerPerAll model: ",viewN
        try:
          nodeID = slicer.util.getNode(viewN)
          #print "T_viewerPerAll Model: ",nodeID
        except IndexError:
          nodeID = ""

        displayNode = nodeID.GetDisplayNode()
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.AddViewNodeID(viewNode.GetID())
        displayNode.SetVisibility(True)
        print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewN,'\n'

      if ".nrrd" in n:
        viewN = n[:len(n)-5]
        #print "T_viewerPerAll volume: ",viewN
        try:
          nodeID = slicer.util.getNode(viewN)
          #print "T_viewerPerAll Volume: ",nodeID
        except IndexError:
          nodeID = ""

        # Volume Rendering module is used
        logic = slicer.modules.volumerendering.logic()
        displayNode = logic.CreateVolumeRenderingDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        displayNode.UnRegister(logic)
        displayNode.AddViewNodeID(viewNode.GetID())
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, nodeID)
        displayNode.SetVisibility(True)
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())

        print "Node Index: ", index,'\nView Node ID: ', viewNode.GetID(),'\nView Name: ', viewN,'\n'
      index+=1

  #INCOMPLETE-------------------------------------------------
  def viewerPerScene(self, nodes = None, sceneviewNames = []):
    if not nodes:
      nodes = slicer.util.getNodes('*SceneView*')

    if len(nodes) == 0 :
      print "No files charged!"
      return 

    layoutManager = slicer.app.layoutManager()
    actualSceneView = self.makeViewer(nodes, sceneviewNames)

    for index in range(len(nodes)):
      viewName = actualSceneView[index]
      #print "viewName",viewName
      try:
        nodeID = slicer.util.getNode(viewName)
      except IndexError:
        nodeID = ""

      threeDWidget = layoutManager.threeDWidget(index+1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      # model module is used
      displayNode = nodeID.GetDisplayNode()
      nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
      displayNode.AddViewNodeID(viewNode.GetID())
      displayNode.SetVisibility(True)

      print "Node Index: ", index, '\nView Node ID: ', viewNode.GetID()
    """scene = slicer.mrmlScene

    lViewNode   = scene.GetNodesByClass('vtkMRMLViewNode')

    for v in range(lViewNode.GetNumberOfItems()):
      viewNodeToRemove    = lViewNode.GetItemAsObject(v)
      print ' - Removed view: ', viewNodeToRemove.GetName()
      scene.RemoveNode(viewNodeToRemove)

    lCameraNode = scene.GetNodesByClass('vtkMRMLCameraNode')
    for c in range(lCameraNode.GetNumberOfItems()):
      cameraNodeToRemove  = lCameraNode.GetItemAsObject(c)
      print ' - Removed camera: ', cameraNodeToRemove.GetName()
      scene.RemoveNode(cameraNodeToRemove)

    sceneViews = slicer.util.getNodes('*vtkMRMLSceneViewNode*')# searching loaded SceneViews
    scenes   = [n for n in sceneViews.values()]

    if len(scenes) == 0 :
      return 

    sceneNames = [n.GetName() for n in scenes]
    sceneNames.sort()# SSort Scene views"""

#
# DDDMosaicTest
#   
class DDDMosaicTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """ 
 
  def delaydisplay(self,message,msec = 2000):
    """This utility method dissplays a small disalog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self,scenario=None):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    if scenario == "Volume":
      self.testDDDMosaicVolume()
    elif scenario == "Model":
      self.testDDDMosaicModel()
    elif scenario == "SceneView":#INCOMPLETE
      self.testDDDMosaicSceneView()
    elif scenario == "All":
      self.testDDDMosaicAll()#Volumes and Models

  def testDDDMosaicVolume(self):
    """ Test modes with 6 volumes.
    """

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('DDDMosaic')
    self.setUp()
    volumes = []
    volumeNames = []

    self.delaydisplay("Starting Volume test, loading data")

    fPath = eval('slicer.modules.dddmosaic.path')
    fdir = os.path.dirname(fPath) + '/Resources/VolumesExamples'

    for f in os.listdir(fdir):
      if f.endswith(".nrrd"):
          slicer.util.loadVolume(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          volumes.append(fName)
          volumeNames.append(fName)

    logic = DDDMosaicLogic()
    logic.viewerPerVolume(nodes = volumes, sceneviewNames = volumeNames)
    self.delaydisplay("Volume Test Successful!")

  def testDDDMosaicModel(self):
    """ Test modes with 9 models.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('DDDMosaic')
    self.setUp()
    models = []
    modelNames = []
    
    self.delaydisplay("Starting Model test, loading data")

    fPath = eval('slicer.modules.dddmosaic.path')

    fdir = os.path.dirname(fPath) + '/Resources/ModelsExamples'

    for f in os.listdir(fdir):
      if f.endswith(".vtk"):
          slicer.util.loadModel(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          models.append(fName)
          modelNames.append(fName)

    logic = DDDMosaicLogic()
    logic.viewerPerModel(nodes = models, sceneviewNames = modelNames)
    self.delaydisplay("Model Test Successful!")

  #the implemented method (T_viewerPerAll) to be invoked doesn't work!! ??
  def testDDDMosaicAll(self):
    """ Test modes with 6 volumes and 10 models.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('DDDMosaic')
    self.setUp()
    models = []
    modelNames = []

    self.delaydisplay("Starting Volume and Model test, loading data")

    fPath = eval('slicer.modules.dddmosaic.path')

    fdir = os.path.dirname(fPath) + '/Resources/AllExamples'
    fileNames = []
    for f in os.listdir(fdir):
      if f.endswith(".vtk") or f.endswith(".nrrd"):
          slicer.util.loadModel(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          fileNames.append(fName+fExtension)
          models.append(fName)
          modelNames.append(fName)

    logic = DDDMosaicLogic()
    logic.T_viewerPerAll(nodes = models, sceneviewNames = modelNames,files=fileNames)
    self.delaydisplay("Model Test Successful!")

  #INCOMPLETE-------------------------------------------------
  def testDDDMosaicSceneView(self):
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('DDDMosaic')
    self.setUp()
    scenes = []
    sceneNames = []

    self.delaydisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.dddmosaic.path')

    fdir = os.path.dirname(fPath) + '/Resources/SceneViewExamples'

    for f in os.listdir(fdir):
      if f.endswith(".mrml"):
          slicer.util.loadModel(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          scenes.append(fName)
          sceneNames.append(fName)

    logic = DDDMosaicLogic()
    logic.viewerPerScene(nodes = scenes, sceneviewNames = sceneNames)