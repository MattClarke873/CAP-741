# CAP 741 Log

Phone web app for filling in CAA CAP 741 Section 3.1 (Maintenance Experience) pages and exporting them as a typed PDF on the real Issue 4 template.

## Files
| File | Purpose |
|---|---|
| `index.html` | The whole app |
| `cap741-template.pdf` | Blank Section 3.1 task page + signature sheet (from CAP 741 Issue 4) |
| `pdf-lib.min.js` | PDF library (local copy so it works offline) |
| `data/part66-types.json` | Aircraft type suggestions, built from the UK Part-66 type rating list |
| `data/part145-orgs.json` | MRO suggestions, built from the CAA list of UK Part 145 organisations |
| `sw.js` | Offline cache — bump `VERSION` when you upload changes |
| `manifest.webmanifest`, `icon-*.png` | Home-screen app setup |
| `tools/` | Scripts to rebuild the `data/` lists (not needed online) |

## Put it online (GitHub Pages)
1. Create a new repo, e.g. `cap741`, and upload `index.html`, `cap741-template.pdf`, `pdf-lib.min.js`, `sw.js`, `manifest.webmanifest`, the icons and the `data` folder to the root. The `tools` folder and the Excel file can stay off it.
2. Settings → Pages → Deploy from branch → `main` / root.
3. Open `https://mattclarke873.github.io/cap741/` in Safari on the iPhone → Share → **Add to Home Screen**.

When you upload changes, bump `VERSION` in `sw.js` (e.g. `cap741-v3` → `cap741-v4`) so phones fetch the new copy.

## Dropbox sync (optional)
The app has a step-by-step guide under **Settings → Dropbox sync** that ticks off each step as you go. In short:
1. dropbox.com/developers/apps → Create app → Scoped access → **App folder** → name it.
2. Permissions tab: tick `files.content.write` and `files.content.read` → Submit. Do this *before* connecting.
3. Copy the **App key** from the app's Settings tab (not the App secret) and paste it in the app, or set `DROPBOX_APP_KEY` at the top of the script in `index.html`.
4. In the app: Connect Dropbox → Allow → copy the code Dropbox shows → paste → Finish connecting.

No redirect URL is needed. Data syncs to `Apps/<your app name>/cap741-log.json`. If you change permissions later, disconnect and connect again.

## Using it
- **Entry tab:** pick activity type(s), date (defaults to today), aircraft, ATA chapter, job card, task detail and supervisor. The row meter shows how many of the page's five rows the entry will use and how many are left on that page.
- **Training or certification:** tap which one each entry is for, on the Entry tab. The choice carries over to the next entry. On the Logbook tab you can filter (and download) training or certification entries on their own, and bulk-mark entries that aren't set yet, such as imported ones. It isn't printed on the CAP 741 page.
- **Aircraft:** type a model (e.g. `AW139`, `S-92`) and pick it from the Part-66 list to fill in make, engine and the type-rating endorsement. Pages are grouped by that endorsement.
- **Supervisors:** typing a new name on an entry adds them to the list. Fill in their licence cat., number and MRO on the Supervisors tab (needed for the signature sheet). The MRO box suggests organisations and UK.145 numbers from the CAA list as you type; you can still type your own.
- **ATA coverage (top of the Logbook tab):** tap every licence you're applying for (B1.1–B1.4, B2; more than one is fine). Each gets a weighted readiness score: main systems count 3× other systems, and a chapter only counts up to its target. With several licences picked, a chapter is a main system if any of them treats it as one, and the tile says which. Each relevant chapter shows how many distinct tasks you've logged against a rule-of-thumb target: 5–10 for main systems, 2–5 for the rest. The CAA sets no official minimum. Dashed red = nothing yet, amber = below target, green = on target. The codes on a tile show which activity types you've covered there. Tap a chapter to filter to its pages, or to start an entry if it's empty. Repeats of the same task aren't counted.
- **Repeat and variety checks:** while you type a task, the Entry tab warns if the same (or nearly the same) task is already logged in that ATA chapter. CAP 741 only needs each task once. Coverage tiles flag chapters with repeats and chapters with only routine work (no removal/installation, functional test, troubleshooting, repair, mod or wiring task), and the Logbook warnings list them.
- **Experience time (Logbook tab):** pick your route (no previous technical training, relevant technical training, or a Part-147 basic course) and when your experience started (defaults to your first entry). Each licence you've selected shows time served against the Part-66 66.A.30 basic experience (B1.1/B1.3/B2: 5, 3 or 2 years; B1.2/B1.4: 3, 2 or 1 years) and the date you'll reach it. A 12-month strip shows which recent months have entries. Check the CAA's current rules before you apply.
- **Logbook tab:** pages are shown as CAP 741 sheets, one aircraft type + one ATA chapter per page, five rows a page, sorted by ATA. **Download PDF** saves everything, or one page at a time with **Download page**. On iPhone the PDF lands in Files → Downloads, ready to print.
- On the PDF, activity types are printed in full (e.g. *Removal / Installation*); the app keeps the short codes.
- Print, sign every page yourself, and get each supervisor's signature and stamp in ink.

### Long entries spill into the next row
If the task detail won't fit one row (the text shrinks to 7pt at the smallest first), it carries on into the rows below. The first row keeps the activity, date, reg and job number, and the rows below get a ditto mark `"` in those columns. The supervisor's name and signature box moves to the lowest row of the entry, with the mark in the supervisor boxes above it. Switch it to a dash `–` under **Settings → Pages and printing**. An entry is never split across two pages: if it won't fit in the rows left, it starts a new page. Anything longer than a whole page is cut off, and the app warns you.

### Print when a page fills
When a saved entry uses the last row of a page, the app offers to download just that page so it can be signed while the work is fresh. Turn this off (or back on) under **Settings → Pages and printing**.

## Refreshing the CAA lists
The suggestion lists are snapshots. Current versions in `data/`:
- Part-66 type rating list, version 16 (updated 11 Aug 2026)
- UK Part 145 approved organisations, 16 October 2026 (284 organisations)

To update them on a Mac:

1. Download the latest **UK Part-66 type rating list** Excel file from the CAA website. The script reads the first tab, which is the newest year.
2. Download the latest **Airworthiness Approved Organisations — UK Part 145** PDF from the CAA website, then turn it into text:
   ```bash
   swift tools/pdf-text.swift part145.pdf > part145.txt
   ```
3. Rebuild both lists (run from the app folder):
   ```bash
   python3 tools/build-lists.py uk-part-66-type-rating-list.xlsx part145.txt
   ```
   It prints how many types and organisations it found. Check the count looks sensible against the previous one.
4. Upload the new `data/*.json` files and bump `VERSION` in `sw.js`.

The script skips rows marked **D** (deleted) in the type list and organisations with a revocation date in the Part 145 list. Entries and aircraft already saved aren't changed. The lists only affect what's suggested as you type.
