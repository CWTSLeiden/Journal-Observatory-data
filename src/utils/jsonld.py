import json
from pyld import jsonld

pad_frame = {
    "job:hasAssertion": {}
}

def jsonld_frame(infile, outfile=None, frame={}):
    if not outfile:
        outfile = infile.replace(".json", "_framed.json")
    
    with open(infile, "rb") as f:
        pad = json.load(f)
    frame = {"@graph": pad_frame, "@context": pad["@context"]}
    pad_framed = jsonld.frame(pad, frame)
    with open(outfile, "w") as f:
        json.dump(pad_framed, f, indent=4)


def jsonld_strip_uni_p(d):
    uni = True
    for k in d.keys():
        if k[0] != "@":
            uni = False
    if uni:
        return d.get("@value") or d.get("@id")
    return None


def jsonld_strip_key(key):
    if ":" in key:
        return key[key.index(":")+1:]
    return key
        
        
def jsonld_strip_sub(val):
    if type(val) == dict:
        if jsonld_strip_uni_p(val):
            return jsonld_strip_uni_p(val)
        d = {}
        for k, v in val.items():
            if k in ("@type", "@context"):
                pass
            else:
                d[jsonld_strip_key(k)] = jsonld_strip_sub(v)
        return d
    if type(val) == list:
        if len(val) > 0:
            if type(val[0]) == dict:
                if val[0].get("@id"):
                    d = {}
                    for v in val:
                        key = v.get("@id")
                        del(v["@id"])
                        d[jsonld_strip_key(key)] = jsonld_strip_sub(v)
                    return d
        return [ jsonld_strip_sub(v) for v in val ]
    else:
        return val


def jsonld_strip(infile, outfile=None):
    if not outfile:
        outfile = infile.replace("_framed.json", ".json").replace(".json", "_stripped.json")
    with open(infile, "rb") as f:
        pad = json.load(f)

    strip = {}
    for key, val in pad.items():
        if key not in ("@context", "@id", "@type"):
            strip[jsonld_strip_key(key)] = jsonld_strip_sub(val)

    with open(outfile, "w") as f:
        json.dump(strip, f, indent=4)
