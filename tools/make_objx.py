#!/usr/bin/env python3
"""Chaos's move set from the boss' third form (obj/p_org200_02.objx), made playable.

    make_objx.py <dissidia tools dir> <in p_org200_02.objx> <out p_chaos.objx>

  * motion_map: script 10084 (Demonsdance) has no animation in this form: it gets the animation of 10085, so no action of the
    objx is a dead one. Scripts 10002 / 10003 (steps 2 and 3 of Earthcrusher) carry boss-phase tags (phase 2 / 3): cleared.
  * hits: KICK_2 (The Fall's landing) 30 -> 16 (retail finishers are 10-16).
The unpack / pack round trip is byte exact (charmod_objx), so everything else stays the boss' bytes."""
import json
import os
import sys
import tempfile

tools, src, dst = sys.argv[1:4]
sys.path.insert(0, tools)
import charmod_objx as o  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    data = open(src, "rb").read()
    o.unpack(data, d)
    assert o.pack(d) == data, "unpack/pack is not exact for this file"
    p = os.path.join(d, "motion_map.json")
    j = json.load(open(p))
    rows = {r["script"]: r for r in j["rows"]}
    for s in (10002, 10003):
        rows[s]["phase"] = 0
    if 10084 not in rows:
        j["rows"].append({"script": 10084, "motion": rows[10085]["motion"], "phase": 0})
        j["rows"].sort(key=lambda r: r["script"])
    json.dump(j, open(p, "w"), indent=1)
    p = os.path.join(d, "hits.json")
    j = json.load(open(p))
    for h in j["hits"]:
        if h["name"] == "KICK_2":
            h["power"] = 16
    json.dump(j, open(p, "w"), indent=1)
    open(dst, "wb").write(o.pack(d))
print("wrote", dst)
