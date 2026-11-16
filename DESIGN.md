---
name: FTP y TFTP a corazón abierto
description: A live FTP and TFTP packet lab drawn as an anime-classroom chalkboard, with a whiteboard variant for projectors that wash out the green.
colors:
  wall: "#0d1813"
  panel: "#13221b"
  panel-2: "#192c23"
  raised: "#20372c"
  ledge: "#26352e"
  board: "#21493a"
  line: "rgba(241, 239, 228, 0.12)"
  line-strong: "rgba(241, 239, 228, 0.24)"
  lane: "rgba(241, 239, 228, 0.2)"
  hover: "rgba(241, 239, 228, 0.05)"
  chalk: "#f1efe4"
  chalk-muted: "#d3e2d6"
  chalk-faint: "#a9c2b1"
  chalk-sky: "#9ed8ff"
  chalk-yellow: "#ffe48a"
  chalk-pink: "#ffa3b8"
  chalk-orange: "#ffb877"
  primary-ink: "#173327"
  l-eth: "#c0cbc3"
  l-ip: "#cdb8ff"
  l-tcp: "#9be39b"
  l-udp: "#9be39b"
  l-app: "#f0a8f0"
  wb-wall: "#a9b2ae"
  wb-panel: "#d6dcd9"
  wb-panel-2: "#c8d0cc"
  wb-raised: "#e3e8e5"
  wb-ledge: "#c4ccc8"
  wb-board: "#fdfdfb"
  wb-line: "rgba(28, 35, 40, 0.12)"
  wb-line-strong: "rgba(28, 35, 40, 0.24)"
  wb-lane: "rgba(28, 35, 40, 0.22)"
  wb-hover: "rgba(28, 35, 40, 0.04)"
  wb-chalk: "#1c2328"
  wb-chalk-muted: "#3a454d"
  wb-chalk-faint: "#44505a"
  wb-chalk-sky: "#1d4fc4"
  wb-chalk-yellow: "#0f7a50"
  wb-chalk-pink: "#c4262e"
  wb-chalk-orange: "#b85410"
  wb-primary-ink: "#ffffff"
  wb-l-eth: "#3d4850"
  wb-l-ip: "#5b21b6"
  wb-l-tcp: "#524e08"
  wb-l-udp: "#524e08"
  wb-l-app: "#86198f"
typography:
  display:
    fontFamily: "Klee One, Segoe UI, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 600
    lineHeight: 1.15
  lesson:
    fontFamily: "Klee One, Segoe UI, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.3
  lane-head:
    fontFamily: "Klee One, Segoe UI, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.2
  wire-note:
    fontFamily: "Klee One, Segoe UI, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.45
  hand-note:
    fontFamily: "Klee One, Segoe UI, system-ui, sans-serif"
    fontSize: "15.5px"
    fontWeight: 400
    lineHeight: 1.45
  wire-label:
    fontFamily: "Cascadia Code, Cascadia Mono, JetBrains Mono, Consolas, ui-monospace, monospace"
    fontSize: "16.5px"
    fontWeight: 650
  wire-meta:
    fontFamily: "Cascadia Code, Cascadia Mono, JetBrains Mono, Consolas, ui-monospace, monospace"
    fontSize: "12.5px"
    fontWeight: 400
  figure:
    fontFamily: "Cascadia Code, Cascadia Mono, JetBrains Mono, Consolas, ui-monospace, monospace"
    fontSize: "17px"
    fontWeight: 650
  caption-mono:
    fontFamily: "Cascadia Code, Cascadia Mono, JetBrains Mono, Consolas, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 500
  title:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "17px"
    fontWeight: 700
  body:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "14.5px"
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "tnum"
  inspector:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "14px"
    fontWeight: 400
  control:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "13.5px"
    fontWeight: 600
  caption:
    fontFamily: "Segoe UI Variable Text, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "12px"
    fontWeight: 400
rounded:
  xs: "3px"
  tag: "6px"
  sm: "8px"
  button: "9px"
  segment: "10px"
  md: "12px"
  pill: "999px"
spacing:
  sp-1: "4px"
  sp-2: "8px"
  sp-3: "12px"
  sp-4: "16px"
  sp-5: "24px"
  gutter: "78px"
