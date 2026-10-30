# Saved chess-log viewer

The Flask viewer reads exports from its working directory. It does not run agents
or call OpenAI. Follow the [root setup](../README.md), then use its loopback Flask
CLI command; the original direct-script entry point uses a network-visible debugger.

The list page and `/api/games` enumerate `agent_chess_log_*.txt` files.
`/game/<filename>` renders one export; missing files return 404. Referenced SVG
boards are served from `board_images/`.

A minimal log uses this format:

```text
Date: 2026-10-30 12:00:00
White: DemoWhite
Black: DemoBlack
Mode: COLLABORATIVE
Move 1 - DemoWhite (analytical):
  Move: e2e4
  Reasoning: Synthetic offline example
  Feeling: focused
  Board Image: move_001.svg
```

Put the matching SVG at `board_images/move_001.svg`. These are display records,
not evidence that a model chose the move or experienced the named feeling.
The parser preserves colon-containing field text and reports unreadable-file
errors. Generated reflection/evolution/feedback text uses normal template
escaping; CSS preserves line breaks without treating the text as executable HTML.

On 2026-10-30, parser/rendering regressions, synthetic list/detail/404/SVG responses
and a two-move Edge walkthrough passed. No paid calls or real feedback test ran.
Styles/icons use public Bootstrap and Font Awesome CDNs. Use trusted local exports;
production authentication, filename boundaries and full accessibility are unverified.
The original project code/documentation use GPL-3.0-or-later; see the
[license](../LICENSE) and [third-party notices](third-party-notices.md).
