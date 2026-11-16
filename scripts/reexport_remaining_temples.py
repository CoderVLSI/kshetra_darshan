"""
Re-export all 12 remaining Shakti Peetha temple models in Blender 5.3
Ensures all 18 temples are built with the clean PBR materials and upgraded architecture.
"""
import subprocess
import sys
import os

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"
BLENDER_DIR = r"d:\Kshetra_Darshan\blender"

temple_scripts = [
    "build_kalighat_temple.py",
    "build_madurai_meenakshi_temple.py",
    "build_kanchipuram_kamakshi_temple.py",
    "build_kashi_vishalakshi_temple.py",
    "build_mysore_chamundeshwari_temple.py",
    "build_tuljapur_bhavani_temple.py",
    "build_mahur_renuka_temple.py",
    "build_alampur_jogulamba_temple.py",
    "build_srisailam_bhramaramba_temple.py",
    "build_pithapuram_puruhutika_temple.py",
    "build_jajpur_biraja_temple.py",
    "build_prayag_madhaveswari_temple.py",
]

print(f"Starting batch re-export of {len(temple_scripts)} temples...")
for script in temple_scripts:
    script_path = os.path.join(BLENDER_DIR, script)
    print(f"\n--- Building {script} ---")
    cmd = [BLENDER_EXE, "--background", "--python", script_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: {script}")
    else:
        print(f"FAILED: {script}")
        print(res.stderr[:400])

print("\nBatch re-export finished!")
