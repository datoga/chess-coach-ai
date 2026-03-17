# Training Roadmap

**Estimated Level:** {{user_profile.estimated_level}} | **Games Analyzed:** {{user_profile.games_analyzed}} | **Last Updated:** {{user_profile.last_updated}}

---

## Current Training Balance

| Phase | Weight | Default |
|-------|--------|---------|
| Openings | {{phase_balance.openings.weight}}% | {{phase_balance.openings.default}}% |
| Middlegame | {{phase_balance.middlegame.weight}}% | {{phase_balance.middlegame.default}}% |
| Endgame | {{phase_balance.endgame.weight}}% | {{phase_balance.endgame.default}}% |
| Tactics | {{phase_balance.tactics.weight}}% | {{phase_balance.tactics.default}}% |

## Active Weaknesses

{{#active_weaknesses}}
### {{theme}} ({{phase}}) — {{severity}}

- **Recurrence:** {{recurrence}} times
- **First Detected:** {{first_detected}}
- **Last Seen:** {{last_seen}}
- **Trend:** {{improvement_trend}}
- **Progress:** {{prescribed_sessions_completed}}/{{prescribed_sessions_total}} sessions

{{/active_weaknesses}}

## Strengths

{{#strengths}}
- **{{theme}}** ({{phase}}): Win rate {{win_rate}}% over {{games}} games
{{/strengths}}

## Next Session Plan

{{#next_session_plan}}
1. **{{activity}}** ({{duration_min}} min)
{{/next_session_plan}}
