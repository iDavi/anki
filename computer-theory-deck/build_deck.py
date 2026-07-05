#!/usr/bin/env python3
"""Build 'Computer Theory (Theory of Computation)' Anki deck as an .apkg file.

Usage:  pip install genanki && python3 build_deck.py [output.apkg]

Produces a deck with subdecks ordered as a course: study 00 -> 05 in order.
Card fields: Question / Answer / Example-intuition / Portuguese key term.
"""

import sys

import genanki

from cards import complexity, context_free, decidability, foundations, regular, turing

MODEL_ID = 1607392319001
DECK_ID_BASE = 2059400110000

CSS = """
.card {
  font-family: -apple-system, "Segoe UI", Roboto, "Noto Sans", sans-serif;
  font-size: 19px;
  line-height: 1.45;
  color: #1a1a2e;
  background-color: #fbfbf8;
  text-align: left;
  padding: 22px;
  max-width: 620px;
  margin: 0 auto;
}
.night_mode .card { color: #e8e8e8; background-color: #23252e; }
.question { font-size: 21px; font-weight: 600; }
.answer { margin-top: 10px; }
.extra {
  margin-top: 16px; padding: 10px 14px; border-left: 4px solid #7aa2f7;
  background: rgba(122,162,247,.08); font-size: 16.5px; border-radius: 0 8px 8px 0;
}
.extra::before { content: "💡 "; }
.pt {
  margin-top: 12px; font-size: 15px; color: #6b7280; font-style: italic;
}
.pt::before { content: "🇧🇷 "; font-style: normal; }
.section { font-size: 13px; letter-spacing: .12em; text-transform: uppercase;
  color: #9ca3af; margin-bottom: 10px; }
hr#divider { border: none; border-top: 2px solid #d8d8d0; margin: 14px 0; }
b { color: #b4462d; }
.night_mode b { color: #ff9e64; }
sub, sup { font-size: 70%; }
"""

MODEL = genanki.Model(
    MODEL_ID,
    "Computer Theory Q&A",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Extra"},
        {"name": "PT"},
        {"name": "Section"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="section">{{Section}}</div>'
            '<div class="question">{{Question}}</div>',
            "afmt": '<div class="section">{{Section}}</div>'
            '<div class="question">{{Question}}</div>'
            '<hr id="divider">'
            '<div class="answer">{{Answer}}</div>'
            '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}'
            '{{#PT}}<div class="pt">{{PT}}</div>{{/PT}}',
        },
    ],
    css=CSS,
)

SECTIONS = [
    ("00 Foundations (start here)", "Foundations", foundations.CARDS),
    ("01 Regular Languages & Finite Automata", "Regular Languages", regular.CARDS),
    ("02 Context-Free Languages & PDAs", "Context-Free Languages", context_free.CARDS),
    ("03 Turing Machines & Church-Turing", "Turing Machines", turing.CARDS),
    ("04 Decidability & Reductions", "Decidability", decidability.CARDS),
    ("05 Complexity: P, NP & Beyond", "Complexity", complexity.CARDS),
]


def build(out_path: str) -> None:
    decks = []
    total = 0
    for i, (subdeck_name, section_label, cards) in enumerate(SECTIONS):
        deck = genanki.Deck(
            DECK_ID_BASE + i,
            f"Computer Theory::{subdeck_name}",
        )
        for card in cards:
            note = genanki.Note(
                model=MODEL,
                fields=[
                    card["q"],
                    card["a"],
                    card.get("ex", ""),
                    card.get("pt", ""),
                    section_label,
                ],
                tags=["computer-theory"] + card.get("tags", []),
                guid=genanki.guid_for(card["q"]),
            )
            deck.add_note(note)
        total += len(cards)
        decks.append(deck)
        print(f"  {subdeck_name}: {len(cards)} cards")

    genanki.Package(decks).write_to_file(out_path)
    print(f"Wrote {total} cards to {out_path}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "computer-theory.apkg")
