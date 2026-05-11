DOI-Ready Release Packaging Specification

Synara Research Distribution Standard (SRDS)

Version 1.0

Author: John Carroll Jr.
ORCID: ORCID 0009-0005-6243-3236


---

1. Purpose

This document defines a DOI-ready release packaging standard for:

software repositories,

graph-state simulation systems,

systems-theory publications,

symbolic computation frameworks,

datasets,

and reproducible research artifacts.


The objective is to create release packages compatible with:

Zenodo,

institutional archives,

scholarly repositories,

and long-term preservation systems.


Primary repository target:

Synara-core



---

2. DOI Packaging Goals

Each release package should provide:

Requirement	Purpose

Reproducibility	Reconstructable execution state
Attribution	Persistent authorship
Integrity	Immutable release snapshot
Documentation	Human-readable architecture
Preservation	Long-term archival compatibility



---

3. Standard Release Structure

Recommended release directory structure:

synara-core-vX.Y.Z/
│
├── src/
├── docs/
├── simulations/
├── datasets/
├── tests/
├── examples/
├── archive/
│
├── README.md
├── LICENSE
├── CHANGELOG.md
├── VERSION
├── requirements.txt
├── pyproject.toml
├── CITATION.cff
├── metadata.json
├── DOI_MANIFEST.md
└── REPRODUCIBILITY.md


---

4. Mandatory Release Files

4.1 README.md

Must include:

project overview,

architecture summary,

installation instructions,

execution examples,

citation instructions,

and limitations.



---

4.2 LICENSE

Recommended:

MIT

Apache 2.0

GPLv3


Reference:

Choose a License



---

4.3 CHANGELOG.md

Must document:

release differences,

subsystem modifications,

dependency changes,

and compatibility notes.


Recommended format:

## v0.9.6
- Added graph persistence layer
- Updated recursive propagation operator
- Improved simulation checkpointing


---

4.4 VERSION

Simple plaintext file:

0.9.6


---

5. CITATION Metadata

Required citation metadata file:

cff-version: 1.2.0
title: Synara-core
message: "Please cite this framework using the metadata below."
type: software

authors:
  - family-names: Carroll
    given-names: John Jr.
    orcid: https://orcid.org/0009-0005-6243-3236

version: 0.9.6

repository-code: https://github.com/ak-skwaa-mahawk/Synara-core

license: MIT

Citation format standard:

Citation File Format (CFF)



---

6. metadata.json Schema

Recommended machine-readable metadata:

{
  "title": "Synara-core",
  "version": "0.9.6",
  "author": "John Carroll Jr.",
  "orcid": "0009-0005-6243-3236",
  "repository": "https://github.com/ak-skwaa-mahawk/Synara-core",
  "license": "MIT",
  "keywords": [
    "graph-state",
    "recursive systems",
    "symbolic processing",
    "feedback architecture"
  ],
  "release_date": "2026-05-10"
}


---

7. DOI_MANIFEST.md

Defines archival contents and integrity references.

Example:

# DOI Manifest

Release: v0.9.6

Included:
- Source code
- Documentation
- Simulation artifacts
- Dependency manifests
- Example datasets

Integrity:
- Git commit hash
- SHA256 archive checksum


---

8. Reproducibility Standard

REPRODUCIBILITY.md

Must include:

Section	Description

Runtime Environment	Python version
Dependencies	Package versions
Execution Commands	Startup instructions
Simulation Seeds	Deterministic initialization
Platform Notes	OS/runtime assumptions



---

9. Dependency Preservation

Recommended dependency preservation methods:

Method	Purpose

requirements.txt	Python dependency freeze
pyproject.toml	Build metadata
Dockerfile	Containerized reproducibility
Virtual environment lockfile	Deterministic installs


Core technologies:

Python

NetworkX

FastAPI



---

10. Immutable Integrity Verification

Each release should include:

Git Tag

v0.9.6

SHA256 Checksum

sha256sum synara-core-v0.9.6.zip

Commit Hash

git rev-parse HEAD


---

11. Zenodo DOI Workflow

Recommended DOI workflow:

GitHub Release
      ↓
Zenodo GitHub Sync
      ↓
Automatic DOI Generation
      ↓
ORCID Linkage
      ↓
Scholarly Citation

Resources:

Zenodo GitHub Integration

GitHub Releases Documentation



---

12. Suggested Release Naming Convention

Recommended archive naming:

synara-core-v0.9.6.zip

Alternative research snapshot naming:

synara-core-v0.9.6-doi-release.zip


---

13. Archival Compression Standards

Recommended formats:

Format	Usage

ZIP	General distribution
TAR.GZ	Unix/Linux archival
7Z	High compression


Preferred DOI upload format:

ZIP



---

14. Long-Term Preservation Layers

Recommended redundancy strategy:

Layer	Purpose

GitHub	Active development
Zenodo DOI	Scholarly preservation
ORCID	Identity linkage
Offline archive	Disaster recovery



---

15. Release Validation Checklist

Before DOI publication:

[ ] README complete

[ ] License included

[ ] CITATION.cff valid

[ ] Metadata complete

[ ] Dependencies frozen

[ ] Tests passing

[ ] Version tagged

[ ] Archive checksummed

[ ] Documentation included

[ ] DOI metadata verified



---

16. Recommended Citation Format

Example scholarly citation:

Carroll Jr., J. (2026).
Synara-core (Version 0.9.6) [Software].
GitHub + Zenodo.
https://github.com/ak-skwaa-mahawk/Synara-core


---

17. Conclusion

This DOI-ready release packaging framework establishes a structured methodology for preparing recursive systems research repositories and graph-state architectures for scholarly archival preservation.

By integrating:

semantic versioning,

reproducibility standards,

citation metadata,

DOI workflows,

ORCID linkage,

and immutable release snapshots,


the framework enables long-term academic preservation and verifiable attribution of evolving computational systems research.