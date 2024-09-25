import maya.cmds as cmds
import maya.api.OpenMaya as om
def RealRestTransform(self, input_obj):
    attrArray = [
        "translateX",
        "translateY",
        "translateZ",
        "rotateX",
        "rotateY",
        "rotateZ"
        ]
    for j in range(len(attrArray)):
            BLattrLocked = cmds.getAttr(input_obj + "." + attrArray[j], lock=True)
            if BLattrLocked:
                continue
            else:
                cmds.setAttr(input_obj + "." + attrArray[j],0) 

def FuncScreenSpaceMoTrail():
    def get_active_cam():
        #https://forums.autodesk.com/t5/maya-programming/query-currently-active-viewport-camera/td-p/8814385 
        #i prefer to be conservative on this code. usually the last cam is the one u set active.
        for i in cmds.getPanel(type="modelPanel"):
            cam=cmds.modelEditor(i,q=1,av=1,cam=1)
            cam = cam.split(r"|")[1]
        return cam

    def get_pos(input_obj):
        pos = cmds.xform(input_obj, q=1, ws=1, t=1)
        return om.MVector(pos)
    
    def get_plane_normal(input_plane):
        mx_plane = cmds.xform(input_plane, q=1, m=1, ws=1)            
        return om.MVector(mx_plane[8], mx_plane[9], mx_plane[10])
    
    def ray_plane_intersect(pos_loc, pos_cam, pos_plane, normal_plane):
        vec_cam_n_loc = pos_loc - pos_cam
        vec_cam_n_loc.normalize()
        vec_cam_n_plane = pos_plane - pos_cam
        dotProd_cam_loc___cam_plane = vec_cam_n_loc * vec_cam_n_plane
        if dotProd_cam_loc___cam_plane < 1e-6:
            return

        aa = vec_cam_n_plane / dotProd_cam_loc___cam_plane #dist between cam & plane / cos == 
        bb = aa * vec_cam_n_loc #dist between cam & intersect point
        res = pos_cam + bb * (vec_cam_n_loc)
        return res
    
    f_default_plane_dist = -10
    trg_obj = cmds.ls(sl=1)[0]
    if not trg_obj: 
        print("plz select 1 obj")
        return
    cam_active = get_active_cam()
    nod_plane = cmds.polyPlane(ax=[0,0,1], ch=0, sh=1, sw=1)[0]
    print(trg_obj, cam_active, nod_plane)
    cmds.parent(nod_plane, cam_active)
    RealRestTransform(nod_plane)
    cmds.setAttr(f"{nod_plane}.translateZ", f_default_plane_dist)
    
    pos_trg_obj = get_pos(trg_obj)
    pos_cam_active = get_pos(cam_active)
    pos_nod_plane = get_pos(nod_plane)
    n_plane = get_plane_normal(nod_plane)
    pos_intersect_point  = ray_plane_intersect(pos_trg_obj, pos_cam_active, pos_nod_plane, n_plane)
    
    #run timeline
    f_startframe, f_endframe = cmds.playbackOptions(q=1, min=1), cmds.playbackOptions(q=1, max=1)
    where_was_i = cmds.currentTime(q=1)
    ls_res_world_pos = []
    ls_loc_trg = []
    for i in range(int(f_startframe), int(f_endframe)+1):
        cmds.currentTime(i)
        pos_trg_obj = get_pos(trg_obj)
        pos_cam_active = get_pos(cam_active)
        pos_nod_plane = get_pos(nod_plane)
        n_plane = get_plane_normal(nod_plane)
        pos_intersect_point  = ray_plane_intersect(pos_trg_obj, pos_cam_active, pos_nod_plane, n_plane)
        ls_res_world_pos.append(pos_intersect_point)
        loc_trg = cmds.createNode("transform", name="shitt"+str(i))
        locShape_trg = cmds.createNode("locator", name=f"{loc_trg}Shape", parent=loc_trg)
        ls_loc_trg.append(loc_trg)
        cmds.xform(loc_trg, t=pos_intersect_point)
        cmds.parent(loc_trg, cam_active)
    #tried on calc matrix to do it, failed.
    cmds.currentTime(where_was_i)
    ls_loc_trg_pos = []
    for i in range(len(ls_loc_trg)):
        a = cmds.xform(ls_loc_trg[i], q=1, ws=1, t=1)
        ls_loc_trg_pos.append(a)
    crv_screenSpace_MoTrail = cmds.curve(d=1, p=ls_loc_trg_pos, n="ScreenSpaceMoTrail", ws=1)
    crvShape_screenSpace_MoTrail = cmds.listRelatives(crv_screenSpace_MoTrail, f=1, s=1)[0]
    cmds.setAttr(f"{crvShape_screenSpace_MoTrail}.dispCV", 1)
    cmds.setAttr(f"{crvShape_screenSpace_MoTrail}.overrideEnabled", 1)
    cmds.setAttr(f"{crvShape_screenSpace_MoTrail}.overrideColor", 14)
    cmds.parent(crv_screenSpace_MoTrail, cam_active)
    cmds.delete(nod_plane, ls_loc_trg)
FuncScreenSpaceMoTrail()