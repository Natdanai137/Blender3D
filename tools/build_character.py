import bpy
import math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 0.72
    return m

cream = material('Warm ivory suit', (0.88, 0.84, 0.66))
teal = material('Sea glass jacket', (0.10, 0.48, 0.49))
dark = material('Midnight boots and belt', (0.055, 0.13, 0.18))
coral = material('Coral trim', (0.92, 0.33, 0.25))
skin = material('Face', (0.94, 0.65, 0.44))
hair = material('Chestnut hair', (0.25, 0.14, 0.11))
white = material('Eye white', (0.96, 0.95, 0.84))
black = material('Eye pupil', (0.03, 0.05, 0.06))

arm_data = bpy.data.armatures.new('Mixamo compatible rig')
rig = bpy.data.objects.new('Armature', arm_data)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')

def bone(name, head, tail, parent=None):
    b = arm_data.edit_bones.new('mixamorig_' + name)
    b.head = head
    b.tail = tail
    if parent:
        b.parent = arm_data.edit_bones['mixamorig_' + parent]
    return b

bone('Hips', (0, 0, 1.02), (0, 0, 1.19))
bone('Spine', (0, 0, 1.19), (0, 0, 1.39), 'Hips')
bone('Spine1', (0, 0, 1.39), (0, 0, 1.62), 'Spine')
bone('Spine2', (0, 0, 1.62), (0, 0, 1.81), 'Spine1')
bone('Neck', (0, 0, 1.81), (0, 0, 1.94), 'Spine2')
bone('Head', (0, 0, 1.94), (0, 0, 2.22), 'Neck')
for side, sign in [('Left', 1), ('Right', -1)]:
    bone(side+'Shoulder', (sign*.28, 0, 1.72), (sign*.42, 0, 1.70), 'Spine2')
    bone(side+'Arm', (sign*.42, 0, 1.70), (sign*.70, 0, 1.49), side+'Shoulder')
    bone(side+'ForeArm', (sign*.70, 0, 1.49), (sign*.91, 0, 1.30), side+'Arm')
    bone(side+'Hand', (sign*.91, 0, 1.30), (sign*1.02, 0, 1.21), side+'ForeArm')
    bone(side+'UpLeg', (sign*.17, 0, 1.02), (sign*.19, 0, .58), 'Hips')
    bone(side+'Leg', (sign*.19, 0, .58), (sign*.19, 0, .13), side+'UpLeg')
    bone(side+'Foot', (sign*.19, 0, .13), (sign*.19, -.16, .08), side+'Leg')
    bone(side+'ToeBase', (sign*.19, -.16, .08), (sign*.19, -.27, .08), side+'Foot')
    for finger, offset in [('Thumb', -.065), ('Index', -.035), ('Middle', 0), ('Ring', .035), ('Pinky', .065)]:
        parent = side+'Hand'
        for index in range(1, 5):
            x = sign*(1.00 + index*.035)
            b = bone(side+'Hand'+finger+str(index), (x, offset, 1.21), (x+sign*.034, offset, 1.20), parent)
            parent = side+'Hand'+finger+str(index)
bpy.ops.object.mode_set(mode='OBJECT')
rig.select_set(False)

def bind(obj, bone_name):
    group = obj.vertex_groups.new(name='mixamorig_'+bone_name)
    group.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    mod = obj.modifiers.new('Skin to Mixamo rig', 'ARMATURE')
    mod.object = rig
    obj.parent = rig
    return obj

def cube(name, loc, scale, mat, bone_name, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft corners', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    return bind(obj, bone_name)

def ico(name, loc, radius, mat, bone_name, scale=(1,1,1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return bind(obj, bone_name)

# Facing Blender -Y, which becomes Godot's forward direction after glTF import.
cube('Jacket torso', (0, 0, 1.50), (.61, .34, .66), teal, 'Spine1', .075)
cube('Belt', (0, 0, 1.12), (.56, .37, .11), dark, 'Hips', .018)
cube('Belt buckle', (0, -.195, 1.12), (.11, .025, .09), coral, 'Hips', .01)
cube('Chest badge', (.13, -.19, 1.63), (.13, .035, .13), coral, 'Spine2', .015)
cube('Collar', (0, 0, 1.81), (.42, .37, .13), cream, 'Spine2', .025)
ico('Head', (0, -.005, 2.13), .25, skin, 'Head', (1, .88, 1.12))
cube('Hair cap', (0, .025, 2.34), (.51, .43, .12), hair, 'Head', .04)
cube('Hair fringe', (-.11, -.18, 2.29), (.24, .10, .10), hair, 'Head', .025)
for side, sign in [('Left', 1), ('Right', -1)]:
    ico(side+' ear', (sign*.245, 0, 2.13), .07, skin, 'Head', (.6, 1, 1.1))
    ico(side+' eye white', (sign*.095, -.221, 2.16), .052, white, 'Head', (1, .32, 1.12))
    ico(side+' eye pupil', (sign*.095, -.241, 2.15), .027, black, 'Head', (1, .28, 1.05))
    cube(side+' shoulder', (sign*.40, 0, 1.70), (.23, .30, .22), coral, side+'Shoulder', .04)
    cube(side+' upper sleeve', (sign*.55, 0, 1.57), (.23, .25, .34), teal, side+'Arm', .035)
    cube(side+' forearm', (sign*.80, 0, 1.39), (.18, .20, .28), cream, side+'ForeArm', .03)
    ico(side+' glove', (sign*.98, 0, 1.25), .11, dark, side+'Hand', (1.1, .8, .85))
    cube(side+' trouser', (sign*.18, 0, .80), (.25, .30, .46), cream, side+'UpLeg', .035)
    cube(side+' lower leg', (sign*.19, 0, .37), (.21, .25, .40), cream, side+'Leg', .02)
    cube(side+' boot', (sign*.19, -.07, .12), (.27, .41, .20), dark, side+'Foot', .025)
cube('Smile', (0, -.245, 2.02), (.12, .018, .018), hair, 'Head', .005)

# Tiny action makes the exported glTF include an AnimationPlayer and skeleton pose.
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='POSE')
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'
    pb.keyframe_insert(data_path='rotation_quaternion', frame=1)
    pb.keyframe_insert(data_path='rotation_quaternion', frame=2)
bpy.ops.object.mode_set(mode='OBJECT')
rig.animation_data.action.name = 'TPose'
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 2

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'source' / 'Mira.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT / 'assets' / 'Mira.glb'), export_format='GLB', export_animations=True, export_nla_strips=False, export_apply=False)
print('Saved Mira.blend and Mira.glb')
