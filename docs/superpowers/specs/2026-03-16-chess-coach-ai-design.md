# Chess Coach AI — Phase 1 Design Specification

## Overview

AI-powered chess coaching system built as a **Claude Code plugin** with a multi-agent architecture designed for **cowork** (agent teams). The system treats chess players as cognitive athletes, integrating technical analysis, biohacking, and applied psychometrics.

**Plugin name:** `chess-coach-ai`
**Platform:** Lichess-first (Chess.com prepared for Phase 2)
**Architecture:** Claude Code plugin with 4 specialized agents + coordinator skill
**Storage:** Google Drive primary, local fallback

---

## 1. Plugin Structure

```
chess-coach-ai/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── agents/
│   ├── intel.md
│   ├── gm.md
│   ├── mind.md
│   └── biohack.md
├── skills/
│   └── coach/
│       ├── SKILL.md
│       ├── eval-set.json
│       └── evals/
│           └── evals.json
├── hooks/
│   └── hooks.json
├── tools/
│   ├── lichess_client.py
│   ├── chessdb_client.py
│   ├── pgn_parser.py
│   ├── time_analysis.py
│   ├── style_classifier.py
│   ├── error_classifier.py
│   ├── dqm_calculator.py
│   ├── wellness_tracker.py
│   ├── game_vault.py
│   ├── opening_classifier.py
│   ├── tactics_generator.py
│   ├── validate_schema.py
│   └── detect_pgn_save.py
├── data/
│   ├── schemas/
│   │   ├── player_report.json
│   │   ├── game_analysis.json
│   │   ├── training_insights.json
│   │   ├── mental_profile.json
│   │   ├── biohack_protocol.json
│   │   ├── roadmap_state.json
│   │   └── game_vault_entry.json
│   ├── supplements.json
│   ├── nutrition_protocols.json
│   └── openings/
│       └── (lichess-org/chess-openings TSV data)
├── templates/
│   ├── intel_dossier.md
│   ├── game_review.md
│   ├── training_roadmap.md
│   └── pre_game_protocol.md
├── vault/
│   └── .gitkeep
├── tests/
│   ├── test_lichess_client.py
│   ├── test_chessdb_client.py
│   ├── test_pgn_parser.py
│   ├── test_time_analysis.py
│   ├── test_style_classifier.py
│   ├── test_error_classifier.py
│   ├── test_dqm_calculator.py
│   ├── test_game_vault.py
│   ├── test_wellness_tracker.py
│   ├── test_opening_classifier.py
│   └── test_tactics_generator.py
├── evals/
│   ├── intel/
│   │   ├── eval-set.json
│   │   └── evals.json
│   ├── gm/
│   │   ├── eval-set.json
│   │   └── evals.json
│   ├── mind/
│   │   ├── eval-set.json
│   │   └── evals.json
│   └── biohack/
│       ├── eval-set.json
│       └── evals.json
├── requirements.txt
├── CLAUDE.md
├── README.md
└── .gitignore
```

### Plugin Manifest (.claude-plugin/plugin.json)

```json
{
  "name": "chess-coach-ai",
  "description": "AI-powered chess coaching system with multi-agent architecture. Integrates technical analysis, biohacking, and applied psychometrics to treat chess players as cognitive athletes.",
  "version": "0.1.0",
  "author": { "name": "datoga" },
  "license": "MIT",
  "keywords": ["chess", "coaching", "lichess", "stockfish", "biohacking", "training"]
}
```

