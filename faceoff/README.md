# Stock face-off videos

Data files hold the numbers (and, for the older template mode, the script). Bank pairs use `"kind": "bank"`: ROE instead of ROCE, an asset-quality scene (gross/net NPA + NIM) instead of cash flow, quarterly profit instead of OPM.

Two stocks from the same sector compared in a ~5-minute 1920×1080 video. Every video gets its own look, story structure, motion style, chart forms, narrator voice and music. The brand (logo, green, disclaimer, follow CTA) never changes.

Educational only. Never a buy/sell call: the scripts and the final card say so, and the footer on every frame carries the disclaimer and data source.

## Run

```bash
# from the repo root (needs node_modules, assets/, and the Kokoro model files kokoro-v1.0.onnx + voices-v1.0.bin at the root, or KOKORO_DIR)
npm install
pip install --break-system-packages kokoro-onnx soundfile playwright && python3 -m playwright install chromium

python3 faceoff/engine/build.py  tcs-infy          # pick style, write script, generate voice → faceoff/out/tcs-infy/spec.json
python3 faceoff/engine/render.py tcs-infy full 3   # 3 parallel Chromium workers → 8-second chunk files (re-run resumes)
python3 faceoff/engine/mix.py    tcs-infy          # join chunks + voice + music + SFX, loudness -14 LUFS
```

Then add the result to `faceoff/history.json` (look, structure, motion, var, voice) so the next video avoids it.

Useful flags for `build.py`: `--look`, `--structure`, `--motion`, `--voice`, `--var '{"size":2}'`, `--seed N`, `--no-voice` (fast layout test), `--out DIR`.
Stills for checking: `python3 faceoff/engine/render.py <pair> snap 12.5 40 95`.

## Phase 3: story-first episodes (use this for new videos)

Every video is written around ONE angle in the data, with its own scene list, narration format and opening.

```bash
python3 faceoff/engine/episode.py pick hdfcbank-icicibank            # → format, opening, look, motion, voices (no-repeat)
# write faceoff/episodes/<slug>.json for that pick (see hdfc-icici-debate.json)
python3 faceoff/engine/episode.py build faceoff/episodes/<slug>.json # voices every line → faceoff/out/<slug>/spec.json
python3 faceoff/engine/render.py <slug> full 3
python3 faceoff/engine/mix.py <slug>
```

- **Formats:** `documentary` (one narrator), `debate` (moderator + two hosts, each arguing for one stock; speaker pill with a voice-reactive avatar), `quiz` (questions with a 3-second countdown before each reveal), `newsdesk` (fast anchor read + scrolling stats ticker).
- **Openings:** `stat` (one shocking number), `question`, `invest` ("₹1 lakh invested 5 years ago"), `chart` (open on the most surprising chart).
- **Scene types:** `hero` (one or two giant numbers), `kinetic` (word-by-word text), `duel` (split-screen metric rows), `chartzoom` (big chart; camera flies to each callout), `invest`, `mythfact` (TRUE / FALSE / HALF TRUE stamp), `quiz`, `split` (closing halves), `classic` (any chart scene below, e.g. `{"key": "latest", "variant": 1}`), `cta`.
- **Lines:** `[speaker, text]` with speaker `n` / `a` / `b`, or `["pause", seconds]`. Each line is a beat; scene specs reference beats by index.
- **No-repeat:** format, opening and look never repeat within the last 3 videos; motion and voices differ from the last video. Record each finished video in `history.json` (format, opening, look, motion, voices).
- Pick 7–13 scenes that serve the angle. Not every metric belongs in every video.

## Hosts, industry packs, sound (Phase 3.1)

