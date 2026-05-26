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

## Photographic derivative benchmark assets

The following Shibboleth assets are photographic derivatives built from public-domain or clearly licensed source photos:

- `dataset/images/photo-garbled-library-sign.jpg`
- `dataset/images/photo-duplicated-hat-portrait.jpg`
- `dataset/images/photo-five-chairs-table.jpg`
- `dataset/images/photo-three-wheel-bicycle.jpg`

These files were created in-repo by `scripts/generate_photographic_assets.py`.

### Source files

- `dataset/sources/library-road-sign-source.jpg`
  - Source: https://commons.wikimedia.org/wiki/Special:FilePath/Library-road-sign.jpg
  - License status: Wikimedia Commons public-domain source
- `dataset/sources/portrait-hat-man-source.jpg`
  - Source: https://commons.wikimedia.org/wiki/Special:FilePath/Portrait,%20hat,%20man,%20studio%20Fortepan%203545.jpg
  - License status: Wikimedia Commons public-domain source
- `dataset/sources/table-and-chairs-source.jpg`
  - Source: https://commons.wikimedia.org/wiki/Special:FilePath/Table%20and%20chairs.jpg
  - License status: Wikimedia Commons public-domain source
- `dataset/sources/bicycle-park-source.jpg`
  - Source: https://commons.wikimedia.org/wiki/Special:FilePath/Bicycle2010.JPG
  - License status: public domain (author release on Wikimedia Commons)

The derivatives intentionally introduce clear visual anomalies while preserving the underlying photographic scene. They are meant to be more realistic than the synthetic probes while still staying easy to score.
