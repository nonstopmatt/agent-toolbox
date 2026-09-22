---
name: self-improvement-report
description: Report on what the task-observer and skill-observations system has logged and changed. Use only when the user runs /self-improvement-report or asks how Claude has been improving itself.
model: claude-sonnet-5
---
Say in one line which model is running, so a silently-dropped `model:` field is
visible. (Sonnet, not Haiku: Haiku is NOT in this account's session-model
allowlist -- fable-5-1, opus-5, opus-4-8, sonnet-5 -- so `model: claude-haiku-4-5`
was accepted by the parser and silently discarded at runtime. Verified 2026-09-20.) (Two known silent-failure cases: the model is outside this session's
availableModels allowlist, or auto mode skipped it because fast mode is disabled
by config.)

Read the 20 newest files in ~/.claude/skill-observations/observation-log/
and the "Skill fixes" section of ~/.claude/CLAUDE.md. Summarize in
under 300 words: patterns observed, skill changes with dates,
suggestions not yet applied. Change nothing. Outside this skill,
never bring up observations or self-improvement activity.

If a review is due, say so in one line and point at /skill-review. Do not run
the review here -- this skill reads and reports, it never edits a skill.
