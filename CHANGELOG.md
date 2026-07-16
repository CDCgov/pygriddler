# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed

- v0.4 parser no longer raises an opaque `TypeError` on an empty `union` or `product`. An empty union now yields the empty experiment and an empty product yields a single empty spec, matching each operator's identity.

## 0.4.0

### Added

- uv tool support

### Changed

- **Breaking**: Griddles must specify a `schema`. Now the schemas can iterate separately from the software version of `griddler` itself.

## 0.3.0

### Removed

- **Breaking**: Functionality unrelated to parsing griddlers, e.g., `run_squash()`

## 0.2.0

v0.2 was the first fully-functioning prototype. It uses a syntax that will be made obsolete with v0.3. It is not recommended for any new project.
