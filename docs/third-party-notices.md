# Third-party notices

The project's GPL-3.0-or-later grant does not replace third-party copyright
notices or license terms. Dependencies are installed separately from
`requirements.txt`; their distributions include their own license files.

## Chess engine library and board artwork

- **python-chess / chess**, by Niklas Fiekas and contributors, is licensed under
  [GPL version 3 or later](https://github.com/niklasf/python-chess#license).
- The SVG board exports in `board_images/` and `games/` and the viewer screenshot
  include chess-piece artwork by **Colin M. L. Burnett (Cburnett)**, supplied through
  `chess.svg`. Copyright remains with the original artist.
- The [python-chess SVG documentation](https://python-chess.readthedocs.io/en/latest/svg.html)
  identifies the artwork and its GFDL/BSD/GPL alternatives. The original
  [Wikimedia pawn artwork page](https://commons.wikimedia.org/wiki/File:Chess_plt45.svg)
  records the GPL version 2-or-later option; this distribution uses the GPLv3
  option, with the full GPLv3 text in [LICENSE](../LICENSE).
- Board compositions are generated from game positions; the piece shapes are
  not claimed as original artwork by this project's author. The published SVGs
  retain editable vector paths.

## Python dependencies

| Package | License | Upstream terms |
|---|---|---|
| OpenAI Python SDK | Apache-2.0 | [License](https://github.com/openai/openai-python/blob/main/LICENSE) |
| python-dotenv | BSD-3-Clause | [License](https://github.com/theskumar/python-dotenv/blob/v1.0.0/LICENSE) |
| Flask | BSD-3-Clause | [License](https://github.com/pallets/flask/blob/3.1.0/LICENSE.txt) |

These are the direct dependencies; their separately installed transitive
dependencies retain the licenses shipped in those distributions. Access to the
OpenAI service is governed separately by its service terms; this source-code
license does not grant API access or credits.

## Viewer styles and icons

The viewer loads these resources from external CDNs; their files are not vendored:

- **Bootstrap 5.1.3**, by the Bootstrap authors: [MIT license](https://getbootstrap.com/docs/5.1/about/license/).
- **Font Awesome Free 6.0.0**, by Fonticons, Inc.: icons under CC BY 4.0, fonts
  under SIL OFL 1.1, and code under MIT. See the
  [versioned license/attribution notice](https://github.com/FortAwesome/Font-Awesome/blob/6.0.0/LICENSE.txt).

Keep upstream attribution and license notices when redistributing those resources.
