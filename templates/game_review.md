# Game Review

**Game ID:** {{game_id}} | **Result:** {{result}} | **Color:** {{user_color}}

---

## Performance Summary

| Metric | Score |
|--------|-------|
| **ACPL** | {{acpl}} |
| **DQM** | {{dqm}} |
| **Opening Accuracy** | {{opening_accuracy}} |
| **Middlegame Accuracy** | {{middlegame_accuracy}} |
| **Endgame Accuracy** | {{endgame_accuracy}} |

**Structure Played:** {{structure_played}} ({{structure_performance_percentile}} percentile)

## Critical Moments

{{#critical_moments}}
### Move {{move_number}}: {{user_move}} ({{classification}})

- **Best Move:** {{best_move}}
- **Maia Prediction:** {{maia_prediction}} (level {{maia_level}})
- **Eval Loss:** {{eval_loss_cp}} cp
- **Theme:** {{training_theme}}

> {{explanation}}

{{/critical_moments}}

## Training Recommendations

{{#recommended_study}}
- {{.}}
{{/recommended_study}}
