# Post-performance analysis (Instagram + YouTube)

Run when the owner asks for an analysis. An analysis is not finished until the data is saved.

## 1. Collect (Instagram Graph API / MCP)

1. Profile info (followers, following, media count, bio).
2. Recent media (limit ~30) — large output; parse with Python/jq, don't read raw.
3. Media insights for every post since the last analysis, plus posts that were < 7 days old last time (to record their 7-day numbers).
4. Account insights: `follower_demographics`, `period=lifetime`, `breakdown=country`; optionally follower/non-follower split.
5. Follows/unfollows and per-reel "Follows" / profile visits are **not** returned by the API for Reels (error 100) — record numbers the owner reads from the app.
6. If comment `data` comes back empty while counts are non-zero, the Meta app is probably in Development mode → owner switches it to Live, or read via browser.

## 2. Save (mandatory)

```
analytics/raw/YYYY-MM-DD/*.json        raw output of every call
analytics/posts.csv                    one row per post × checkpoint (upsert, never duplicate)
analytics/account.csv                  one row per analysis
analytics/reports/YYYY-MM-DD.md        the report
```

`posts.csv` columns:
```
analysis_date,media_id,published_at,age_days,checkpoint,type,episode,short_id,hook_variant,phase,anchor,hook_format,hook_text,duration_s,reach,views,likes,comments,shares,saves,avg_watch_s,skip_rate,share_per_reach,save_per_reach,collab,notes,permalink
```
- `checkpoint`: `24h` (age 1–2 d), `7d` (7–9 d), else `snapshot`.
- Define project-specific taxonomies (e.g. `phase`, `anchor` = movement / case / concept) in a `PHASES.md` and keep them stable.
- `hook_format`: contrast, concept question, myth, cost of inaction, narrative, advice, news, other.
- Ratios to 4 decimals.

`account.csv`: `analysis_date,followers,follows,media_count,followers_delta,follows_manual,unfollows_manual,top_countries,bio_aligned,posts_analyzed,notes` (`top_countries` like `IR:1415|TR:131|…`).

## 3. Analyse

1. Best and worst post by share/reach and skip rate.
2. Mean skip rate and share/reach per hook format; median/max reach per topic taxonomy — control for collab status and production tier, or state explicitly that they are confounded.
3. A/B hooks of the same short.
4. Reach trend of consecutive posts and effect of publish spacing.
5. Follower change vs last analysis; follows per 1,000 reach (growth bottleneck is usually viewer → follower conversion, ~2/1k is typical).
6. Exclude posts < 24 h from conclusions; for them report only skip rate and watch time as "provisional".
7. Compare posts only at equal age.

### Evaluation framework

- **Outliers** are not baselines. A post leaves outlier status only when its pattern is reproduced by changing parameters you control (topic, hook, length, named teaser, collabs, timing). Until then it's a hypothesis. Compare cluster members with the cluster median and everything else with the non-outlier median at equal age.
- **Before crediting content for a spike, ask the owner whether a big account shared it** — the API can't show story shares.
- **Baseline by collab status and face**: a non-collab post with the creator on camera has lower share odds than a collab reel with AI characters. Don't call a low-reach post restricted/shadowbanned without evidence from the app's Account Status.
- Collab acceptance timing is unpredictable — never assume hour-one acceptance or credit a jump to a collab without evidence; record what's known (count, partial collab) in `notes`.
- Record external context the owner mentions (trending topic, authority mentions, mutual collabs same day) — for interpretation, not control.
- **Two speeds**: snapshot + data every time; rule-change proposals only in a weekly review and only when ≥ 3 equal-age posts show the pattern. Strategy improves, it doesn't flip. Security/brand issues are immediate exceptions.
- Success = engagement (deep engagement = shares + saves + comments per reach; follows/reach), not reach alone.
- Early warning of format fatigue: saves and shares slowly falling while likes stay flat. 🟡
- Consecutive posts are not a randomised experiment — say so.

## 4. Report

- Write the report, show the owner a short summary.
- Append only **new** lessons to `DECISIONS.md` under a dated heading.
- Changes to workflow/strategy files are proposals; apply only after approval.

## Checklist

- [ ] raw saved · [ ] posts.csv upserted · [ ] account.csv row · [ ] report saved · [ ] new lessons logged

## YouTube appendix

- Data API v3 with the uploader token: channel stats + all public and scheduled videos → `analytics/youtube/{raw/,videos.csv,channel.csv,reports/}`.
- Check upcoming schedules: flag more than one short per day or two videos in the same minute.
- Traffic sources, retention, watch time and CTR need the YouTube Analytics API (`yt-analytics.readonly`) or a Studio export; record "not available" until enabled.
- Lessons that held: poetic titles are unsearchable; searchable explainers in the audience's language with real case studies grow channels; side content must never displace the main series' slots.
