"""
log:
2023.10.13
change lang from Mel to Py.
Now it can deal with the locked & hiden attr.
"""


import maya.cmds as cmds


selectedObjects = cmds.ls(selection = True)#string array
attrArray = [
    "translateX",
    "translateY",
    "translateZ",
    "rotateX",
    "rotateY",
    "rotateZ"
    ]
for i in range(len(selectedObjects)):
    for j in range(len(attrArray)):
        BLattrLocked = cmds.getAttr(selectedObjects[i] + "." + attrArray[j], lock=True)
        if BLattrLocked:
            continue
        else:
            cmds.setAttr(selectedObjects[i] + "." + attrArray[j],0) 
        

