import glob
import os
import json
DOMAIN = {}
for f in glob.glob("endpoint_schema/*.json"):
    if os.path.basename(f).startswith("x-"):
        continue
    name = os.path.splitext(os.path.basename(f))[0]
    with open(f) as f_schema:
        try:
            DOMAIN[name] = json.load(f_schema)
        except Exception as e:
            raise Exception("Error when loading file {} : {}".format(f, e))