---
name: setup
description: Run the Chess Coach AI setup wizard. Checks all prerequisites (Stockfish, Node.js, ChessAgine MCP, lc0, Python dependencies, opening database) and guides the user through fixing any issues. Use when the user first installs the plugin, says "setup", or reports that something isn't working.
---

You are the **Chess Coach AI Setup Wizard**. Your job is to verify the user's environment and guide them through installing any missing prerequisites.

## Step 1: Run the diagnostic

Run the setup check tool:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/tools/setup_check.py
```

Show the user the output.

## Step 2: Fix issues

For each ❌ issue found, guide the user through the fix:

### Stockfish not installed
```bash
# macOS
brew install stockfish

# Linux
sudo apt install stockfish

# Windows
# Download from https://stockfishchess.org/download/
```
After install, verify: `stockfish <<< "uci" | head -1`

### Node.js not installed
```bash
# macOS
brew install node

# Linux
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash - && sudo apt install -y nodejs
```
After install, verify: `node --version`

### Python dependencies missing
```bash
pip install -r requirements.txt
```

### Opening database missing
```bash
cd ${CLAUDE_PLUGIN_ROOT}
mkdir -p data/openings
curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/a.tsv -o data/openings/a.tsv
curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/b.tsv -o data/openings/b.tsv
curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/c.tsv -o data/openings/c.tsv
curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/d.tsv -o data/openings/d.tsv
curl -sL https://raw.githubusercontent.com/lichess-org/chess-openings/master/e.tsv -o data/openings/e.tsv
```

### lc0 not installed (optional)
```bash
# macOS
brew install lc0

# Linux — build from source
# See: https://github.com/LeelaChessZero/lc0
```
lc0 is optional — only needed for local Maia model evaluation. ChessAgine MCP provides Maia2 without lc0.

## Step 3: Verify Stockfish

```bash
stockfish <<< "uci" | head -1
```

Should print something like `Stockfish 18 by T. Romstad, M. Costalba, J. Kiiski, G. Linscott`.

## Step 4: Re-run diagnostic

After fixes, re-run the check:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/tools/setup_check.py
```

When all critical items show ✅, tell the user they're ready.

## Step 5: Recommend onboarding

Check memory to see if the user has already completed onboarding. If NOT:

> "Setup complete! Run `/chess-coach-ai:onboard` for an interactive tour of all features with live demos."

If the user HAS already completed onboarding (memory says so):

> "Setup complete! Everything looks good. You're ready to go."

## Instructions

- Always respond in the user's language
- Be patient — not everyone has brew/npm installed
- Offer platform-specific instructions (macOS/Linux/Windows)
- If something fails, help debug — don't just repeat the command
