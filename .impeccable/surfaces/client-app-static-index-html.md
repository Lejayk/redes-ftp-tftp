---
version: 1
slug: "client-app-static-index-html"
primary_target: "client/app/static/index.html"
related_targets: ["client/app/static/styles.css","client/app/static/app.js"]
---

# Live panel: FTP and TFTP on the wire

Scope: the single-page live panel served at `/` (client/app/static). Visitor mode: Operate. The presenter drives it; the class reads it on a projector.

Audience and job: Grupo 1 presenting the Networks assignment; the professor and classmates must understand FTP and TFTP from real captured packets. Constraints: offline at showtime, no build step, Spanish interface copy, legible from the back row.

## Direction contract

THESIS: The panel is the classroom chalkboard: every captured packet is chalked onto the board as it crosses the wire, so the class reads the protocol the way a teacher would draw it. It refuses the dark Wireshark-terminal dashboard and the white SaaS dashboard.

OWN-WORLD: Deep chalkboard green drenches the board; side panels sit in a darker green-black. Chalk white carries text and TCP plumbing, chalk sky the commands and requests, chalk yellow the data, chalk pink the failures, chalk orange the retransmissions; colour lives only in protocol data. Teacher's handwriting (Klee One) for board notes, monospace for wire data, system sans for controls. The light variant is a whiteboard with black, blue, green, and red markers. (15/11/2026: the vertical Japanese duty corner was removed at the user's request.)

STORY: The class watches a conversation get chalked line by line: FTP's two channels and its password in plain text, TFTP's TID and its stop-and-wait. The presenter paces it with the arrow key.

FIRST VIEWPORT: Standard shell. Top bar with the protocol tabs and pacing controls; left column with the client controls (Demo completa as the primary action) and the client log; centre board with three lifelines (client, known port, transfer port); right packet inspector; a ledge under the board with the statistics.

FORM: Chalkboard of an anime classroom, position 4 of 7 on the ordered list; seed:d1b1bbe91224d7b4. Signature move: each packet is drawn as a chalk stroke from sender to receiver, and Limpiar sweeps the board with an eraser. Raises: (split-flap board) fixed columns and tabular figures never move; (labanotation) a retransmission's silence is drawn as its own measured gap; (lexicon plate) colour is quarantined to protocol data; (gate board) errors and retransmissions keep their chalk underline until erased.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