### MCP Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "chessagine": {
      "command": "npx",
      "args": ["-y", "chessagine-mcp"]
    }
  }
}
```

ChessAgine provides: Stockfish 18, Maia2, Lichess game retrieval, board visualization, PGN support. All cowork teammates inherit this automatically.

---

## 2. Agent Architecture

### Agents

| Agent | File | Role |
|-------|------|------|
| **Intel** | `agents/intel.md` | Intelligence gathering & reconnaissance — profiles opponents and users via Lichess API, Opening Explorer, chessdb.cn |
| **GM** | `agents/gm.md` | Grandmaster-level analysis — Stockfish/Maia evaluation, error classification, training roadmaps, auto-analysis |
| **Mind** | `agents/mind.md` | Mental performance — tilt detection, time pattern analysis, emotional error classification, resilience protocols |
| **Biohack** | `agents/biohack.md` | Biohacking & performance — nutrition, sleep, supplementation, pre-game protocols, wearable interface (future) |

### Coordinator

The skill `/chess-coach-ai:coach` acts as the coordinator. It receives user requests, determines which agents to dispatch via cowork, and synthesizes their outputs into unified reports in the user's language.

### Communication Flow

Agents do not communicate directly. The coordinator is the hub:

```
Intel ──→ Coordinator ──→ GM (passes player_report for repertoire prep)
Mind  ──→ Coordinator ──→ GM (adjusts roadmap based on psychological patterns)
Biohack → Coordinator ──→ GM (reduces study load if physical state is low)
```

Contracts are defined in `data/schemas/` — each agent produces and consumes JSON with predefined structure.

### Main Flows

| Flow | Trigger | Agents | Output |
|------|---------|--------|--------|
| **Pre-game prep** | "prepare my game against {user}" | Intel → GM + Biohack | Intelligence dossier + opening prep + pre-game protocol |
| **Game review** | User pastes PGN or "review my last game" | GM + Mind | Technical + psychological analysis, saved to vault |
| **Training roadmap** | "create a training plan" | GM + Mind + Biohack | Personalized syllabus with wellness integration |
| **Quick intel** | "intel on {user}" | Intel only | Player profile + stats + weaknesses |
| **Session check-in** | "starting a training session" | Biohack + GM | Adapted session plan based on current state |
| **Save game** | User pastes PGN + "save this game" | GM (tags) | Game stored in vault with metadata |
| **Add opponent game** | PGN or Lichess URL + "add opponent game" | Intel | Stored in vault/opponents/{username} |
| **Import games** | "import my games from lichess" | Intel | Batch download → vault |

### Agent Dependencies per Flow

```
PRE-GAME:  Intel ──→ GM (needs player_report for repertoire)
           Biohack runs in parallel (no dependency)
           Mind not needed

REVIEW:    GM + Mind run in parallel (both read PGN independently)
           GM auto-generates training_insights

ROADMAP:   GM first (needs game history analysis)
           Then Mind + Biohack in parallel
           Coordinator merges all three
