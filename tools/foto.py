import json, os, urllib.request, urllib.parse, time
UA = {"User-Agent": "LibroCineseFoto/1.0 (educational children book)"}
os.makedirs("foto", exist_ok=True)
meta = {}
for line in open("tools/queries.txt", encoding="utf8"):
    line = line.strip()
    if not line: continue
    key, q = line.split("|", 1)
    params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
              "gsrsearch": q + " filetype:bitmap", "gsrlimit": "6", "prop": "imageinfo",
              "iiprop": "url|extmetadata|mime", "iiurlwidth": "1200"}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
    except Exception as ex:
        print("ERR", key, ex); continue
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    for i, p in enumerate(pages):
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("mime", "").startswith("image/jpeg") and not ii.get("mime", "").startswith("image/png"): continue
        src = ii.get("thumburl") or ii.get("url")
        em = ii.get("extmetadata", {})
        name = f"{key}_{i}.jpg"
        try:
            b = urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=60).read()
            open("foto/" + name, "wb").write(b)
            meta[name] = {"title": p.get("title"), "page": ii.get("descriptionurl"),
                          "artist": em.get("Artist", {}).get("value", ""), "license": em.get("LicenseShortName", {}).get("value", ""),
                          "desc": em.get("ImageDescription", {}).get("value", "")[:300]}
            print("ok", name, p.get("title"))
        except Exception as ex:
            print("ERR img", name, ex)
        time.sleep(1)
json.dump(meta, open("foto/meta.json", "w"), ensure_ascii=False, indent=1)