components:
  button:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.chalk}"
    typography: "{typography.control}"
    rounded: "{rounded.button}"
    padding: "7px 12px"
  button-primary:
    backgroundColor: "{colors.chalk}"
    textColor: "{colors.primary-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.button}"
    padding: "7px 12px"
  button-primary-whiteboard:
    backgroundColor: "{colors.wb-chalk}"
    textColor: "{colors.wb-primary-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.button}"
    padding: "7px 12px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.chalk}"
    typography: "{typography.control}"
    rounded: "{rounded.button}"
    padding: "7px 12px"
  button-icon:
    backgroundColor: "transparent"
    textColor: "{colors.chalk}"
    rounded: "{rounded.button}"
    width: "34px"
  button-small:
    typography: "{typography.caption}"
    rounded: "{rounded.button}"
    padding: "4px 10px"
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.chalk-muted}"
    typography: "{typography.title}"
    rounded: "{rounded.sm}"
    padding: "7px 16px"
  tab-active:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.chalk}"
    typography: "{typography.title}"
    rounded: "{rounded.sm}"
    padding: "7px 16px"
  segment-on:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.chalk}"
    typography: "{typography.control}"
    rounded: "7px"
    padding: "5px 12px"
  input:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.sm}"
    padding: "6px 9px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.chalk}"
    typography: "{typography.caption-mono}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  pill-status:
    backgroundColor: "transparent"
    textColor: "{colors.chalk-faint}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "3px 9px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.md}"
    padding: "16px"
  board:
    backgroundColor: "{colors.board}"
    textColor: "{colors.chalk}"
  ledge:
    backgroundColor: "{colors.ledge}"
    textColor: "{colors.chalk}"
    padding: "10px 16px"
  lesson-title:
    textColor: "{colors.chalk}"
    typography: "{typography.lesson}"
  teacher-note:
    textColor: "{colors.chalk-muted}"
    typography: "{typography.wire-note}"
  packet-label:
    typography: "{typography.wire-label}"
  inspector-note:
    backgroundColor: "{colors.board}"
    textColor: "{colors.chalk}"
    typography: "{typography.hand-note}"
    rounded: "{rounded.sm}"
    padding: "10px 12px"
  badge:
    backgroundColor: "transparent"
    textColor: "{colors.chalk-sky}"
    typography: "{typography.caption-mono}"
    rounded: "{rounded.tag}"
    padding: "1px 7px"
  hexgrid:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.chalk}"
    typography: "{typography.wire-meta}"
    rounded: "{rounded.sm}"
    padding: "8px"
  toast:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.chalk}"
    typography: "{typography.body}"
    rounded: "{rounded.segment}"
    padding: "11px 16px"
---

# Design System: FTP y TFTP a corazón abierto

## Overview

**Creative North Star: "The Classroom Chalkboard"**

The panel is the chalkboard of an anime classroom: a deep green board, framed by a darker green-black wall and side panels, on which every captured packet is chalked from sender to receiver as it crosses the wire. The class reads the protocol the way a teacher draws it: three lifelines, a lesson title underlined in chalk, one stroke per packet and a handwritten note beneath it. The system refuses both the dark Wireshark-style terminal dashboard and the white SaaS dashboard.

Density is split by audience. The board is set at projector scale for the back row; the side columns and the toolbar are set at laptop scale for the presenter who drives them. Colour is quarantined to protocol data, so a sky stroke always means a command and an orange one always means a retransmission, while the chrome stays in chalk white, worn chalk and board greens. Everything that looks drawn was drawn: the chalk stroke, dash, arrowhead, touch-down dot, circle, eraser and board haze are authored SVGs, never generated noise.

A whiteboard variant serves projectors that wash the green out. It keeps every role and every gesture, swaps chalk for flat marker lines, and keeps the board as the only bright plane in the room.

**Key Characteristics:**
- A deep green board is the lit stage; the wall and side panels sit darker so the eye lands on the board.
- Hue lives only in protocol data; chrome is chalk white, worn chalk and board greens.
- Three hands: teacher's handwriting for notes and titles, monospace for anything that crossed the wire, system sans for controls.
- Every chalk mark is an authored SVG used as a mask over the role colour; no procedural texture.
- Motion is two gestures: a packet is chalked from sender to receiver, and Limpiar sweeps an eraser across the board.
- Two variants, chalkboard and whiteboard, share one set of roles through `:root` and `:root[data-theme="light"]`.