```

---

## 3. Agent Detail: Intel

**Role:** Intelligence gathering & reconnaissance.

### Tools

- `lichess_client.py` — Player stats, game history, activity
- `chessdb_client.py` — Position-based lookups (opening book depth)
- `pgn_parser.py` — Parse downloaded games
- `time_analysis.py` — Clock usage patterns per move
- `style_classifier.py` — Classify into archetypes (activist/theorist/defender) and sub-profiles (precision_player/chaos_specialist based on ACPL in quiet vs complex positions)
- `opening_classifier.py` — ECO code + opening name via lichess-org/chess-openings
- `game_vault.py` — Store/retrieve opponent PGNs
- **ChessAgine MCP** — Lichess game retrieval, opening explorer

### Output Schema: player_report.json

```json
{
  "username": "string",
  "platform": "lichess",
  "ratings": { "bullet": 0, "blitz": 0, "rapid": 0, "classical": 0 },
  "games_analyzed": 0,
  "style_archetype": "activist|theorist|defender",
  "style_sub_profile": "precision_player|chaos_specialist|balanced",
  "acpl_avg": 0.0,
  "clock_inflection_point": { "move_number": 35, "avg_error_spike": 2.3 },
  "opening_weaknesses": [
    { "eco": "B12", "name": "Caro-Kann", "color": "black", "win_rate": 0.38, "games": 42 }
  ],
  "comfort_lines": [
    { "eco": "B90", "name": "Sicilian Najdorf", "color": "black", "win_rate": 0.72, "games": 89 }
  ],
  "time_trouble_frequency": 0.35,
  "recent_form": "improving|stable|declining",
  "last_updated": "ISO-8601"
}
```

### Key Logic

- Opening Explorer filtered by opponent: detects lines with win rate < 45%
- ACPL crossover: quiet positions vs chaotic → `style_sub_profile` classification (precision_player, chaos_specialist, or balanced)
- Clock inflection point: which move the opponent starts making systematic blunders
- Generates dossier using `templates/intel_dossier.md`

---

## 4. Agent Detail: GM

**Role:** Grandmaster-level analysis, error classification, training roadmaps, auto-analysis.

### Tools

- **ChessAgine MCP** — Stockfish 18 eval, Maia2 (human move prediction), board visualization
- `pgn_parser.py` — Decompose games into positions
- `error_classifier.py` — Classify errors by cognitive origin
- `dqm_calculator.py` — Decision Quality Metric
- `opening_classifier.py` — ECO code classification
- `game_vault.py` — Read/write games and insights
- `tactics_generator.py` — Wraps pgn-tactics-generator and chess-artist for puzzle generation
- **chess-artist** — Auto-PGN annotation + puzzle generation
- **pgn-tactics-generator** — Tactical puzzles from user's own blunders
- **cdblib** — Cloud eval fallback via chessdb.cn
- **syzygy-tables.info** — Online endgame tablebase probing

### Output Schema: game_analysis.json

```json
{
  "game_id": "string",
  "user_color": "white|black",
  "result": "1-0|0-1|1/2",
  "acpl": 28.5,
  "dqm": 0.82,
  "critical_moments": [
    {
      "move_number": 23,
      "user_move": "Nf3",
      "best_move": "d5",
      "maia_prediction": "Nf3",
      "maia_level": 1500,
      "eval_loss_cp": 120,
      "classification": "pattern_recognition_failure|conceptual_weakness|tactical_miss|time_pressure",
      "explanation": "string",
      "training_theme": "central_pawn_break"
    }
  ],
  "opening_accuracy": 0.92,
  "middlegame_accuracy": 0.78,
  "endgame_accuracy": 0.65,
  "structure_played": "sicilian_hedgehog",
  "structure_performance_percentile": 0.70,
  "recommended_study": ["isolated_queen_pawn", "rook_endgames"]
}
```

### Auto-Analysis Flow

When the user saves a game (or imports a batch), GM auto-triggers:

1. Full positional analysis (Stockfish + Maia)
2. Error classification (cognitive origin)
3. DQM calculation
4. Training insights generation
5. Insights appended to vault index

### Training Insights Schema: training_insights.json

```json
{
  "training_insights": {
    "game_id": "string",
    "date": "ISO-8601",
    "insights": [
      {
        "theme": "rook_endgame_technique",
        "severity": "critical|important|minor",
        "phase": "opening|middlegame|endgame|tactics",
        "description": "Failed to build a bridge in a Lucena position at move 52",
        "position_fen": "8/5k2/R7/1r6/5PK1/8/8/8 w - - 0 52",
        "user_move": "Ra7",
        "best_move": "Rf6+",
        "study_recommendation": "Lucena position drill — execute 10 times vs engine",
        "tags": ["endgame", "rook_endgame", "lucena", "technique"],
        "recurrence": 3
      }
    ],
    "pattern_summary": {
      "strengths_confirmed": ["opening_preparation"],
      "weaknesses_confirmed": ["endgame_technique"],
      "new_weakness_detected": ["time_management_after_move_35"],
      "improvement_since_last": ["central_pawn_breaks"]
    },
    "roadmap_update": {
      "increase_priority": ["rook_endgames"],
      "decrease_priority": [],
      "add_topic": ["bridge_building_technique"],
      "suggested_block_rebalance": {
        "openings": 15,
        "middlegame": 30,
        "endgame": 35,
        "tactics": 20
      }
    }
  }
}
```

### Key Logic

- Compares user move vs Stockfish (optimal) vs Maia (human at user's level)
- Maia predicts for lower level → "Pattern Recognition Failure"
- Maia correct but deep strategic error → "Conceptual Weakness"
- DQM (Decision Quality Metric) = normalized score from 0.0 to 1.0 measuring decision consistency. Calculated as `1 - (ACPL / max_expected_acpl_for_level)`, where `max_expected_acpl_for_level` is calibrated per rating band. Unlike ACPL (raw centipawn loss), DQM is level-relative: a DQM of 0.82 means the user played at 82% of their expected best. This allows tracking improvement independently of opponent strength or game result.
- For prep: receives `player_report` from Intel → selects lines exploiting opponent weaknesses
- Auto-generates tactical puzzles from user's own blunders via pgn-tactics-generator

---

## 5. Agent Detail: Mind

**Role:** Mental performance analysis — psychological patterns, emotional states, decision quality under pressure.

### Tools

- `time_analysis.py` — Time per move patterns
- `error_classifier.py` — Behavioral error classification
- `pgn_parser.py` — Game sequence analysis (post-loss patterns)

### Output Schema: mental_profile.json

```json
{
  "tilt_detected": false,
  "tilt_type": "none|injustice|hate_to_lose|panic_admin",
  "tilt_evidence": "string",
  "decision_patterns": {
    "impulsive_moves": { "count": 3, "avg_time_seconds": 8, "positions": "complex" },
    "paralysis_moves": { "count": 1, "avg_time_seconds": 840, "quality": "mediocre" }
  },
  "tension_management": {
    "premature_simplification_rate": 0.25,
    "pieces_traded_when_ahead": 0.60
  },
  "post_loss_pattern": "aggressive_overcompensation|passive_withdrawal|stable",
  "resilience_score": 0.7,
  "recommended_interventions": [
    {
      "type": "breathing_exercise|candidate_moves_drill|review_winning_game|meditation",
      "trigger": "before_game|after_loss|during_time_pressure",
      "description": "string"
    }
  ],
  "session_recommendation": "play|study_only|rest"
}
```

### Key Logic

- Error in < 10s in complex position → impulsivity → candidate moves drill
- Error after > 15min thought → paralysis → pattern recognition exercises
- Post-loss sequence with elevated ACPL → tilt → recalibration protocol
- Premature simplification when ahead → "Panic Admin"
- If `session_recommendation: "rest"` → coordinator skips heavy study assignments

---

## 6. Agent Detail: Biohack

**Role:** Physical and biochemical performance optimization.

### Tools

- `wellness_tracker.py` — Collect/store manual input (sleep, food, energy, HRV)

### Input/Output Schema: biohack_protocol.json

```json
{
  "current_state": {
    "sleep_hours": 7,
    "sleep_quality": "good|fair|poor",
    "hrv": null,
    "energy_level": 7,
    "last_meal_hours_ago": 2,
    "hydration": "adequate|low"
  },
  "competition_phase": "pre_tournament|game_day|between_rounds|post_game|rest_day",
  "protocol": {
    "nutrition": [
      { "timing": "3h_before_game", "recommendation": "string", "rationale": "string" }
    ],
    "supplementation": [
      { "name": "L-Theanine + Caffeine", "dose": "200mg/100mg", "timing": "1h_before", "evidence_level": "strong" }
    ],
    "physical": [
      { "activity": "20min walk to venue", "timing": "45min_before", "purpose": "circulation + mindfulness" }
    ],
    "mental": [
      { "technique": "Botvinnik rest protocol", "duration_min": 60, "timing": "2h_before" }
    ],
    "recovery": [
      { "action": "no screens 90min before sleep", "purpose": "maximize REM consolidation" }
    ]
  },
  "training_intensity_modifier": 1.0,
  "alerts": ["Low sleep detected — reduce new opening study, prioritize review"]
}
```

### Input Schema: biohack_protocol.json > current_state

The `current_state` object in `biohack_protocol.json` serves as the wellness input contract. The Biohack agent collects this data via `wellness_tracker.py` (either `from_manual()` conversational prompts or `from_wearable()` in a future phase). The full `biohack_protocol.json` schema (shown above) acts as both input and output: `current_state` is populated by the user, and `protocol` is generated by the agent.

### Key Logic

- sleep < 6h or energy < 5 → `training_intensity_modifier: 0.6`, alert to GM
- Nutrition protocol adapted by competition phase (from `nutrition_protocols.json`)
- Evidence-based supplementation only (from `supplements.json`)
- Wearable interface prepared: `wellness_tracker.py` has `from_manual()` and `from_wearable()` methods (latter raises `NotImplementedError` with instructions)

---

## 7. Game Vault

### Storage Strategy

```
Google Drive (primary)
  └── chess-coach-ai/
      ├── my-games/
      ├── opponents/{username}/
      ├── insights/
      ├── index.json
      └── roadmap_state.json

