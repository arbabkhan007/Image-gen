#!/usr/bin/env python3
"""Rebuild 2700x2025 Etsy masters, gallery.html, LISTING_NOTES.md and per-kit zips
for every Novality Store kit under output/etsy/. Run from repo root."""
import os, glob, zipfile, shutil
from PIL import Image, ImageFilter

BASE = 'output/etsy'
W, H, TR = 2700, 2025, 2700 / 2025

CAP_G = {
 '01-hero-santa-red': ('Alternate hero (pom-pom styling)','Alternate styling with a pom-pom tip - NOT in the written pattern; main hero is shot 16'),
 '02-hero-forest-green': ('Hero - Forest green','Second colourway hero with a pine sprig'),
 '03-colourways-lineup': ('All five colourways','Santa red, Forest green, Nordic grey, Candy pink, Midnight navy'),
 '04-macro-bobble-nose': ('The 5-dc bobble nose','Embroidered eyes one round above, either side, as written in R14'),
 '05-macro-spiral-stitches': ('No-see-through fabric','Dense spiral single crochet; colour-change slant at the back - the no-sew look'),
 '06-hands-scale': ('Palm-sized','About 11-12.5 cm (4.5-5 in) tall'),
 '07-size-ruler': ('Documented size','About 12 cm tall, 5 cm base, stands unaided'),
 '08-materials-flatlay': ('Everything you need','Worsted in body/white/skin, 3.5 mm hook, fibre fill, marker, tapestry needle'),
 '09-tree-ornament': ('Ornament option','Hangs by the optional ch-18 loop'),
 '10-mantel-trio': ('Mantel styling','A trio in 1-2 hours each - quick seasonal makes'),
 '11-hat-bend-brim': ('Hat bend + optional brim','Soft-bending tip with white slip-stitch brim at the R15-16 line'),
 '12-back-seamless': ('Seamless back','One uninterrupted spiral, colour-change slant at the back, no seams'),
 '13-size-variations': ('Three sizes','Mini 8-9 cm, standard 11-12.5 cm, large about 15 cm'),
 '14-gift-box': ('Gift-ready','Kraft box, twine bow, dried orange and pine'),
 '15-wip-one-piece': ('One piece, no sewing','Body, beard and face rounds in one continuous tube on the hook'),
 '16-hero-santa-red-v2': ('Hero - Santa red (MAIN)','Plain closed hat tip with crocheted hanging loop, no pom-pom'),
}
CAP_T = {
 '01-hero-fir-green': ('Hero - Fir green','Cone with tiered bobble rows, yarn baubles, flat folded base'),
 '02-clean-white': ('Clean white hero','Seamless white background main-listing style'),
 '03-macro-bobble-tiers': ('Bobble tiers macro','Distinct tiers of 5-dc bobbles with plain rounds between; columns stay straight'),
 '04-macro-contrast-bobbles': ('Contrast baubles macro','Red and gold contrast bobbles closed with a green loop'),
 '05-base-fold-detail': ('Base fold detail','Widest tier meets the table on the flat folded BLO base'),
 '06-hands-scale': ('Palm-sized','About 12 cm tall, 7 cm wide'),
 '07-size-ruler': ('Documented size','Measuring tape: about 12 cm x 7 cm'),
 '08-colourways-lineup': ('Five colourways','Fir green, Sage velvet, Snow white, Crimson berry, Gold-tipped'),
 '09-set-of-three': ('Set of three','DK about 9 cm, worsted about 12 cm, chunky about 16 cm'),
 '10-mantel-lifestyle': ('Mantel styling','With pine, candle and fairy lights'),
 '11-hanging-ornament': ('Ornament option','Hangs by the ch-18 loop at the tip'),
 '12-materials-flatlay': ('Everything you need','Green worsted, contrast minis, 4 mm hook, fill, felt base disc'),
 '13-table-centrepiece': ('Table centrepiece','Linen, stoneware, taper candle and dried orange'),
 '14-tip-closeup': ('Tip close-up','Closed 3-st tip over the final pinch of stuffing'),
 '15-wip-one-piece': ('One piece, no sewing','Base and bobble tiers complete, working round on the hook'),
}
CAP_O = {
 '01-hero-trio': ('Hero - the bundle','Red striped bauble, gold blocked star, white lace snowflake'),
 '02-clean-white': ('Clean white hero','The three ornaments on seamless white'),
 '03-bauble-closeup': ('Bauble close-up','Stuffed sphere, metallic surface stripes, crown loop'),
 '04-star-closeup': ('Star close-up','Flat blocked five points with ch-2 tips'),
 '05-snowflake-closeup': ('Snowflake close-up','Six open lace arms in crisp cotton'),
 '06-colourways': ('Five colourways','Snow white, Classic red & white, Gold, Evergreen trio, Frost blue'),
 '07-garland': ('Garland','All three strung on one length of yarn'),
 '08-on-the-tree': ('On the tree','The trio hanging among fairy lights'),
 '09-hands-scale': ('Palm-sized','Bauble 4 cm, star 9 cm, snowflake 10 cm'),
 '10-blocking-mat': ('Blocking','Star and snowflake pinned flat to dry'),
 '11-materials-flatlay': ('Leftover-yarn project','5-15 g amounts, 3-4 mm hooks, pins and board'),
 '12-backing-cards': ('Gift backing cards','Loops threaded through cards, knots hidden'),
 '13-window-snowflake': ('Window light','Lace snowflake glowing against frosty glass'),
 '14-star-gift-topper': ('Gift topper','Blocked star on a kraft-wrapped gift'),
 '15-bauble-bowl': ('Bowl styling','Baubles piled in stoneware'),
}
CAP_S = {
 '01-hero-under-tree': ('Hero - under the tree','Standard skirt, forest & cream, trunk through the centre ring'),
 '02-flat-top-view': ('Flat top view','12-spoke circle, bobble rings, scalloped border'),
 '03-bobble-ring-macro': ('Bobble rings','CC 5-dc bobbles popped to the front every third round'),
 '04-scallop-border-macro': ('Scalloped border','Shell border with the gentle wave of the design'),
 '05-centre-hole': ('Centre hole','Closed ring fitted around the trunk; 12 spokes radiate'),
 '06-colourways': ('Four colourways','Forest & cream, Snow white & red, Navy & silver, Single-colour cream'),
 '07-three-sizes': ('Three sizes','Mini about 50 cm, standard about 80 cm, large about 100 cm'),
 '08-mini-tabletop': ('Mini tabletop','Sideboard tree with cocoa'),
 '09-large-interior': ('Large size','Tall tree, bright Scandinavian room'),
 '10-surface-spokes': ('Surface snowflake','Loose CC surface sl sts up the 12 columns'),
 '11-gifts-on-skirt': ('Gifts on the skirt','Kraft parcels at the border'),
 '12-border-wave': ('Border wave','Flat blocked circle, gentle shell wave'),
 '13-wip': ('Growth ladder WIP','+12 sts per round, hook in at the join'),
 '14-cozy-cream': ('Single-colour cream','With knit throw and cocoa'),
 '15-measure-materials': ('Measure first','Diameter and centre hole checked against the stand'),
}
CAP_WR = {
 '01-hero-poinsettia-door': ('Hero - poinsettia','Standard door wreath, ribbon wrapped twice'),
 '02-snowflake-dressed': ('Swap to snowflake','Lace snowflake tied on'),
 '03-bow-dressed': ('Swap to bow','Holiday bow tied on'),
 '04-removable-trio': ('Base + 3 decorations','Each with its folded removable tie'),
 '05-tie-detail': ('Lark-head tie','Tails wrapped opposite ways, reef knot at back'),
 '06-tube-join-macro': ('Seamless tube join','Whip-stitched 12 pairs, openings kept round'),
 '07-mini-ornament': ('Mini ornament','About 7 cm, doubled yarn tie'),
 '08-colourways': ('Four colourways','Classic, Winter white & gold, Berry, Farmhouse'),
 '09-sizes': ('Three sizes','Mini, standard door, large door'),
 '10-hanger-detail': ('Load-rated hanger','Woven ribbon wrapped twice around the tube'),
 '11-materials-flatlay': ('Everything you need','Green worsted, decor minis, fill, rated ribbon'),
 '12-poinsettia-macro': ('Poinsettia macro','Six petals, yellow centre, three leaves'),
 '13-snowflake-macro': ('Snowflake macro','Metallic thread held with the white'),
 '14-bow-macro': ('Bow macro','Two loops, two tails, wrapped band'),
 '15-porch-lifestyle': ('Winter porch','Lantern, mini evergreens, snow'),
}

