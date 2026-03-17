# Intelligence Dossier: {{username}}

**Platform:** {{platform}} | **Last Updated:** {{last_updated}}

---

## Player Profile

| Metric | Value |
|--------|-------|
| **Bullet** | {{ratings.bullet}} |
| **Blitz** | {{ratings.blitz}} |
| **Rapid** | {{ratings.rapid}} |
| **Classical** | {{ratings.classical}} |
| **Games Analyzed** | {{games_analyzed}} |

## Playing Style

**Archetype:** {{style_archetype}}
**Sub-profile:** {{style_sub_profile}}
**Average ACPL:** {{acpl_avg}}

## Opening Weaknesses

{{#opening_weaknesses}}
- **{{name}}** ({{eco}}, {{color}}): Win rate {{win_rate}}% over {{games}} games
{{/opening_weaknesses}}

## Comfort Lines

{{#comfort_lines}}
- **{{name}}** ({{eco}}, {{color}}): Win rate {{win_rate}}% over {{games}} games
{{/comfort_lines}}

## Clock Management

- **Time Trouble Frequency:** {{time_trouble_frequency}}%
- **Clock Inflection Point:** Move {{clock_inflection_point.move_number}} (avg error spike: {{clock_inflection_point.avg_error_spike}} cp)

## Recent Form

**Trend:** {{recent_form}}

## Recommended Strategy

Based on the analysis above, the agent should generate specific strategic recommendations targeting the opponent's weaknesses.