Local fallback (vault/)
  └── same structure
```

- `game_vault.py` tries Google Drive first (REST API + OAuth2)
- No credentials or connection failure → transparent fallback to local `vault/`
- Bidirectional sync when connection recovers
- User can add PGNs from any source: paste in chat, local file, Lichess URL

### Vault Entry Schema: game_vault_entry.json

Each stored game is wrapped in a metadata envelope:

```json
{
  "game_id": "string (hash of PGN)",
  "source": "manual|lichess_import|lichess_url",
  "category": "my_game|opponent_prep",
  "opponent_username": "string|null",
  "date_played": "ISO-8601",
  "date_stored": "ISO-8601",
  "time_control": "string (e.g. 600+0)",
  "result": "1-0|0-1|1/2",
  "user_color": "white|black|unknown",
  "opening_eco": "string",
  "opening_name": "string",
  "tags": ["string"],
  "pgn_file": "relative path to .pgn file",
  "insights_file": "relative path to insights .json|null",
  "auto_analyzed": false,
  "sync_status": "local_only|synced|pending_sync"
}
```

### Schema: roadmap_state.json

The `data/schemas/roadmap_state.json` schema validates the `vault/roadmap_state.json` state file. The `phase_balance` keys are canonical: `openings`, `middlegame`, `endgame`, `tactics`. All references — including `suggested_block_rebalance` in `training_insights.json` — must use these exact keys.

### Add Game Flows

| Action | Input | Result |
|--------|-------|--------|
| "save this game" + pasted PGN | Raw PGN | GM auto-tags → vault (my-games) |
| "add opponent game" + PGN or URL | PGN/Lichess URL | Stored in opponents/{username} |
| "import my games from lichess" | Username + date range | Intel downloads via API → vault (my-games) |
| "prepare against {user}" | Username | Intel fetches + downloads → opponents/{user} |

### Vault Structure

```
vault/
├── my-games/
│   ├── 2026-03-16_user_vs_opponent_sicilian.pgn
│   └── ...
├── opponents/
│   └── {username}/
│       ├── game1.pgn
│       └── ...
├── insights/
│   ├── 2026-03-16_user_vs_opponent_insights.json
│   └── ...
├── index.json
└── roadmap_state.json
```

---

## 8. Training Engine — Long-term Roadmap

### Three Dimensions

The roadmap is a **living syllabus** that recalibrates with every analyzed game based on what the user actually fails at.

#### Openings (moves 1-15)
- **Detection:** Comparison vs opening book + Stockfish
- **Metrics:** Repertoire coverage, novelty handling, preparation depth, transposition awareness
- **Example prescription:** "Study 5 master games in the Advance French with early Nc6. Play 10 training games forcing this line."

#### Middlegame (moves 15-35)
- **Detection:** Structure-based analysis + Maia comparison
- **Metrics:** Structure win rate (per pawn structure type), plan execution, tactical alertness, tension management, piece activity
- **Example prescription:** "Study Kasparov's IQP masterclass. Key: keep pieces on, attack before endgame. Play 5 games where you must NOT trade queens with IQP."

#### Endgame (moves 35+)
- **Detection:** Tablebase comparison + technique evaluation
- **Metrics:** Conversion rate, theoretical knowledge, technique under time pressure, drawn endgame defense
- **Example prescription:** "Learn bridge technique: execute Lucena 10x vs engine. Practice Philidor defense 10x."

### roadmap_state.json

```json
{
  "user_profile": {
    "estimated_level": 1650,
    "games_analyzed": 87,
    "last_updated": "2026-03-16"
  },
  "phase_balance": {
    "openings": { "weight": 20, "default": 20 },
    "middlegame": { "weight": 35, "default": 35 },
    "endgame": { "weight": 25, "default": 15 },
    "tactics": { "weight": 20, "default": 30 }
  },
  "active_weaknesses": [
    {
      "id": "w_001",
      "theme": "rook_endgame_technique",
      "phase": "endgame",
      "severity": "critical",
      "recurrence": 5,
      "first_detected": "2026-01-10",
      "last_seen": "2026-03-14",
      "improvement_trend": "stagnant",
      "prescribed_sessions_completed": 2,
      "prescribed_sessions_total": 5
    }
  ],
  "resolved_weaknesses": [
    {
      "id": "w_000",
      "theme": "back_rank_mate_blindness",
      "phase": "tactics",
      "resolved_date": "2026-02-20",
      "sessions_to_resolve": 3,
      "games_since_last_occurrence": 22
    }
  ],
  "strengths": [
    { "theme": "sicilian_najdorf_white", "phase": "openings", "win_rate": 0.72, "games": 18 }
  ],
  "repertoire": {
    "white": {
      "main_line": "1.e4",
      "vs_sicilian": "Open Sicilian",
      "vs_french": "Advance Variation",
      "vs_caro_kann": "needs_preparation",
      "coverage_score": 0.75
    },
    "black": {
      "vs_e4": "Sicilian Najdorf",
      "vs_d4": "Queen's Gambit Declined",
      "vs_c4": "needs_preparation",
      "coverage_score": 0.60
    }
  },
  "next_session_plan": [
    { "weakness_id": "w_001", "activity": "Lucena drill 10x vs engine", "duration_min": 30 },
    { "weakness_id": "w_002", "activity": "Review annotated IQP game #4", "duration_min": 20 },
    { "weakness_id": null, "activity": "Tactical puzzles — pin/skewer theme", "duration_min": 15 }
  ]
}
```

### Recalibration Logic

```
New game analyzed
     │
     ▼
