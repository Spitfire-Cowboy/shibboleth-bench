# Dataset provenance

## Synthetic benchmark assets

The following Shibboleth assets are **self-authored synthetic probe images** created in-repo by `scripts/generate_synthetic_assets.py`:

- `dataset/images/mirror-hat-mismatch.png`
- `dataset/images/water-reflection-buoys.png`
- `dataset/images/six-finger-hand.png`
- `dataset/images/garbled-sign-text.png`
- `dataset/images/detached-glasses-arm.png`
- `dataset/images/shadow-direction-mismatch.png`
- `dataset/images/repeated-chairs-count.png`
- `dataset/images/detached-mug-handle.png`
- `dataset/images/transparent-glasses-count.png`

These images are intentionally simple. They are not meant to be photoreal examples of AI imagery. They are controlled anomaly probes for testing whether multimodal models can:
- count discrete objects correctly
- reason about reflection mismatch
- detect malformed text
- detect attachment and continuity problems
- detect transparent-object counting cases
- detect obvious lighting contradictions

## Canonical logo benchmark item

- `dataset/images/two-hat-logo.png`

This benchmark item remains the original motivating probe for the repository and should continue to be tracked separately in any publication-quality discussion.
