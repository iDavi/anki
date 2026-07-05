# Computer Theory — Anki Deck

A complete, zero-prerequisites Anki deck covering **theory of computation**
(*teoria da computação*), the course taught at USP as *Autômatos,
Computabilidade e Complexidade* (MAC0414 and similar), following the standard
university syllabus (Sipser, *Introduction to the Theory of Computation* —
the classic textbook worldwide and at USP).

**130 cards** in 6 subdecks, ordered as a course:

| Subdeck | Topic | Cards |
|---|---|---|
| 00 Foundations | sets, strings, languages, countability, proof techniques | 21 |
| 01 Regular Languages | DFA, NFA, regex, pumping lemma, Myhill–Nerode | 30 |
| 02 Context-Free Languages | CFG, parse trees, PDA, CNF, CFL pumping lemma | 22 |
| 03 Turing Machines | formal model, variants, Church–Turing thesis | 16 |
| 04 Decidability | A_TM, halting problem, reductions, Rice's theorem | 17 |
| 05 Complexity | P, NP, NP-completeness, Cook–Levin, PSPACE, hierarchies | 24 |

Every card has three layers:

- **Answer** — the precise definition/theorem/proof sketch, as expected in exams;
- 💡 **Example & intuition** — a concrete example, a mnemonic, or the classic exam trap;
- 🇧🇷 **Portuguese key term** — the terminology used in Brazilian
  universities, so the vocabulary on the exam won't surprise you.

Cards tagged `keyproof` are the proofs you should be able to reproduce on
paper; cards tagged `trap` are classic exam mistakes.

## Using the deck

1. Install [Anki](https://apps.ankiweb.net/) (desktop) or AnkiDroid/AnkiMobile.
2. Double-click `computer-theory.apkg` (or *File → Import*).
3. Study the subdecks **in order** (00 → 05) — later sections assume earlier ones.

Suggested pace: one subdeck per week ≈ 6 weeks, with daily reviews (the
whole point of spaced repetition — don't binge, review daily). Flashcards
teach you the concepts, statements, and proof *outlines*; to pass a written
exam, also practice writing 3–4 full proofs per section by hand (pumping
lemma arguments, one undecidability reduction, one NP-completeness
reduction). The `technique` tag marks the cards that give you the templates.

## Rebuilding

```
pip install genanki
python3 build_deck.py computer-theory.apkg
```

Card content lives in `cards/*.py`, one module per subdeck — edit and
rebuild; notes keep stable identities (GUIDs derived from the question), so
re-importing updates cards in place without losing review history.
