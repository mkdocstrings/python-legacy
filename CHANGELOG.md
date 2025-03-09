# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [0.2.5](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.5) - 2025-03-09

<small>[Compare with 0.2.4](https://github.com/mkdocstrings/python-legacy/compare/0.2.4...0.2.5)</small>

### Build

- Depend on mkdocstrings 0.28.3 ([a2317df](https://github.com/mkdocstrings/python-legacy/commit/a2317df0e27d9ae600bb04843871e3b2f7763c94) by Timothée Mazzucotelli).
- Drop support for Python 3.8 ([2907379](https://github.com/mkdocstrings/python-legacy/commit/290737942189e5f285f170f2d1bb227f82a6017c) by Timothée Mazzucotelli).

## [0.2.4](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.4) - 2024-09-07

<small>[Compare with 0.2.3](https://github.com/mkdocstrings/python-legacy/compare/0.2.3...0.2.4)</small>

### Bug Fixes

- Pass down docstring style and options to pytkdocs ([68934d5](https://github.com/mkdocstrings/python-legacy/commit/68934d5b9050359b2742edd07eb36afe4c51b6e2) by Timothée Mazzucotelli). [Issue-4](https://github.com/mkdocstrings/python-legacy/issues/4)

### Code Refactoring

- Update cross-reference markup to new autorefs format ([89592bd](https://github.com/mkdocstrings/python-legacy/commit/89592bdba0597c1f637978caa19053afbfb124ad) by Matthias Schoettle). [Issue-6](https://github.com/mkdocstrings/python-legacy/issues/6), [PR-7](https://github.com/mkdocstrings/python-legacy/pull/7), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>

## [0.2.3](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.3) - 2022-05-28

<small>[Compare with 0.2.2](https://github.com/mkdocstrings/python-legacy/compare/0.2.2...0.2.3)</small>

### Packaging / Dependencies
- Depend on mkdocstrings 0.19 ([71123dc](https://github.com/mkdocstrings/python-legacy/commit/71123dc4dda6ece390d94d0400920541ded76ede) by Timothée Mazzucotelli).

### Code Refactoring
- Unify default configurations ([47c53fc](https://github.com/mkdocstrings/python-legacy/commit/47c53fcc1c6519025f0aec65b85bdc99e4eac2f5) by Timothée Mazzucotelli).
- Stop using deprecated base classes ([5a28b12](https://github.com/mkdocstrings/python-legacy/commit/5a28b125a2ac87ddf1b804160deb11076a0ae409) by Timothée Mazzucotelli).
- Use new `mkdocstrings_handlers` namespace ([d688c87](https://github.com/mkdocstrings/python-legacy/commit/d688c87dd3eca4d8cc25761d957e6855832da4b4) by Timothée Mazzucotelli).


## [0.2.2](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.2) - 2022-02-19

<small>[Compare with 0.2.1](https://github.com/mkdocstrings/python-legacy/compare/0.2.1...0.2.2)</small>

### Bug Fixes
- Handle empty error in JSON output ([0e7ab59](https://github.com/mkdocstrings/python-legacy/commit/0e7ab594ae550b4c95a3a8b47ff190dbe88ff000) by rachmadani haryono). [PR #1](https://github.com/mkdocstrings/python-legacy/pull/1)


## [0.2.1](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.1) - 2022-02-05

<small>[Compare with 0.2.0](https://github.com/mkdocstrings/python-legacy/compare/0.2.0...0.2.1)</small>

### Dependencies
- Require at least mkdocstrings 0.18 ([09d8e9c](https://github.com/mkdocstrings/python-legacy/commit/09d8e9c4a3d8aaf4ee1d95a702d4ad3c5b46638e) by Timothée Mazzucotelli).


## [0.2.0](https://github.com/mkdocstrings/python-legacy/releases/tag/0.2.0) - 2022-02-03

<small>[Compare with 0.1.0](https://github.com/mkdocstrings/python-legacy/compare/0.1.0...0.2.0)</small>

### Features
- Add `show_signature` rendering option ([e741b37](https://github.com/mkdocstrings/python-legacy/commit/e741b3709e35e89372021a44f46c9b1939c8147d) by Will Da Silva).

### Dependencies
- Depend on mkdocstrings ([a154c05](https://github.com/mkdocstrings/python-legacy/commit/a154c051aa6230870d2857ca911dcf797e0ec8b6) by Timothée Mazzucotelli).

### Code Refactoring
- Add user warning about mkdocstrings extra ([71ea2d8](https://github.com/mkdocstrings/python-legacy/commit/71ea2d80f071e091f7a2f7b695ffcdd9dbe0351f) by Timothée Mazzucotelli).


## [0.1.0](https://github.com/mkdocstrings/python-legacy/releases/tag/0.1.0) - 2021-12-18

<small>[Compare with first commit](https://github.com/mkdocstrings/python-legacy/compare/720f91ec264b37345d6a1fe7e77a3164c0bf642f...0.1.0)</small>

### Features
- Copy code from mkdocstrings ([720f91e](https://github.com/mkdocstrings/python-legacy/commit/720f91ec264b37345d6a1fe7e77a3164c0bf642f) by Timothée Mazzucotelli).