## Colors

A board-green room lit by six chalks, where every hue on screen is a word in the protocol.

### Primary
- **Chalkboard Green** (`board`, #21493a): the board itself, behind the timeline, the sticky lane heads and the inspector's explanation card. It carries the drawn board haze (`img/board-haze.svg`, the eraser ghost every used board keeps).
- **Chalk White** (`chalk`, #f1efe4): all primary text, TCP handshake and close strokes, TFTP ACK strokes, the primary button fill, focus rings, the active-tab underline and the step bar's top rule.
- **Board-Green Ink** (`primary-ink`, #173327): text and icons on the chalk-white primary button.

### Secondary
The protocol chalks. Each one is a fixed role, set on a packet row as `--c` and read by its stroke, label, selection tint, legend swatch and inspector badge.
- **Chalk Sky** (`chalk-sky`, #9ed8ff): FTP commands and replies on the control channel, TFTP RRQ/WRQ requests, and the known-port lifeline dot.
- **Chalk Yellow** (`chalk-yellow`, #ffe48a): data, on the FTP data channel and in TFTP DATA blocks, and the transfer-port lifeline dot.
- **Chalk Pink** (`chalk-pink`, #ffa3b8): what failed or was exposed: TFTP ERROR, TCP RST, the circle around a plaintext password and its marked inspector field and bytes. It is also the one hue chrome may borrow, for the error log dot, a failed operation's end mark and the toast border, because there it means the same thing.
- **Chalk Orange** (`chalk-orange`, #ffb877): retransmissions, and the handwritten label of the silence that preceded one.
- **Faint Chalk** (`chalk-faint`, #a9c2b1): TCP ACKs, drawn smaller and slightly transparent as useful noise. It doubles as the faint text tint.

### Tertiary
The spare chalks, used only for the inspector's protocol layers (swatches, field highlights and hex bytes).
- **Slate Chalk** (`l-eth`, #c0cbc3): Ethernet.
- **Violet Chalk** (`l-ip`, #cdb8ff): IP.
- **Leaf Chalk** (`l-tcp` and `l-udp`, #9be39b): the transport layer. TCP and UDP share one hue because a packet never carries both.
- **Lilac Chalk** (`l-app`, #f0a8f0): the application layer.

### Neutral
- **Classroom Wall** (`wall`, #0d1813): the page background behind the panels.
- **Dark Frame** (`panel`, #13221b): side panels, the inspector, the board's frame column and the top bar.
- **Recessed Frame** (`panel-2`, #192c23): wells for tabs and the mode switch, inputs, selects and the hex dump.
- **Raised Frame** (`raised`, #20372c): buttons, the active tab, the active segment and the toast.
- **Chalk Ledge** (`ledge`, #26352e): the statistics strip under the board, where the chalk would rest.
- **Worn Chalk** (`chalk-muted`, #d3e2d6): secondary text, the teacher's notes, inactive tabs and the client lane dot.
- **Chalk Lines** (`line`, `line-strong`, `lane`, `hover`): chalk white at 12%, 24%, 20% and 5% alpha, for dividers, control borders, dashed lifelines and row hover.

### Whiteboard Variant
Set on `:root[data-theme="light"]`; the same custom-property names take marker values.
- **Whiteboard** (`wb-board`, #fdfdfb): the only bright plane. It carries a drawn marker ghost (`img/whiteboard-ghost.svg`) at 5% opacity.
- **Grey Room** (`wb-wall` #a9b2ae, `wb-panel` #d6dcd9, `wb-panel-2` #c8d0cc, `wb-raised` #e3e8e5, `wb-ledge` #c4ccc8): wall and panels stay clearly darker than the board.
- **Markers**: black (`wb-chalk`, #1c2328) for text and TCP plumbing, blue (`wb-chalk-sky`, #1d4fc4) for commands and requests, green (`wb-chalk-yellow`, #0f7a50) for data, grey (`wb-chalk-faint`, #44505a) for ACKs and faint text, red (`wb-chalk-pink`, #c4262e) for failures and exposures, orange (`wb-chalk-orange`, #b85410) for retransmissions. The direction named four markers; the build added orange so the retransmission role survives the switch.
- **Spare markers** for inspector layers: grey (`wb-l-eth`, #3d4850), violet (`wb-l-ip`, #5b21b6), olive (`wb-l-tcp`/`wb-l-udp`, #524e08), magenta (`wb-l-app`, #86198f), each at 4.5:1 on its cell.
- **Primary** on the whiteboard is marker black with white ink (`wb-primary-ink`, #ffffff).

### Named Rules
**The Colour Quarantine Rule.** Hue belongs to protocol data. Buttons, pills, tabs, focus rings, log dots and panel chrome use only chalk white, worn chalk and the board greens. Chalk pink is the single exception, and only where chrome reports a failure.

**The Fixed Roles Rule.** A role keeps its colour everywhere it appears: sky for commands and requests, yellow for data, white for TCP handshake and close, faint for ACK, pink for failures, orange for retransmission. The whiteboard maps them one to one onto blue, green, black, grey, red and orange markers.

**The Spare Chalk Rule.** Inspector layer hues come from the chalks the board never uses, so a byte's layer can never be mistaken for a packet's role.

**The Tinted Wear Rule.** Worn chalk on the chalkboard is tinted with the board green, never a neutral grey. Every secondary text tint holds 4.5:1 on its own ground in both variants.

## Typography

**Display Font:** Klee One, self-hosted (400 and 600, OFL, `fonts/klee-one-*.woff2`, 600 preloaded), with Segoe UI and system-ui as fallback
**Body Font:** Segoe UI Variable Text (with Segoe UI, system-ui, -apple-system)
**Label/Mono Font:** Cascadia Code (with Cascadia Mono, JetBrains Mono, Consolas, ui-monospace)

**Character:** A teacher's careful handwriting next to a terminal's exact monospace: the hand explains, the mono quotes the wire, and a quiet system sans stays out of the way on the controls.

### Hierarchy
- **Lesson** (600, 24px, 1.3): the title of each operation written on the board, underlined in chalk. The largest type on screen, because the back row reads it first.
- **Display** (600, 21px, 1.15; 19px below 1500px): the product title in the top bar, its second half in worn chalk.
- **Lane Head** (600, 17px, 1.2): the names of the three lifelines.
- **Wire Note** (400, 17px, 1.45): the teacher's notes under each packet and the measured-silence label.
- **Wire Label** (mono 650, 16.5px): the packet itself on its arrow (`SYN`, `PASS redes2026`, `DATA #2`), in the role colour.
- **Hand Note** (400, 15.5px, 1.45): the inspector's explanation card and empty state. The board's own empty state is handwriting at 17px.
- **Title** (sans 700, 17px): panel headings and protocol tabs.
- **Figure** (mono 650, 17px): statistics on the ledge and the inspector packet title.
- **Body** (sans 400, 14.5px, 1.45): base text; the inspector's fields run at 14px.
- **Control** (sans 600, 13.5px): buttons; selects, hints and the client log use the same size at 400.
- **Wire Meta** (mono 400, 12.5px): timestamps in the gutter, the TCP detail line under each arrow, operation end marks (600) and the hex dump (line-height 1.6). The legend uses the same size in sans.
- **Caption** (12px): sans 400 for stat labels and role captions, 600 for pills; mono for chips and tab ports (500), command mnemonics (600) and badges (700).

### Named Rules
**The Three Hands Rule.** Klee One is the teacher writing on the board; monospace is anything that crossed the wire (labels, addresses, timestamps, hex, figures, file names, input values); system sans is the controls. A wire value is never set in Klee One, and a control is never set in it either.

**The Two Scales Rule.** Controls use the laptop scale (`--fs-caption` 12px to `--fs-display` 21px); the board uses the projector scale (`--fs-wire-meta`, `--fs-wire-label`, `--fs-wire-note`, `--fs-lesson`). Anything the class must read lives on the projector scale.

**The Still Figures Rule.** The whole page runs `font-variant-numeric: tabular-nums`, and fixed columns hold times, sizes and statistics, so no figure moves sideways as its value changes.

## Layout

The shell is a full-height grid: a top bar, then a three-column workspace (`clamp(250px, 19vw, 318px)` controls, a flexible board, `clamp(320px, 25vw, 400px)` inspector) with 12px gaps and padding. Above 1180px the page itself never scrolls; each column scrolls inside its panel. Spacing runs on a 4px base (4, 8, 12, 16, 24).

The top bar holds the brand, the protocol tabs and a right-aligned toolbar (mode switch, speed, Cancelar, Limpiar, theme toggle, live status). At 1500px and below it compresses to stay on one row: the subtitle and the speed label hide, the title drops to 19px and tabs tighten.

The centre column stacks the legend bar, the board, the step-mode bar and the statistics ledge. On the board, a 78px gutter holds timestamps; three lifelines stand at 11%, 54% and 90% of the lane width (client, known port, transfer port) under sticky 72px lane heads with a dashed underline. A packet row is 68px tall (ACKs 38px): label above the stroke, stroke at 28px, detail line below, note after. Notes indent to the client lifeline.

At 1180px and below the page scrolls: controls and board share two columns (280px and the rest, board row at `100vh - 96px`) and the inspector drops to a full-width row beneath; the top bar may wrap. At 860px and below everything stacks in one column, the board takes 80vh, the key hint disappears, and lane heads wrap and drop their addresses.

**The Measured Silence Rule.** A retransmission's wait is drawn as its own gap row, 28px plus 16px per second of silence (capped at 6 s), labelled in orange handwriting. On this board, time is distance.

## Elevation & Depth

Depth is tonal, not shadowed. On the chalkboard the wall is darkest, the panels step up through `panel`, `panel-2`, `raised` and `ledge`, and the board green is the lit plane the eye lands on. On the whiteboard the order inverts but the principle holds: the white board is the only bright plane, and wall and panels sit clearly darker around it. State and selection are drawn with rings and tints, never lift.

### Shadow Vocabulary
- **Board edge** (`box-shadow: inset 0 0 0 1px var(--line)`): the hairline frame of the board.
- **Brand-mark frame** (`box-shadow: inset 0 0 0 2px var(--ledge)`): the frame of the miniature board in the top bar.
- **Active segment ring** (`box-shadow: 0 0 0 1px var(--line-strong)`): the selected mode in the switch.
- **Focus halo** (`box-shadow: 0 0 0 3px color-mix(in srgb, var(--focus) 22%, transparent)`): a focused input or select, beside its chalk border.
- **Selected packet** (`box-shadow: inset 0 0 0 1.5px color-mix(in srgb, var(--c) 45%, transparent)`): with a 10% role-colour wash on the row.
- **Marked field** (`box-shadow: inset 0 0 0 1.5px var(--chalk-pink)`): the plaintext password in the inspector.
- **Toast** (`box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35)`): the only floating panel.
- **Eraser** (`filter: drop-shadow(0 8px 10px rgba(0, 0, 0, 0.35))`): the physical eraser crossing the board.

### Named Rules
**The Lit Board Rule.** The board is always the brightest-reading plane in its variant. A new surface steps in tone, never in shadow.

**The Physical Object Rule.** Only things that physically float above the board cast a shadow: the eraser and the toast. Panels, cards and buttons stay flat.

## Shapes

The room is softly rounded and the chalk is drawn. Panels and the tab well take 12px corners, the mode switch and the toast 10px, buttons 9px, inputs, tabs, rows and the hex dump 8px, badges and inspector fields 6px, hex bytes 3px, and pills and chips are fully round. Lifelines are 1.5px dashes; the lane-head rule is a 1px dash.

Chalk marks are never CSS borders or gradients. They are eight authored drawings: five masks over the role colour (the 160px stroke tile and dash tile, repeated horizontally; the double-pass chevron head; the irregular touch-down dot; the open hand-drawn circle) and three images (the eraser, the board haze, the whiteboard ghost). On the whiteboard the stroke mask switches off and a marker line becomes a flat 4px bar with 3px rounded ends (2px for ACKs, 2.5px for underlines).

**The Hand-Drawn Mark Rule.** A new mark reuses an authored mask with `background: var(--c)`: the colour comes from the role, the shape from the drawing. No procedural noise, no SVG turbulence and no gradient grain.

## Components

### Buttons
Quiet frames until the presenter needs them; one chalk-white action per panel.
- **Shape:** gently rounded (9px), 1px `line-strong` border.
- **Default:** `raised` fill, chalk text, control type, 7px 12px padding, 8px gap to a 16px stroke icon. A command mnemonic (`LIST`, `RETR`, `STOR`) rides inside in caption mono, worn chalk.
- **Primary:** chalk-white fill with board-green ink (marker black with white ink on the whiteboard). Used for Demo completa, Descargar RRQ and Siguiente.
- **Hover / Focus / Active:** the border brightens to full chalk; a press drops the button 1px; focus is a 2px chalk outline at 2px offset. Disabled sits at 40% opacity.
- **Ghost:** transparent fill (Cancelar, Limpiar, theme toggle, En vivo); its `on` state is a chalk border. Icon-only ghosts are 34px wide; small buttons use 4px 10px and caption type.

### Navigation
- **Protocol tabs:** a recessed well (`panel-2`, 1px line, 12px corners, 4px inset) holding FTP and TFTP in title type with a mono port caption (`TCP · 21`). Inactive tabs are worn chalk; the active tab takes the raised fill and a 7px chalk-stroke underline inset 16px, the teacher underlining today's topic. On the whiteboard the underline is a 2.5px marker line.
- **Mode switch:** the same well at 10px corners; the active segment takes the raised fill and a 1px `line-strong` ring.

### Inputs / Fields
- **Style:** `panel-2` fill, 1px line border, 8px corners, 6px 9px padding. Text inputs are monospace, because their values go onto the wire; the caret is chalk.
- **Focus:** the border turns chalk and a 3px chalk halo at 22% appears; hover raises the border to `line-strong`.
- **Disabled:** 55% opacity. Checkboxes use the faint chalk as accent colour.

### Chips
- **Style:** file chips in TFTP's controls: transparent, `line-strong` border, fully round, caption mono, with the file size in faint chalk.
- **State:** hover brightens the border to chalk. Chips are actions, with no selected state.

### Status Pills
- **Style:** fully round, 1px border in `currentColor`, caption at 600. Off is faint chalk, neutral is worn chalk, on is full chalk. Pills never take a protocol hue.

### Panels and the Ledge
- **Panel:** `panel` fill, 1px line, 12px corners, 16px padding, title-type heading. Numbered client steps sit beside 24px handwritten numerals in a 1px `line-strong` circle.
- **Ledge:** the statistics strip under the board: `ledge` fill, a `line-strong` top rule, bottom corners matching the panel. Each statistic is a faint caption over a mono figure, separated by 1px lines; the last operation's name is in handwriting, and the FTP vs TFTP comparison sits right-aligned behind its own rule.

### Client Log
- 13.5px worn-chalk lines with a 7px chalk dot marking tone: faint for information, chalk for success, worn chalk for a warning, pink for an error (whose line rises to full chalk). A mono tag names the protocol.

### Chalked Packet Row (signature)
The packet as the teacher draws it.
- **Structure:** a 78px time gutter and a lane area; the row's kind class sets `--c` to its role. The stroke is the chalk tile masked over `--c`, with the touch-down dot at the sender and the chevron head at the receiver. The label sits above in wire-label mono and the role colour, the TCP detail line below in faint wire meta, the note beneath in Klee One.
- **ACKs:** a 38px row, a thinner stroke at 85% opacity, a 12.5px label, no detail line and no note; a toggle hides them.
- **Failures:** ERROR and retransmission strokes switch to the dash tile, and ERROR, retransmission and RST labels keep a 2px underline in their role colour until the board is erased.
- **Plaintext password:** the teacher circles it with the pink chalk circle, and the inspector marks the same field and bytes in pink.
- **States:** hover is a 5% chalk wash; selected is a 10% role wash with a 1.5px role ring at 45%. Each row is a keyboard button (Enter or Space opens the inspector).
- **Motion:** a live packet on the visible tab is chalked in 0.42s: a clip-path grows from the sender's edge to the receiver's on `cubic-bezier(0.16, 1, 0.3, 1)`, padded 14px so the head and dot are included. Label, detail and note fade in over 0.3s after 0.24s. The draw class is removed by a 700ms timer, not `animationend`, so a hidden tab never replays a backlog. Packets are paced 90, 280 or 620ms apart (Rápida, Normal, Lenta), or one at a time with the right arrow in step mode.

### Lesson Title and Operation End
- **Lesson title:** each operation opens with its name in lesson type, underlined by an 8px worn-chalk stroke (a 2.5px marker line on the whiteboard).
- **Operation end:** a mono 12.5px line with a check or cross icon: chalk on success, pink on failure.

### Lane Heads and Legend
- **Lane heads:** sticky, board-filled, with a dashed underline. Each shows a handwritten name, a mono address and a faint role caption over a 9px ring dot in the lane's colour (client worn chalk, known port sky, transfer port yellow).
- **Legend:** 26px by 9px swatches cut from the same stroke tile (the dash tile for failures), with worn-chalk labels at 12.5px.

### Eraser
- **Drawing:** a 60px by 150px authored eraser seen from above, maroon back and grey felt on the leading edge, with the eraser drop shadow.
- **Motion:** Limpiar sweeps it from off the left edge to the board's right edge in 0.62s on `cubic-bezier(0.65, 0, 0.35, 1)`. The timeline content clips away from the left on the same duration and easing, so the chalk disappears exactly under the felt while the lifelines stay. The board resets after 650ms.

### Step-Mode Bar
- A strip above the ledge with a 1.5px chalk top rule and an 8% chalk wash over the panel: pause icon, a faint caption over the next step's name in handwriting, the key hint and a primary Siguiente. It slides up 6px in 0.2s using transform only, so a paused animation still looks active.

### Packet Inspector
- **Header:** a role-coloured badge (1px border and text in `--c`, 6px corners, caption mono 700) beside the packet in figure mono; a faint mono route line below.
- **Explanation card:** a board-coloured card with hand-note type, the teacher's note carried into the inspector.
- **Layers:** flat sections separated by 1px lines, each opened by a 9px swatch in its layer hue. Fields run on a 42/58 grid: worn-chalk sans names, mono values. Hover or a linked byte highlights the field with a 16% layer wash.
- **Hex dump:** `panel-2`, 8px corners, wire-meta mono at 1.6 line height, 8 bytes per line in a narrow inspector and 16 once it is wider than 520px (the stacked layout), so the ASCII column never scrolls away. Bytes are coloured by layer; the highlighted byte fills with its layer colour; marked bytes take a 30% pink wash.

### Toast
- `raised` fill, a 1.5px pink border (toasts only report failures), 10px corners, body type and the toast shadow, sliding up 6px on entry.

### Brand Mark
- A 40px miniature board (6px corners, 2px ledge frame) with two chalk strokes: a sky question and a yellow answer, the smallest possible protocol exchange. On the whiteboard they become 2.5px marker bars.

### Icons
- One stroke family: 24 by 24 inline SVG symbols, stroke 2, round caps and joins, rendered at 16px in `currentColor`.

## Do's and Don'ts

### Do:
- **Do** give every new protocol element a role from the fixed set and set `--c` on it; the stroke, label, selection wash, legend swatch and badge all read from `--c`.
- **Do** draw new chalk marks with the authored masks (`--stroke`, `--stroke-dash`, `--stroke-head`, `--stroke-dot`, the chalk circle) and give them a flat marker-bar fallback under `:root[data-theme="light"]`.
- **Do** define every new colour in both `:root` and `:root[data-theme="light"]`, and hold secondary text at 4.5:1 on its own ground in both.
- **Do** set anything the class must read on the projector scale (`--fs-wire-*`, `--fs-lesson`), and keep laptop-scale type for the presenter's controls.
- **Do** keep failures dashed and underlined in their role colour until Limpiar erases the board.
- **Do** honour `prefers-reduced-motion`: the chalk draw, the eraser and every transition switch off, and Limpiar clears instantly.

### Don't:
- **Don't** put a protocol hue on chrome: no coloured buttons, tabs, pills or focus rings. Pink is the only borrowed hue, and only to report a failure.
- **Don't** reuse a protocol hue for an inspector layer, or a layer hue on the board.
- **Don't** tint worn chalk on the chalkboard with a neutral grey; wear takes the board green.
- **Don't** fake chalk with procedural noise, SVG turbulence or gradient grain; the strokes, haze and ghost are drawn.
- **Don't** give panels, cards or buttons a drop shadow; only the eraser and the toast cast one.
- **Don't** let a figure column change width as its value changes; times, sizes and statistics stay tabular.
- **Don't** drift toward the dark Wireshark-style terminal dashboard or the white SaaS dashboard.