Theme in active_weaknesses?
     ├── YES → recurrence++ → improvement_trend?
     │         ├── stagnant/worsening → severity UP → phase_balance shifts
     │         └── improving → maintain prescription
     │
     └── NO → Significant error (eval loss > 80cp)?
               ├── YES → New active_weakness created
               └── NO → Log but don't act (may be variance)

10+ games without an active_weakness appearing?
     └── YES → Move to resolved_weaknesses → phase_balance rebalances
```

### Cross-agent Integration

```
roadmap_state says: "Priority 1: Lucena drill (30min)"
biohack says: "Low energy, slept 4h, modifier 0.6"

GM adjusts: "Priority 1: Review already-solved Lucena positions (15min, passive study)
             Skip active drills today. Focus on light tactical puzzles."
```

---

## 9. Testing & Evals

### Three-Layer Strategy

#### Layer 1: Unit Tests (pytest)

Standard Python tests for each tool. External APIs mocked.

```
tests/
├── test_lichess_client.py
├── test_chessdb_client.py
├── test_pgn_parser.py
├── test_time_analysis.py
├── test_style_classifier.py
├── test_error_classifier.py
├── test_dqm_calculator.py
├── test_game_vault.py
├── test_wellness_tracker.py
├── test_opening_classifier.py
└── test_tactics_generator.py
```

#### Layer 2: Trigger Evals

Each agent and the main skill have `eval-set.json` with positive (should trigger) and negative (should not trigger) cases. 8-10 of each.

**Example (skills/coach/eval-set.json):**
```json
[
  { "eval_id": "pos_prep", "query": "Prepare my game against DrNykterstein", "should_trigger": true },
  { "eval_id": "pos_review", "query": "Review this game: 1.e4 e5 2.Nf3...", "should_trigger": true },
  { "eval_id": "pos_roadmap", "query": "Create a training plan for me", "should_trigger": true },
  { "eval_id": "neg_general", "query": "What's the weather today?", "should_trigger": false },
  { "eval_id": "neg_code", "query": "Fix the bug in auth.py", "should_trigger": false }
]
```

#### Layer 3: Quality Evals

Assertion-based evals verifying output correctness per flow:

- **Pre-game prep:** Includes opponent rating, opening weaknesses, recommended lines, pre-game protocol
- **Game review:** Identifies critical errors, classifies error type, provides DQM, suggests training
- **Biohack low sleep:** Reduces intensity, addresses nutrition, avoids heavy material
- **Tilt detection:** Detects tilt, recommends break, offers recovery protocol
- **Save game:** Confirms save, tags with opening, includes metadata

Each agent has its own eval suite in `evals/{name}/`.

### Hooks Quality Gate

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/tools/validate_schema.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/tools/detect_pgn_save.py"
          }
        ]
      }
    ]
  }
}
```

