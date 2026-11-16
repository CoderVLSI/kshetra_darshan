"""Run one temple builder, prepare metre-scaled surfaces, and export once more."""
import sys
import runpy
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'blender'))
args = sys.argv[sys.argv.index('--') + 1:]
script = Path(args[0]).resolve()
runpy.run_path(str(script), run_name='__main__')
temple_id = script.stem.removeprefix('build_').removesuffix('_temple')
from deity_detail import upgrade_scene
upgrade_scene(temple_id)
from surface_detail import prepare_scene
prepare_scene()
temple_id = script.stem.removeprefix('build_').removesuffix('_temple')
target = ROOT / 'godot' / 'assets' / 'models' / (temple_id + '_kshetra_full.glb')
bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', export_apply=True,
    export_yup=True, export_materials='EXPORT', export_cameras=False, export_lights=False)
print('REBUILT', temple_id, target.stat().st_size)
