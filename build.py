#!/usr/bin/env python3
"""Reads info/ and writes info/index.js for arrascordle.html.

info/achievements.csv   master list:  Achievements,Desc,Points
info/users.csv          id,name,achievements   (achievements separated by ';')
info/pfp/<id>.png       profile picture for the user with that id (1.png, 2.png, ...)
info/music/             background songs (mp3, ogg, wav, m4a, flac, opus, aac) - shown in Settings

Run this again whenever you edit anything in info/."""
import csv, json, os, re

root = os.path.dirname(os.path.abspath(__file__))
info = os.path.join(root, "info")
EXTS = ("png", "jpg", "jpeg", "gif", "webp", "bmp", "svg", "avif")

def read(path):
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read()

master_path = os.path.join(info, "achievements.csv")
users_path = os.path.join(info, "users.csv")
for p in (master_path, users_path):
    if not os.path.exists(p):
        raise SystemExit(f"missing {os.path.relpath(p, root)}")

master = read(master_path).replace("\r\n", "\n")
known = {r[0].strip().lower() for r in list(csv.reader(master.splitlines()))[1:] if r}

users, seen = [], set()
for row in csv.DictReader(read(users_path).splitlines()):
    uid = (row.get("id") or "").strip()
    name = (row.get("name") or "").strip()
    if not uid or not name:
        continue
    if uid in seen:
        print(f"  warning: duplicate id {uid} ({name})")
    seen.add(uid)
    ach = [a.strip().strip('"') for a in (row.get("achievements") or "").split(";")]
    ach = [a for a in ach if a and not re.fullmatch(r"achievements?", a, re.I)]
    for a in ach:
        if a.lower() not in known:
            print(f"  warning: '{a}' ({name}) not in achievements.csv -> 0 points")
    img = next((f"info/pfp/{uid}.{e}" for e in EXTS
                if os.path.isfile(os.path.join(info, "pfp", f"{uid}.{e}"))), None)
    if not img or os.path.getsize(os.path.join(root, img)) == 0:
        print(f"  warning: no usable pfp for {uid} ({name}) -> expected info/pfp/{uid}.png")
        img = None
    users.append({"name": name, "image": img, "list": "\n".join(ach)})
    print(f"ok   {uid:>3} {name}")

AUDIO = (".mp3", ".ogg", ".wav", ".m4a", ".flac", ".opus", ".aac", ".webm")
music_dir = os.path.join(info, "music")
os.makedirs(music_dir, exist_ok=True)
def natural(t): return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", t)]
music = []
for f in sorted(os.listdir(music_dir), key=natural):
    base, ext = os.path.splitext(f)
    if ext.lower() in AUDIO:
        music.append({"name": re.sub(r"[_]+", " ", base).strip(), "file": f"info/music/{f}"})
        print(f"song {f}")
if not music:
    print("  note: no songs in info/music/ (music player will be hidden)")

with open(os.path.join(info, "index.js"), "w", encoding="utf-8") as fh:
    fh.write("window.INFO = " + json.dumps({"master": master, "users": users, "music": music}, ensure_ascii=False, indent=1) + ";\n")
print(f"wrote info/index.js ({len(users)} users, {len(music)} songs)")
