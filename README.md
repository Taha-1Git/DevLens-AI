# DevLens AI — Free Codebase Analyzer

AI-powered codebase analyzer. 100% free to run — no paid services required.

## How it's structured

```
devlens-ai/
├── backend/          → FastAPI server (deploy free on Railway)
│   ├── main.py
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.json
└── frontend/         → Single HTML file (host free on Netlify Drop)
    └── index.html
```

## Step 1 — Get a free Anthropic API key

1. Go to https://console.anthropic.com
2. Sign up (free), go to **API Keys** → **Create Key**
3. Anthropic gives free trial credits to new accounts — enough for a lot of testing.
   Copy the key (starts with `sk-ant-...`)

## Step 2 — Deploy the backend (free, no credit card)

**Using Railway:**

1. Go to https://railway.app → sign up with GitHub (free tier, no card needed)
2. Push the `backend/` folder to a new GitHub repo
3. In Railway: **New Project → Deploy from GitHub repo** → select your repo
4. Railway auto-detects Python via `requirements.txt` and `Procfile`
5. Go to your service → **Variables** tab → add:
   ```
   ANTHROPIC_API_KEY = sk-ant-your-key-here
   ```
6. Railway gives you a public URL like `https://devlens-ai-production.up.railway.app`
7. Test it: visit `https://your-url.up.railway.app/health` — should show `{"ok":true,"key_set":true}`

**Alternative — Render.com (also free, no card):**
1. https://render.com → New → Web Service → connect your repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the same `ANTHROPIC_API_KEY` environment variable

## Step 3 — Host the frontend (free)

**Easiest — Netlify Drop:**
1. Go to https://app.netlify.com/drop
2. Drag the `frontend/index.html` file in
3. You get a public URL instantly — share it with anyone

**Or GitHub Pages:** push `frontend/index.html` to a repo, enable Pages in repo settings.

## Step 4 — Connect them

1. Open your deployed frontend URL
2. In the top nav bar, paste your Railway backend URL into the **Backend URL** box
3. Status badge turns green (✓ Backend connected) — you're live
4. The browser remembers the backend URL (localStorage), so you only set it once

## Using it

1. **Load codebase** tab → paste a public GitHub URL or drag-drop local files → **Index codebase**
2. **Ask AI** tab → use quick-chips or type any question
3. **Project summary** tab → generate README, tech stack breakdown, security audit, etc.

## Cost reality check

- Railway free tier: 500 hours/month + $5 trial credit — plenty for personal/demo use
- Claude Haiku 4.5 (used by default): cheapest current model, ~$0.001 per question
- Anthropic free trial credits cover hundreds of questions before you'd need to add billing

## Notes

- Model is set to `claude-haiku-4-5-20251001` in `backend/main.py` — fast and cheap. Change to `claude-sonnet-4-6` for higher quality answers if you don't mind slightly higher cost.
- GitHub loading is capped at 80 files and skips `node_modules`, `.git`, `dist`, `build`, etc.
- Indexing/chunking happens entirely in the browser — only relevant chunks are sent to your backend.