---

## 10. Dependencies & External Tools

### Python Dependencies (requirements.txt)

```
chess>=1.11.0
stockfish>=3.28.0
berserk>=0.13.0
cairosvg>=2.7.0
google-api-python-client>=2.0.0
google-auth-oauthlib>=1.0.0
```

### External Data & Tools

| Tool | Source | Purpose |
|------|--------|---------|
| **lichess-org/chess-openings** | GitHub dataset | ECO codes + opening names for automatic classification |
| **pgn-tactics-generator** | GitHub tool | Generate tactical puzzles from user's own blunders |
| **cdblib** | Python library | Cloud eval via chessdb.cn API (100K queries/day, no local engine needed) |
| **chess-artist** | GitHub tool | Auto-annotate PGN + generate puzzles from blunders |
| **syzygy-tables.info** | REST API | Online endgame tablebase probing (no 150GB local download) |

### Required Binaries

```
- Stockfish 18+ (brew install stockfish)
- Node.js 24+ (for ChessAgine MCP server)
- lc0 (optional, for Maia models — brew install lc0)
```

### MCP Server

**ChessAgine** (`npx -y chessagine-mcp`): Stockfish 18, Maia2, Lichess game retrieval, board visualization, PGN support. All cowork teammates inherit automatically.

---

## 11. Error Handling & Resilience

