# Shibboleth expansion targets: common AI image failure modes

This document records high-signal visual failure modes worth turning into future Shibboleth benchmark items.

The goal is not to collect every possible artifact. It is to focus on **small, high-confidence probes** that multimodal models should either answer correctly or fail clearly.

## Selection principles

A good Shibboleth item should be:
- visually simple
- easy to score
- hard to wave away with vague language
- specific enough that a wrong answer is obviously wrong
- reproducible in a single image

## Priority edge cases

### 1. Hands and fingers

Why it matters:
- still one of the most common failure surfaces in synthetic imagery
- easy for both humans and models to reason about when posed simply

Good benchmark forms:
- count visible fingers on a single hand
- identify whether a hand has too many fingers
- determine whether fingers are fused / merged / duplicated

Suggested prompt styles:
- `How many fingers are visible on the raised hand?`
- `Is this hand anatomically normal? Answer yes or no.`

## 2. Mirror reflections

Why it matters:
- mirror geometry still exposes inconsistencies in many generated images
- easy to make a binary or counting probe

Good benchmark forms:
- person facing mirror with mismatched reflection pose
- reflected object count differs from real object count
- hat / glasses / hand position differs across mirror plane

Suggested prompt styles:
- `Does the mirror reflection match the real pose? Answer yes or no.`
- `How many hats appear in the mirror?`

## 3. Water or glossy-surface reflections

Why it matters:
- water and shiny surfaces often produce broken reflection logic
- complements mirror tests without being the same geometry problem

Good benchmark forms:
- lake or puddle reflection missing part of subject
- reflected count differs from subject count
- reflected lighting or orientation is impossible

Suggested prompt styles:
- `Does the water reflection show the same number of people?`
- `Is the reflection physically consistent? Answer yes or no.`

## 4. Text, signage, and labels

Why it matters:
- image generators often produce plausible-looking but wrong text
- multimodal models can also misread or overconfidently normalize it

Good benchmark forms:
- sign with near-legible but wrong text
- product label with malformed brand text
- book cover or poster with obvious garbling

Suggested prompt styles:
- `What exact word is printed on the sign?`
- `Is the label readable English? Answer yes or no.`

## 5. Eyewear, jewelry, and symmetrical accessories

Why it matters:
- asymmetry and attachment errors remain common in generated imagery
- good source of binary checks

Good benchmark forms:
- one earring missing or malformed
- glasses arm detached from frame
- sunglasses reflection inconsistent between lenses

Suggested prompt styles:
- `Are both earrings present?`
- `Do the glasses attach correctly on both sides?`

## 6. Repeated object patterns

Why it matters:
- repeated motifs often reveal duplication or counting mistakes
- easy to score when the count is small and explicit

Good benchmark forms:
- chairs around a table
- plates in a cabinet
- windows on a facade
- wheels on a bicycle or car-like object

Suggested prompt styles:
- `How many chairs are visible around the table?`
- `How many wheels does the bicycle have?`

## 7. Shadow and lighting contradictions

Why it matters:
- generated imagery often looks plausible locally while violating scene-wide lighting consistency
- good for yes/no probes

Good benchmark forms:
- two subjects lit from incompatible directions
- object shadow missing or pointing the wrong way
- mirrored lighting inconsistent across a reflective surface

Suggested prompt styles:
- `Do the shadows fall in the same direction?`
- `Is the lighting physically consistent?`

## 8. Object attachment and continuity

Why it matters:
- generators still create floating straps, disconnected handles, impossible seams, or merged edges
- strong screening signal when the object is familiar

Good benchmark forms:
- mug handle detached from mug
- guitar strap unattached
- backpack strap passing through a body
- watch band disconnected from the watch face

Suggested prompt styles:
- `Is the strap attached correctly?`
- `Does the object connect physically in a plausible way?`

## 9. Transparent objects and glass

Why it matters:
- transparency, refraction, and overlapping contours remain brittle
- useful complement to reflection tests

Good benchmark forms:
- glass containing impossible liquid boundary
- transparent vase with inconsistent background distortion
- drinking glass with impossible rim or handle geometry

Suggested prompt styles:
- `Is the glass physically plausible? Answer yes or no.`
- `How many transparent glasses are on the table?`

## 10. Face-side consistency

Why it matters:
- while faces are much better than early models, ears, teeth, and side accessories can still break
- useful only when the flaw is crisp and unambiguous

Good benchmark forms:
- mismatched earrings
- extra teeth or merged teeth in a grin
- ear shape inconsistent across sides

Suggested prompt styles:
- `Are both ears shaped normally?`
- `Does the smile show a normal number of visible teeth?`

## Current coverage

Already represented in the checked-in dataset:
- hands / finger count
- mirror mismatch
- water reflection mismatch
- malformed sign text
- accessory asymmetry / detached glasses
- repeated-object counting
- shadow contradiction
- object continuity / attachment
- transparent-object counting

## Recommended next dataset build order

1. **More naturalistic mirror and reflection scenes**
2. **Accessory symmetry variants (earrings, watches, straps)**
3. **Transparent-object plausibility beyond simple counting**
4. **Wheel / window / repeated-structure counting**
5. **Face-side consistency probes**
6. **More realistic lighting contradictions**

## Acquisition guidance

For public release, prefer images that are:
- created in-house
- clearly licensed for redistribution
- accompanied by provenance notes
- stable enough that future reruns use the exact same file

## Research notes

This expansion plan is informed by repeated public reporting and academic discussion around synthetic-image artifacts, including:
- hand/finger artifact work such as HanDiffuser (`arXiv:2403.01693`)
- detection guides that emphasize reflections, text, accessories, and lighting inconsistencies
- broader discussion of artifact localization and human-detectable cues in generated images
