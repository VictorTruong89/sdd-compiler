"""Run SWE-Dev's own test step on one sample, three ways, with no model. Needs Docker and the sample's image.

    python3 judge_one.py download/data/dataset/test/easy/advertools-test_ad_create-level1-metadata.json

Uses `run_tests_in_docker` from the benchmark's `infer/single/single_evaluation_passk.py` unchanged:
  image as shipped   nothing written into the container (the evaluator's own baseline)
  reference          the sample's `GT_file_code` written in
  untouched          the sample's `file_code` written in: the masked files, as if the agent did nothing
Prints one JSON object; redirect it to keep it.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "download" / "repo" / "infer" / "single"))
from single_evaluation_passk import run_tests_in_docker  # noqa: E402

sample = Path(sys.argv[1])
meta = json.loads(sample.read_text(encoding="utf-8"))
out = {"sample": sample.name, "image": f"dorothyduuu/swe-dev:{meta['package_name']}-image", "runs": {}}
for label, key in (("image_as_shipped", ""), ("reference", "GT_file_code"), ("untouched", "file_code")):
    t = time.time()
    r = run_tests_in_docker(meta, key)
    out["runs"][label] = {"passed": r["passed"], "failed": r["failed"], "errors": r["errors"],
                          "seconds": round(time.time() - t, 1)}
print(json.dumps(out, indent=2))