KITS = [
 ('No-Sew Christmas Gnome', 'NS 11', 'no-sew-christmas-gnome', CAP_G,
  'No-Sew Christmas Gnome Crochet Pattern - One Piece Amigurumi, Beginner PDF, US+UK Terms, Gnome Ornament',
  'christmas gnome pattern, no sew gnome, crochet gnome pdf, amigurumi gnome, gnome ornament, beginner crochet, holiday crochet, gnome gift idea, nordic gnome, one piece amigurumi, winter crochet, gnome decor, crochet pattern uk'),
 ('Bobble Christmas Tree', 'NS 12', 'bobble-christmas-tree', CAP_T,
  'Bobble Christmas Tree Crochet Pattern - One Piece Amigurumi Tree, Easy-Intermediate PDF, US+UK Terms, Bauble Bobbles',
  'crochet tree pattern, bobble christmas tree, amigurumi tree, crochet tree pdf, christmas tree decor, bauble bobbles, holiday crochet, nordic christmas, tree ornament pattern, winter crochet, one piece crochet, easy crochet pattern, christmas table decor'),
 ('Christmas Ornament Bundle', 'NS 13', 'christmas-ornament-bundle', CAP_O,
  'Christmas Ornament Bundle Crochet Pattern - Bauble, Star & Snowflake, Beginner PDF, US+UK Terms',
  'crochet ornament pattern, christmas bauble, crochet star, crochet snowflake, ornament bundle, gift topper, garland pattern, beginner crochet, window decor, leftover yarn project, holiday pdf, tree ornaments, nordic christmas'),
 ('Bobble Snowflake Tree Skirt', 'NS 14', 'bobble-snowflake-tree-skirt', CAP_S,
  'Bobble Snowflake Tree Skirt Crochet Pattern - 3 Sizes, Easy-Intermediate PDF, US+UK Terms',
  'tree skirt pattern, crochet tree skirt, bobble crochet, snowflake skirt, christmas tree skirt, holiday home decor, scallop border, winter crochet, easy intermediate pdf, tree stand cover, festive floor decor, crochet skirt pdf, bobble snowflake'),
 ('Interchangeable Christmas Wreath', 'NS 15', 'interchangeable-wreath', CAP_WR,
  'Interchangeable Christmas Wreath Crochet Pattern - 3 Removable Decorations, 3 Sizes, Beginner PDF',
  'crochet wreath pattern, christmas wreath, door wreath, poinsettia crochet, removable decorations, interchangeable wreath, stuffed tube wreath, mini wreath ornament, winter white wreath, farmhouse wreath, beginner crochet pdf, holiday door decor, handmade wreath'),
]