### Fallback Strategy

| Component | Failure | Fallback |
|-----------|---------|----------|
| **Lichess API** | Rate limited (429) | Exponential backoff (1s, 2s, 4s), max 3 retries. If persistent, use cached data from vault |
| **chessdb.cn** | Timeout or quota exceeded | Skip cloud eval, use Stockfish local. Log warning |
| **Stockfish binary** | Not installed or crash | Fall back to ChessAgine MCP eval. If both fail, return analysis without engine eval and warn user |
| **ChessAgine MCP** | Server not running / npx fails | Agent reports missing capability. Coordinator adjusts flow to skip Maia comparison |
| **Google Drive** | No credentials / auth expired / network error | Transparent fallback to local vault. Queue changes for sync when reconnected |
| **syzygy-tables.info** | API down | Skip tablebase probing. Endgame analysis uses Stockfish eval only |
| **PGN parsing** | Malformed PGN | Return parse error with specific line/move. Do not crash the analysis pipeline |

### Validation

- All agent outputs are validated against their JSON schema via the `TaskCompleted` hook before the coordinator accepts them
- If validation fails, the task is rejected and the agent retries once with the validation error as feedback
- `detect_pgn_save.py` checks that written files matching `vault/**/*.pgn` are valid PGN before triggering auto-analysis

### ChessAgine MCP Verification

Before first use, the setup flow must verify ChessAgine's actual tool surface. The spec assumes these capabilities based on published documentation (March 2026). If any tool is missing, the corresponding agent feature degrades gracefully rather than failing entirely.

---

## 12. Multilingual Support

- All code, docs, agent prompts, and templates in **English**
- Agents respond in the user's language (native Claude capability)
- Templates use placeholders, no hardcoded text
- `SKILL.md` instructs: "Always respond in the user's language"

---

## 13. Future Considerations (Not in Phase 1)

- Chess.com API integration (platform abstraction layer ready)
- Wearable integration (Oura, WHOOP) via `wellness_tracker.from_wearable()`
- Premium cloud game storage (shared vault)
- Maia-individual (personalized player modeling)
- Position embeddings via chesspos (recurring pattern clustering)
- Spaced repetition module (Chessdriller integration)
- "Game Intelligence" metric (Chess-Data-Processing)
