import bpy
import os

def imageFromPath(Img,image_format,isNormal = False):
    Im = bpy.data.images.get(os.path.basename(Img)[:-4])
    if not Im:
        Im = bpy.data.images.new(os.path.basename(Img)[:-4],1,1)
        Im.source = "FILE"
        Im.filepath = Img[:-3]+ image_format
        if isNormal:
            Im.colorspace_settings.name = 'Non-Color'
    return Im