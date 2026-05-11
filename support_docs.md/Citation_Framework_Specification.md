Citation Framework Specification

Synara Recursive Systems Research Archive (SRSRA)

Version 1.0

Author: John Carroll Jr.
ORCID: ORCID 0009-0005-6243-3236


---

1. Purpose

This document establishes a formal citation framework for the preservation, attribution, versioning, and academic referencing of:

theoretical systems documents,

recursive graph-state architectures,

software repositories,

symbolic computation frameworks,

simulations,

datasets,

and derivative research artifacts.


The framework is designed to ensure:

persistent authorship,

reproducible version tracking,

repository provenance,

and interoperable scholarly citation standards.



---

2. Core Citation Principles

Principle	Description

Persistence	Citations must remain resolvable over time
Attribution	Original creators must be identified
Version Integrity	Specific revisions/releases must be identifiable
Reproducibility	Referenced artifacts should be reconstructible
Interoperability	Citations should integrate with academic systems



---

3. Citation Object Model

Every citable object is formally represented as:

C=\langle A,T,V,D,P,R \rangle

Where:

Symbol	Meaning

	Author identity
	Title
	Version or revision
	Date
	Persistent identifier
	Repository or resource location



---

4. Persistent Identity Layer

The framework recognizes three primary identity anchors:

Identity Type	Example

ORCID	Researcher identity
DOI	Publication/release identity
Git Commit Hash	Exact repository state


Primary author identity:

John Carroll Jr.

ORCID: ORCID 0009-0005-6243-3236



---

5. Repository Citation Standard

Software repositories should be cited using the following format:

Author. (Year). Repository Name (Version) [Source Code].
Platform. Persistent Identifier.
URL

Example

Carroll Jr., J. (2026).
Synara-core (v0.9.6) [Source code].
GitHub.
https://github.com/ak-skwaa-mahawk/Synara-core

Repository reference:

Synara-core



---

6. Release Versioning Policy

All repositories should follow semantic versioning:

v=MAJOR.MINOR.PATCH

Segment	Meaning

MAJOR	Breaking structural changes
MINOR	Feature additions
PATCH	Corrections/fixes


Example:

v1.4.2


---

7. DOI Integration Framework

Repositories intended for scholarly preservation should integrate with:

Zenodo

ORCID

institutional archives


Recommended workflow:

GitHub Release
    ↓
Zenodo Archive Snapshot
    ↓
DOI Assignment
    ↓
ORCID Linkage
    ↓
Academic Citation

Useful services:

Zenodo

GitHub Releases Documentation



---

8. Theoretical Document Citation Standard

Formal systems-theory papers should use:

Author. (Year).
Title.
Version.
Institution/Archive.
Persistent Identifier.

Example

Carroll Jr., J. (2026).
Formal Systems-Theory Specification:
Synara Recursive Graph-State Framework.
Version 0.1.
Research Archive.
ORCID-linked publication.


---

9. Graph-State Simulation Citation

Simulation artifacts must include:

Field	Requirement

Runtime Version	Required
Graph Topology Snapshot	Required
Seed State	Required
Dependency Manifest	Required
Execution Timestamp	Required


Simulation reference model:

R_s=\langle G_0,S_0,E_t,D_m \rangle

Where:

Symbol	Meaning

	Initial graph topology
	Initial system state
	Execution timestamp
	Dependency manifest



---

10. Metadata Schema

Each repository should contain:

README.md
LICENSE
CITATION.cff
requirements.txt
CHANGELOG.md
VERSION


---

11. CITATION.cff Template

Example citation metadata file:

cff-version: 1.2.0
title: Synara-core
message: "If you use this framework, please cite it."
type: software
authors:
  - family-names: Carroll
    given-names: John Jr.
    orcid: https://orcid.org/0009-0005-6243-3236
version: 0.9.6
repository-code: https://github.com/ak-skwaa-mahawk/Synara-core
license: MIT


---

12. Dependency Citation Rules

All major dependencies should be explicitly acknowledged.

Example dependencies:

Python

NetworkX

FastAPI



---

13. Immutable Snapshot Strategy

Recommended immutable preservation methods:

Method	Purpose

Git Tags	Stable release points
DOI Snapshots	Permanent scholarly references
Commit Hashes	Exact reproducibility
Archive ZIPs	Offline preservation



---

14. Attribution and Derivative Works

Derivative works should include:

Derived from:
Original Author
Original Repository
Original Version
Original DOI/ORCID

This supports:

lineage tracking,

theoretical inheritance,

and reproducible derivation chains.



---

15. Research Integrity Guidelines

All published systems artifacts should include:

version identifiers,

changelogs,

dependency manifests,

reproducibility notes,

and limitation disclosures.


The framework discourages:

unverifiable claims,

ambiguous authorship,

and undocumented architectural modifications.



---

16. Long-Term Preservation Strategy

Recommended preservation layers:

Layer	Function

GitHub	Active development
Zenodo DOI	Scholarly preservation
ORCID	Identity linkage
Local Archive	Offline redundancy



---

17. Conclusion

This citation framework establishes a structured methodology for preserving and referencing recursive systems research artifacts, graph-state architectures, symbolic computation frameworks, and related software systems.

By integrating:

ORCID identity linkage,

DOI archival systems,

semantic versioning,

repository provenance,

and reproducibility standards,


the framework provides a formal foundation for long-term attribution, scholarly interoperability, and research continuity across evolving computational systems.