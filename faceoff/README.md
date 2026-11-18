# Stock face-off videos

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
