import glob
import os
import json
DOMAIN = {}
for f in glob.glob("endpoint_schema/*.json"):
    if os.path.basename(f).startswith("x-"):
        continue
    name = os.path.splitext(os.path.basename(f))[0]
    with open(f) as f_schema:
        DOMAIN[name] = json.load(f_schema)
