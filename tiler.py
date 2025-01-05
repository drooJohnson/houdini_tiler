import hou
import os
import datetime

def fit(input, oldmin, oldmax, newmin, newmax):
    return (((input - oldmin) * (newmax - newmin)) / (oldmax - oldmin)) + newmin

def tile_camera(camera_path, rop_path, xtiles=2, ytiles=2, parent_obj="/obj"):
    root = hou.node(parent_obj)
    if root is None:
        if (hou.node("/obj/CAMERA_TILES")):
            hou.node("/obj/CAMERA_TILES").destroy();
        root = hou.node("/obj").createNode("subnet", "CAMERA_TILES")
        root.setDisplayFlag(False)
    cam = hou.node(camera_path)
    fetch = root.createNode("fetch")
    fetch.parm("useinputoffetched").set(1)
    fetch.parm("fetchobjpath").set(camera_path)
    fetch.setDisplayFlag(0)

    # get node reference to original rop
    rop = hou.node(rop_path)

    # create ropnet
    ropnet = root.createNode("ropnet", "TILE_OUTPUTS")
    output = ropnet.createNode("merge", "OUT")

    for y in range(0, ytiles):
        for x in range(0, xtiles):
            # duplicate camera and reset transform.
            newcam = root.copyItems([cam], channel_reference_originals=True)[0]
            newcam.setInput(0, fetch)
            # clear channel references for things we have to modify
            newcam.parm("winx").deleteAllKeyframes()
            newcam.parm("winy").deleteAllKeyframes()
            newcam.parm("winsizex").deleteAllKeyframes()
            newcam.parm("winsizey").deleteAllKeyframes()
            zoomx = 1.0 / xtiles
            zoomy = 1.0 / ytiles
            newcam.parm("winsizex").set(zoomx)
            newcam.parm("winsizey").set(zoomy)
            # clear transform channel references.
            # looping this way is shorthand for clearing and setting parameters for 'tx', 'ty', 'tz', etc.
            for ch in ['t','r']:
                for dim in ['x','y','z']:
                    newcam.parm(ch+dim).deleteAllKeyframes()
                    newcam.parm(ch+dim).set(0)

            centerx = (float(x) * zoomx) + (zoomx / 2)
            centery = (float(y) * zoomy) + (zoomy / 2)
            nx = fit(centerx, 0, 1, -1, 1) * 0.5
            ny = fit(centery, 0, 1, -1, 1) * 0.5
            newcam.parm("winx").set(nx)
            newcam.parm("winy").set(ny)

            # now set camera resolution to be a single tile width.
            orig_resx = cam.evalParm("resx")
            orig_resy = cam.evalParm("resy")
            newcam.parm("resx").deleteAllKeyframes()
            newcam.parm("resy").deleteAllKeyframes()
            newcam.parm("resx").set(orig_resx / xtiles)
            newcam.parm("resy").set(orig_resy / ytiles)

            # set camera name
            tilenum = "u{}_v{}".format(str(x).zfill(2), str(y).zfill(2))
            newcam.setName(cam.name() + "_{}".format(tilenum), True)

            # duplicate rop and set camera
            newrop = ropnet.copyItems([rop], channel_reference_originals=True)[0]
            newrop.setName(cam.name() + "_{}".format(tilenum), True)
            newrop.parm('RS_renderCamera').deleteAllKeyframes()
            newrop.parm('RS_renderCamera').set(newcam.path())

            # set output to match input, with UVtile as containing directory
            outpathparm = rop.evalParm("RS_outputFileNamePrefix")
            outpathsubdir = datetime.datetime.now().strftime('%Y%m%d_%H%M%S');
            outpath = os.path.join(os.path.dirname(outpathparm), outpathsubdir, (newrop.name() + os.path.basename(outpathparm))).replace("\\","/")
            newrop.parm("RS_outputFileNamePrefix").deleteAllKeyframes()
            newrop.parm("RS_outputFileNamePrefix").set(outpath)

            # merge with ROP network's output
            output.setNextInput(newrop)    
    # cleanup
    root.layoutChildren()
    ropnet.layoutChildren()
    
    ropnet.parm('execute').pressButton();
    
tile_camera("/obj/cam1", "/out/Redshift_ROP1", 4, 4, "/obj/CAM_TILES")
