# Synthetic engagement features: realism & production data

*Addresses reviewer feedback: "discuss how well these engineered features
represent real customer behavior and what additional production data would be
required."*

The public Telco dataset has no behavioural/usage signals, yet the literature
(García et al., 2018; Amin et al., 2019) identifies declining usage and support
friction as the **strongest** churn predictors. To model a realistic digital
subscription we synthesised five engagement features, conditioned on the real
churn label with heavy class overlap and ~8% label noise so no feature is a
give-away.

| Synthetic feature | Real-behaviour proxy | How faithful | Production data source |
|---|---|---|---|
| `logins_30d` | Product stickiness / active use | High — logins are a standard engagement KPI; our declining-for-churners pattern matches observed behaviour | App auth logs / session events (Segment, Amplitude, Mixpanel) |
| `features_used` (of 10) | Depth of adoption | Medium–high — breadth of feature use correlates with retention, but "10 key features" is product-specific | Product analytics feature-flag / event tracking |
| `open_tickets_30d` | Unresolved support friction | High — directly documented as predictive; count is realistic but ignores severity/sentiment | Support desk (Zendesk, Intercom) |
| `days_since_last_interaction` | Recency of engagement | High — recency is one of the most reliable churn signals (RFM) | Event stream / last-seen timestamp |
| `usage_change_pct` | Trend in engagement | High conceptually, but our single-period delta is simpler than a real rolling trend | Time-series of usage aggregated per period |

## Limitations of the synthetic approach

- **Independence assumption.** Each feature was drawn independently per customer;
  in reality logins, recency and usage-change are strongly correlated. Real data
  would have richer (and partly redundant) covariance structure.
- **Stationary distributions.** We used fixed class-conditional distributions;
  real behaviour drifts with seasonality, releases and pricing changes — the very
  reason monthly retraining is in the design.
- **No true temporal dynamics.** `usage_change_pct` is a one-shot delta rather than
  a real trajectory; production should use rolling windows (e.g. 4-week slopes).

## Additional production data that would replace the synthetic layer

1. **Event-level telemetry** — logins, feature events, session duration, per user
   over time (for proper trend features, not a single delta).
2. **Support & satisfaction** — ticket volume, resolution time, CSAT/NPS, sentiment.
3. **Billing & payment health** — failed payments, downgrades, refunds, coupon use.
4. **Commercial context** — plan changes, seat count, contract renewal dates.
5. **Outcome logging** — retention actions taken and whether they worked, to close
   the loop and estimate the intervention-success rate empirically (instead of the
   assumption used in the sensitivity analysis).