# 1) self-heal masters
for title, code, kit, caps, ttitle, tags in KITS:
    d = f'{BASE}/{kit}'
    os.makedirs(f'{d}/etsy-ready', exist_ok=True)
    for f in sorted(glob.glob(f'{d}/*.jpg')):
        out = f'{d}/etsy-ready/{os.path.basename(f)}'
        if os.path.exists(out):
            continue
        im = Image.open(f).convert('RGB'); w, h = im.size
        if w / h > TR:
            nw = int(round(h * TR)); l = (w - nw) // 2; im = im.crop((l, 0, l + nw, h))
        else:
            nh = int(round(w / TR)); t = (h - nh) // 2; im = im.crop((0, t, w, t + nh))
        im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=2))
        im.save(out, 'JPEG', quality=92, progressive=True, optimize=True)
        print('master:', out)

# 2) gallery
html = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
 '<meta name="viewport" content="width=device-width, initial-scale=1">',
 '<title>Novality Store - Etsy Image Kits (NS 11-NS 15)</title><style>',
 ':root{--bg:#f6f1ea;--ink:#2b2620;--card:#fff;--accent:#b3402e;--muted:#8a7f72}*{box-sizing:border-box}',
 'body{margin:0;font-family:"Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--ink)}',
 'header{padding:44px 24px 4px;text-align:center}h1{margin:0 0 6px;font-size:clamp(26px,4vw,40px)}',
 '.sub{color:var(--muted);max-width:780px;margin:0 auto;line-height:1.55;font-size:15px}',
 'h2{max-width:1180px;margin:44px auto 4px;padding:0 20px;font-size:24px}',
 '.ks{max-width:1180px;margin:0 auto 8px;padding:0 20px;color:var(--muted);font-size:13px}',
 'main{max-width:1180px;margin:0 auto;padding:18px 20px 30px;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px}',
 'figure{margin:0;background:var(--card);border-radius:14px;overflow:hidden;box-shadow:0 6px 24px rgba(60,40,20,.10)}',
 'img{display:block;width:100%;height:auto}figcaption{padding:12px 14px 14px}',
 '.idx{color:var(--accent);font-weight:700;font-size:12px;letter-spacing:1.5px}',
 '.cap{margin:4px 0 2px;font-weight:600;font-size:15px}.alt{margin:0;color:var(--muted);font-size:12.5px;line-height:1.5}',
 'footer{text-align:center;color:var(--muted);font-size:12.5px;padding:10px 20px 56px}</style></head><body>',
 '<header><h1>Novality Store - Etsy Image Kits</h1><p class="sub">Photoreal listing kits for five one-piece Christmas patterns, NS 11-NS 15. Click any photo for the 2700x2025 Etsy-ready master.</p></header>']
