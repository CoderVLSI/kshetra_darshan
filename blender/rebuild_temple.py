"""Run a temple builder and export the scene with metre-scaled surfaces."""
import sys
import runpy
from tempfile import TemporaryDirectory
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'blender'))
args = sys.argv[sys.argv.index('--') + 1:]
script = Path(args[0]).resolve()
# Defer-aware builders skip their standalone export. Older builders still run
# through their original entry points and receive the final staged export.
runpy.run_path(str(script), init_globals={'DEFER_GLB_EXPORT': True}, run_name='__main__')
temple_id = script.stem.removeprefix('build_').removesuffix('_temple')
from deity_detail import upgrade_scene
upgrade_scene(temple_id)
from surface_detail import prepare_scene
prepare_scene()
temple_id = script.stem.removeprefix('build_').removesuffix('_temple')
target = ROOT / 'godot' / 'assets' / 'models' / (temple_id + '_kshetra_full.glb')
# Write the completed scene outside Godot's asset tree before replacing it.
# This also avoids truncating the builder's GLB if the final export fails.
with TemporaryDirectory(prefix="temple-export-", dir=ROOT) as scratch:
    staged = Path(scratch) / target.name
    bpy.ops.export_scene.gltf(filepath=str(staged), export_format='GLB', export_apply=True,
        export_yup=True, export_materials='EXPORT', export_cameras=False, export_lights=False)
    staged.replace(target)
print('REBUILT', temple_id, target.stat().st_size)