- **Hosts** (`engine/hosts.js`): three original flat-vector presenters (Arjun, Meera, Priya). Scene type `desk` is a full-screen cutaway; the camera pushes in on whoever speaks; lip-sync from the voice loudness, blinks, breathing, gaze toward the speaker. Gesture per line: `["a", "text", {"g": "point" | "raise" | "surprise"}]`. Hosts never share the frame with a chart.
- **Industry packs** (`engine/packs.js`, set `"industry"` in the episode): `banking` (vault + marble columns, weighty motion, coin/vault sounds, cinematic bed), `it` (wall of code screens, typed reveals, blips/keys, pulse bed), `auto` (dashboard + road, skid-in motion with blur, revs/shifts, bright bed). Each pack also draws a faint ambient layer behind data scenes.
- **Signature charts:** `vault` and `stacks` (banking), `racks` (IT), `speedo` and `race` (auto).
- **Icons:** any `"icon"` / `"icons"` in an episode is embedded from Lucide (ISC licence, `npm i lucide-static`).
- **Signature moment:** put one-off scene code in `episodes/<slug>.js` (see `hdfc-icici-v2.js`, the merger animation) and use its type in the episode.
- **Sound:** `engine/sfxgen.py` synthesises industry effects into `faceoff/sfx/`. The mix ducks music under every voice, keeps it lower under desk talk and lifts it for the close.

## Data

One JSON per pair in `faceoff/data/` (see `tcs-infy.json`): price, market cap, 52-week range, P/E, P/B, dividend yield, ROE, debt/equity,
1/3/5/10-year price CAGR, 10 years of sales / profit / OPM / dividend payout / ROCE, 5 years of operating cash flow,
8 quarters of sales + OPM, 8 quarters of shareholding, latest-quarter highlights, strengths and watch-outs.
Source: Screener.in (consolidated) plus the companies' own quarterly releases. Use the company-reported profit for the latest quarter.

## Style options

| | Options |
|---|---|
| Look | `glass` (dark), `paper` (newspaper), `blueprint`, `neon` (terminal), `flat` (bold yellow) |
| Structure | `chapters`, `rounds` (boxing, round stamps, split decision), `case` (case for A → case for B → head to head), `timeline` (then → now → next) |
| Motion | `canvas` (camera pans over one big page), `cards` (3D card flips), `split` (diagonal wipe with green light bar) |
| Charts | 3 forms each for size, returns, valuation, revenue, profit, quarterly, ROCE, ownership; 2 for cash and latest quarter |
| Voice | `af_heart`, `af_bella`, `bf_emma`, `am_michael` (Kokoro) |
| Music | by look: pulse, marimba, cinematic, lofi, bright (`assets/music`) |

No-repeat rules in `build.py → pick()`: never either of the last 2 looks, never the last structure, avoid the last motion and voice, and revenue/profit never share a chart form.

## Files

- `engine/build.py` – picker, narration per structure, Kokoro voice per sentence (timings drive the animation beats)
- `engine/page.html` – all looks, scene components, chart forms and motion; `seek(t)` draws any frame deterministically
- `engine/render.py` – Playwright frame capture → ffmpeg chunks
- `engine/mix.py` – audio mix (voice, music by look, transition SFX by motion)

## Phase 3.2 — one, two or three stocks
The data file decides the count: keys `a`, `b`, `c` (single stock = `a` only; add `benchLabel`/`benchShort`/`benchNote` for an industry benchmark).
- **1 stock (deep dive):** formats documentary · bullbear · quiz · newsdesk. Bull vs Bear = Arjun (bull, host colour `up`), Meera (bear, `dn`), Priya moderating.
  `duel` rows with a `bench` value become stock-vs-benchmark; `chartzoom` takes a dashed `bench` series; `split` takes `cols` (bull case / bear case); `quiz` takes custom `options`; new `timeline` scene for milestones.
- **3 stocks (industry round-up):** formats panel · countdown · documentary · quiz. Panel = Arjun (a), Meera (b), Kabir (c), Priya moderating at a 4-seat desk.
  New `podium` (ranks on ONE metric, labelled "ranked on this metric only") and `scorecard` (stocks × metrics grid). `duel` becomes a table.
- Every scene type and the banking/IT/auto signature charts lay out for 1–3 stocks. Third-stock colour `--c` per look. No overall winner, ever.
