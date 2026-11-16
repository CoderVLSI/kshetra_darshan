"""
Shared PBR Material Library for Ashta Dasha Maha Shakti Peetha Darshana
All materials are Principled BSDF designed for clean, authentic glTF export.
Blender -> Godot coordinate mapping: (godot_x, godot_y, godot_z) = (blender_x, blender_z, -blender_y)
Ground at Y=0 in Godot means Z=0 in Blender.
"""
import bpy
import math
from surface_detail import add_stone_detail

def _ensure_node_tree(mat):
    """Ensure material has a node tree with Principled BSDF."""
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    output = tree.nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return tree, bsdf

def create_granite_stone(name="Granite_Stone", color=(0.25, 0.23, 0.21, 1.0), roughness=0.85):
    """Dark granite stone - typical South/East Indian temple walls and paving."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    add_stone_detail(mat, bsdf, color)
    return mat

def create_sandstone(name="Sandstone", color=(0.72, 0.58, 0.38, 1.0), roughness=0.88):
    """Warm sandstone for North Indian Nagara temples."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
    add_stone_detail(mat, bsdf, color)
    return mat

def create_white_marble(name="White_Marble", color=(0.90, 0.88, 0.85, 1.0), roughness=0.25):
    """Polished white marble for mandapas and floors."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    return mat

def create_black_stone(name="Black_Stone", color=(0.09, 0.08, 0.08, 1.0), roughness=0.4):
    """Polished black basalt - Hemadpanti / Chalukyan temples and sacred murtis."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    return mat

def create_red_laterite(name="Red_Laterite", color=(0.55, 0.22, 0.12, 1.0), roughness=0.92):
    """Red laterite stone for Assamese/Kerala style temples."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.2
    add_stone_detail(mat, bsdf, color)
    return mat

def create_gold_metal(name="Gold_Metal", color=(0.88, 0.72, 0.20, 1.0)):
    """Gold leaf / gilded surfaces for kalashas, vimanams, jewelry."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['Specular IOR Level'].default_value = 0.8
    return mat

def create_copper_metal(name="Copper_Metal", color=(0.72, 0.45, 0.20, 1.0)):
    """Copper/brass for bells, lamps, kalashas."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Specular IOR Level'].default_value = 0.7
    return mat

def create_brass_metal(name="Brass_Metal", color=(0.82, 0.64, 0.16, 1.0)):
    """Brass for ghanta (bell), deepam lamps."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.3
    return mat

def create_wood(name="Temple_Wood", color=(0.35, 0.20, 0.10, 1.0), roughness=0.75):
    """Carved wooden doors, ceiling panels."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    return mat

def create_terracotta(name="Terracotta", color=(0.72, 0.34, 0.18, 1.0), roughness=0.88):
    """Terracotta for Bengal Navaratna panels."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    add_stone_detail(mat, bsdf, color)
    return mat

def create_red_silk(name="Red_Silk", color=(0.78, 0.08, 0.08, 1.0), roughness=0.5):
    """Red silk drapes for deity adornment."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    bsdf.inputs['Sheen Weight'].default_value = 0.5
    bsdf.inputs['Sheen Tint'].default_value = (0.9, 0.1, 0.1, 1.0)
    return mat

def create_water(name="Sacred_Water", color=(0.14, 0.38, 0.48, 0.85)):
    """Translucent water for kundas and tanks."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Specular IOR Level'].default_value = 0.8
    bsdf.inputs['IOR'].default_value = 1.33
    bsdf.inputs['Transmission Weight'].default_value = 0.8
    bsdf.inputs['Alpha'].default_value = 0.85
    return mat

def create_flame_emission(name="Flame_Glow", color=(1.0, 0.65, 0.15, 1.0), strength=8.0):
    """Emissive material for deepam flames, aarti fire."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = strength
    return mat

def create_skin(name="Priest_Skin", color=(0.60, 0.42, 0.30, 1.0)):
    """Human skin for priest/devotee characters."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Specular IOR Level'].default_value = 0.4
    bsdf.inputs['Subsurface Weight'].default_value = 0.15
    return mat

def create_white_dhoti(name="White_Dhoti", color=(0.95, 0.93, 0.88, 1.0)):
    """White cotton cloth for devotee/priest dhoti."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.7
    return mat

def create_green_foliage(name="Foliage_Green", color=(0.15, 0.38, 0.10, 1.0)):
    """Tree foliage."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.8
    return mat

def create_tree_bark(name="Tree_Bark", color=(0.25, 0.15, 0.08, 1.0)):
    """Tree bark."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.9
    return mat

def create_kumkum_red(name="Kumkum_Red", color=(0.88, 0.10, 0.05, 1.0)):
    """Vermilion kumkum/sindoor for deity decoration."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.8
    return mat

def create_flower_garland(name="Flower_Garland", color=(1.0, 0.75, 0.05, 1.0)):
    """Yellow/orange marigold garlands."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.7
    return mat

def create_colorful_gopuram(name="Gopuram_Paint", color=(0.8, 0.2, 0.1, 1.0)):
    """Painted stucco for colorful gopuram tiers."""
    mat = bpy.data.materials.new(name=name)
    tree, bsdf = _ensure_node_tree(mat)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.7
    return mat
