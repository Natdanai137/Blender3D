import bpy
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'source' / 'Mira.blend'))

world = bpy.context.scene.world
world.color = (0.14, 0.38, 0.40)
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.14, 0.55, 0.58, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .55

def mat(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    return m

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -.14))
floor = bpy.context.object
floor.name = 'Presentation plinth'
floor.dimensions = (3.5, 3.5, .28)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
floor.data.materials.append(mat('Soft green plinth', (.37, .74, .42)))

def area(name, loc, energy, size):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector((0, 0, 1.1)) - obj.location).to_track_quat('-Z', 'Y').to_euler()

area('Key light', (2.5, -3.8, 5), 450, 4)
area('Fill light', (-3, -1, 3), 250, 4)
bpy.ops.object.camera_add(location=(3.0, -5.5, 2.7))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.13)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.4
bpy.context.scene.camera = camera
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = str(ROOT / 'screenshots' / 'Blender-Mira.png')
bpy.ops.render.render(write_still=True)
