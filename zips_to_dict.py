import os
import sys

# Get the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Parent directory (project root)
project_root = os.path.dirname(script_dir)

zips_txt_path = os.path.join(script_dir, 'zips.txt')
output_path = os.path.join(project_root, 'zips_dict.py')

if not os.path.exists(zips_txt_path):
    print(f"ERROR: {zips_txt_path} not found.")
    sys.exit(1)

zips_dict = {}
try:
    with open(zips_txt_path, 'r') as f:
        lines = f.readlines()
except Exception as e:
    print(f"ERROR: Could not open {zips_txt_path}: {e}")
    sys.exit(1)

if not lines:
    print(f"ERROR: {zips_txt_path} is empty.")
    sys.exit(1)

for line in lines:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) == 2:
        key, value = parts
        zips_dict[str(value)] = str(key)

if not zips_dict:
    print(f"ERROR: No valid lines found in {zips_txt_path}.")
    sys.exit(1)

with open(output_path, 'w') as out:
    out.write('zips_dict = ' + repr(zips_dict) + '\n')

print(f"Dictionary with {len(zips_dict)} entries written to {output_path}")
