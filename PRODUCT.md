# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Presenters:** Grupo 1 of the Networks course (Eliab Parra, Sebastian Alsleben, Santiago Landaeta, Leandro Jay), computer engineering students at URU. One of them drives the panel during the talk.
- **Audience:** the professor and classmates, watching the panel on a classroom projector. They never touch it; they read it from their seats.

## Product Purpose

A live lab that shows how FTP and TFTP work from the inside, packet by packet and byte by byte. Success means the class leaves understanding TCP versus UDP, FTP's two channels versus TFTP's TID, the password travelling in plain text, and TFTP's stop-and-wait with retransmission, and the group meets the assignment (client and server in Docker, code that shows the protocol step by step).

## Positioning

Nothing on screen is a canned animation: every arrow is a real frame captured off the client's network card, exchanged between real servers (pyftpdlib, tftpd-hpa) and clients the group wrote by hand over raw sockets.

## Operating Context

- Runs on Leandro's laptop: Windows, Debian in WSL2, Docker Compose. Started with `iniciar.bat`, served at http://localhost:8080.
- Shown on a projector in a lit classroom; internet is not guaranteed.
- The presenter paces it with step-by-step mode, advancing with the right arrow key or a slide clicker.
- Presentation date: 16/11/2026.

## Capabilities and Constraints

- FTP: connect, login (including a wrong password for the 530), LIST, RETR, STOR, free-form commands, QUIT, and a one-click full demo.
- TFTP: RRQ, WRQ, error on a missing file, the empty final block of a 1024-byte file, and a simulated lost ACK that triggers a real server retransmission.
- Sequence diagram per protocol, packet inspector with layers and a hex dump, client log, and per-operation statistics with an FTP vs TFTP comparison.
- Stack is fixed: FastAPI backend, plain HTML/CSS/JS with no build step and no CDN, so it works offline.
- Interface copy is in Spanish (neutral register).

## Brand Commitments

Visual request from the user, binding, in their words: "minimalista, insano, onichan, sin gallos y sin AI slop" (minimal, outrageous, anime-flavored, no glitches, no AI slop).

## Evidence on Hand

- Real captures: the full FTP demo moves a 1300-byte file in 56 packets and 5.7 KB on the wire; the same file over TFTP takes 7 packets and 1.6 KB.
- Sample files in `ftp-server/files` and `tftp-server/files` (`config-router.txt`, `justo-1024.txt`, `bienvenida.txt`).
- No logos, mascots, or illustrations exist; any artwork would have to be authored.

## Product Principles

- The wire is the truth: show what was captured, never decorate it with things that did not happen.
- Readable from the back row: projector first, laptop second.
- The presenter sets the pace; the screen never runs ahead of the explanation.
- Zero network dependencies at showtime.

## Accessibility & Inclusion

Legible on a projector from the back of the classroom (high contrast, large text) and fully operable from the keyboard or a slide clicker.
