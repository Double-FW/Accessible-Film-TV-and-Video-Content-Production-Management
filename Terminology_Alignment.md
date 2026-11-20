---
title: "Terminology alignment for accessible media production"
version: "1.0.0"
date: "2026-11-20"
license: "MIT"
language: "en-GB"
status: "editorial_alignment_not_organisational_adoption"
---

# Terminology alignment

This document applies the scoped decisions in [Double-FW Terminology and Principles](https://github.com/Double-FW/Terminology-and-Principles). The inspected revision is `219b5feddd271bcdf70ea0ac0c4bc5c62fe9a0f4`, specifically its [governance](https://github.com/Double-FW/Terminology-and-Principles/blob/219b5feddd271bcdf70ea0ac0c4bc5c62fe9a0f4/GOVERNANCE.md), [decision register](https://github.com/Double-FW/Terminology-and-Principles/blob/219b5feddd271bcdf70ea0ac0c4bc5c62fe9a0f4/review/DECISIONS.md) and media, experience and evidence glossaries. Most individual definitions remain proposed; this alignment does not approve them all or adopt a production policy.

## Authority and purpose

Use adopted Double-FW meanings when applying Double-FW methodologies. Name and explain a departure from another organisation's approach. Preserve the actual meaning and exceptions of a statute, contract, WCAG criterion or technical specification when citing it. A preferred editorial term cannot change an external requirement. Resolve applicability from current primary sources and the production's actual authority, with specialist advice where needed. Publication, a Git merge or a dataset export is not client approval.

## Media terms

| Term | Working use here | Boundary to preserve |
| --- | --- | --- |
| Audio description (AD) | Spoken access to relevant visual information within the programme experience | Integrated, separate, hybrid and extended routes are possible. A separate track is not the universal definition; choose and verify the route against actual picture/sound and applicable requirements. |
| Captions | Synchronised text conveying relevant speech, speaker information and meaningful non-speech audio | A dialogue-only transcript or translation is not automatically equivalent. |
| Subtitles | Timed text under a stated language and access specification | Regional usage differs; specify sound coverage, language and intended audience instead of relying on the label. |
| Closed Caption Subtitles (CCS) | The defined, viewer-selectable access track in the linked caption guideline | Preserve its owning definition. `CCS 013` is a criterion; section 13 is the separate player section. |
| Transcript | Structured text representing the relevant media/audio information | It is not automatically synchronised or a replacement for required description, captions or signing. |
| Descriptive transcript | Text including relevant visual information as well as audio content | State scope and structure. Its existence does not establish a usable synchronised listening route. |
| Sign-language access | Content in the signed language selected for the actual audience | Signed languages are natural languages, not universal gestural versions of speech or interchangeable with captions. |

Preserve people's chosen identity language, including Deaf and neurodivergent identities. Do not infer diagnosis, preferred language or access route from a person's behaviour, voice or assistive technology.

## Experience principles

- **Equivalent/comparable experience:** state the comparison across meaning, outcomes, effort, privacy, availability, control and dignity. Equivalent does not mean identical formats or a guaranteed experience for everyone (D02).
- **Satisfactory** names the additional proposed Double-FW experience principle; **satisfaction** describes a person's assessment. Neither is a fifth official WCAG principle (D01).
- **Feeling Seen, Feeling Capable, Feeling Confident, Feeling Safe and Feeling Valued** are research lenses and intended qualities. Do not assign them to an audience from the producer's intention or a technical pass (D03).
- Keep WCAG robustness, Agentic Robustness and the reliability of a particular access asset distinct. No general robustness claim proves every player or assistive-technology combination works (D06).
- If using cognitive identifiers, write `CP-01`–`CP-10` with the owning Cognitive UX source. Bare `CP` can have another meaning in other matrices (D04).
- Use **ACT-style procedural test** for a local structured test and **user-oriented task script** for a complete audience activity. Use **W3C ACT** only for the actual W3C work and its stated rule status (D05).

For media, investigate whether people can discover the relevant version, understand or enjoy the intended content, control its presentation and recover from interruption without avoidable effort or loss of dignity. Measure comprehension, technical performance and participant accounts separately; viewing duration alone does not establish engagement or benefit.

## Evidence and decision states

| Label | Meaning in this repository |
| --- | --- |
| Verified | Specified evidence supports a stated requirement for the named version, destination and scope. It is not a blanket accessibility or legal assurance. |
| Failed | Evidence shows the scoped requirement was not met. |
| Unknown | The relevant result has not been established by available evidence. |
| Not tested | The specified evaluation was not performed. This is distinct from an inconclusive performed test. |
| Not applicable | The requirement does not apply in the recorded scope, with reason and the required decision authority. |
| Unresolved | An issue or decision remains open; record its cause, underlying result, owner and next action separately. |
| Proposed / approved | Distinct decision states. Approval needs the actual authorised decision record; it is not inferred from an agent output or filled template. |

Preserve observations, hypotheses, estimates and synthetic examples as separate evidence types (D07). Record original source review dates and export dates separately. A retrieval timestamp does not renew legal or scientific verification. External meanings remain source-owned (D08).

## Handoff states

Receipt, file validation, editorial review, human acceptance, release authorisation and publication verification are separate events. A production may have an accepted caption file while the platform's published rendition remains not tested. Record each state and its evidence without calling the entire journey complete.