for title, code, kit, caps, ttitle, tags in KITS:
    files = sorted(glob.glob(f'{BASE}/{kit}/*.jpg'))
    html.append(f'<h2>{title} <span style="color:var(--muted);font-size:14px">({code})</span></h2>')
    html.append(f'<div class="ks">{len(files)} shots - previews below, masters in etsy-ready/</div><main>')
    for f in files:
        b = os.path.basename(f); idx = b.split('-')[0]
        cap, alt = caps.get(b, (b, b))
        html.append(f'<figure><a href="{kit}/etsy-ready/{b}"><img src="{kit}/{b}" alt="{alt}" loading="lazy"></a>'
                    f'<figcaption><span class="idx">{idx}</span><p class="cap">{cap}</p><p class="alt">{alt}</p></figcaption></figure>')
    html.append('</main>')
html.append('<footer>Masters 2700x2025 (Etsy recommended 4:3) - (c) 2026 Novality Store - #NovalityStore</footer></body></html>')
open(f'{BASE}/gallery.html', 'w').write('\n'.join(html))

# 3) notes
notes = ['# Novality Store - Etsy Image Kits (NS 11 - NS 15)\n',
 'Every shot ships as a 1200x896 preview and a 2700x2025 (4:3, Etsy-recommended) master in `<kit>/etsy-ready/`.\n']
for title, code, kit, caps, ttitle, tags in KITS:
    files = sorted(f for f in caps if os.path.exists(f'{BASE}/{kit}/{f}'))
    notes.append(f'## {title} ({code}) - {len(files)} shots\n')
    notes.append('| # | File | Role | Alt text |\n|---|------|------|----------|')
    for f in files:
        c, a = caps[f]; notes.append(f'| {f[:2]} | {f} | {c} | {a} |')
    notes.append(f'\nTitle: {ttitle}\nTags: {tags}\n')
notes.append('''
## Compliance reminders
- NS 11/12: never market finished items as "baby-safe" or ASTM F963 / EN 71 compliant; no beads/bells on the tree; credit "Novality Store".
- NS 13: decorations, not toys; keep loops short and secured twice; no beads or glued additions.
- NS 14: home decor, not flameproof; keep away from flames/heaters; cool-running approved lights only.
- NS 15: use a load-rated hook and a load-rated cord/ribbon wrapped twice around the whole tube; never rely on crochet stitches or suction cups.
- The patterns themselves may not be redistributed; finished-item sales in small batches with credit are licensed.
''')
open(f'{BASE}/LISTING_NOTES.md', 'w').write('\n'.join(notes))

# 4) zips
for title, code, kit, caps, ttitle, tags in KITS:
    zn = f'{kit}-etsy-kit.zip'
    outp = f'etsy-kits/{zn}'
    os.makedirs('etsy-kits', exist_ok=True)
    with zipfile.ZipFile(outp, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(f'{BASE}/{kit}/*.jpg')):
            z.write(f, f'{kit}-etsy-kit/previews/{os.path.basename(f)}')
        for f in sorted(glob.glob(f'{BASE}/{kit}/etsy-ready/*.jpg')):
            z.write(f, f'{kit}-etsy-kit/etsy-ready/{os.path.basename(f)}')
        z.write(f'{BASE}/LISTING_NOTES.md', f'{kit}-etsy-kit/LISTING_NOTES.md')
        z.write(f'{BASE}/gallery.html', f'{kit}-etsy-kit/gallery.html')
    shutil.copy(outp, f'{BASE}/{zn}')
    with zipfile.ZipFile(outp) as z:
        print(outp, 'entries:', len(z.namelist()), 'corrupt:', z.testzip(), f'{os.path.getsize(outp)/1024/1024:.2f} MB')

for title, code, kit, caps, ttitle, tags in KITS:
    print(kit, 'previews:', len(glob.glob(f'{BASE}/{kit}/*.jpg')), 'masters:', len(glob.glob(f'{BASE}/{kit}/etsy-ready/*.jpg')))
