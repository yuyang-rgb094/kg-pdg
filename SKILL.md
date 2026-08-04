---
name: "kg-pdg"
description: "Knowledge Graph Probe-Driven Growth — turns static knowledge graphs into living, self-growing ecosystems. Invoke when building, maintaining, or extending domain knowledge graphs through question-driven probe methodology."
---

# KG-PDG: Knowledge Graph Probe-Driven Growth Skill

## When to Invoke

Invoke this skill when any of the following conditions are met:

1. **Building a new knowledge graph from scratch.** You need to construct a domain KG and want it to be structurally complete, evidence-backed, and self-auditing from day one rather than a flat collection of facts.
2. **Gap analysis on an existing graph.** You already have a KG (or a draft) and need to systematically discover what is missing — entities, relations, evidence, or citation paths — before it can be trusted for downstream reasoning.
3. **Literature recall verification.** You want to test whether the graph can answer real domain questions, and whether the supporting literature has been adequately captured. This is the "probe" in Probe-Driven Growth.
4. **Ontology design or restructuring.** You are designing the schema of a KG (knowledge types, meta-paths, evidence tiers, citation relations) and need a principled four-dimensional framework rather than ad hoc modeling.
5. **Coverage auditing.** You need to measure how complete the graph is, identify weak zones, and produce a reproducible completion plan.
6. **Cross-domain KG adaptation.** You want to transplant the methodology from one domain (e.g., medicine) to another (e.g., engineering, law, finance) and need a domain adaptation checklist.

Do **not** invoke this skill for simple fact lookup, single-document summarization, or one-off Q&A that does not involve graph construction or structured knowledge modeling. This skill is a *growth methodology*, not a search engine.

## Core Philosophy

KG-PDG is built on a single inversion of the traditional knowledge engineering workflow:

> **Do not plan the graph top-down. Grow it bottom-up, driven by questions (probes).**

In traditional top-down KG construction, a team first designs a comprehensive ontology, then fills it with entities and relations. This approach suffers from three structural failures:

- **Over-engineering:** the ontology anticipates relations that never materialize, creating empty slots that degrade signal-to-noise.
- **Blind spots:** the ontology cannot anticipate relations that only emerge from real domain questions, so critical connections are missed entirely.
- **Stagnation:** once the initial fill is done, the graph has no internal mechanism for discovering its own gaps. It is a frozen snapshot.

KG-PDG inverts this. The graph starts small — sometimes with as few as 30–60 seed entities — and grows through **probe cycles**. Each probe is a real domain question that the graph is asked to answer. When the graph cannot answer (or answers incompletely), the gap is precisely the growth target. The graph is then completed *only where the probe revealed a gap*, and the completion is verified by a backtest: can the graph now answer the probe?

This produces three properties that top-down graphs lack:

1. **Every entity and relation is justified by a question.** There is no speculative content. Signal density is high.
2. **The graph is structurally self-aware.** It knows where it is complete (probes passed) and where it is incomplete (probes failed). Coverage is measurable, not guessed.
3. **The graph is alive.** Each new probe can trigger growth. The graph does not need to be rebuilt; it extends along the exact axis the probe exposed.

The probe-driven philosophy is domain-agnostic. Whether the domain is cardiology, materials science, tax law, or quantitative finance, the loop is the same: **probe → recall → complete → verify**. What changes is the knowledge-type taxonomy, the evidence hierarchy, and the citation-network conventions — all of which are parameters of the four-dimensional ontology, not of the loop itself.

## The 4-Phase Loop

The KG-PDG methodology runs as a repeating four-phase loop. Each iteration is called a **probe cycle**. The loop is designed so that every phase produces a verifiable artifact, and no phase can be skipped without leaving the graph in an inconsistent state.

### Phase 1: Probe

The probe phase converts a real domain question into a structural demand on the graph.

- **Step 1.1 — Question intake.** Receive a natural-language domain question. This can come from a human expert, a literature scan, or (in mature Loop Engineering) an autonomous probe engine. The question must be specific enough to have a determinable answer space. "What is OCT?" is too vague. "What is the prognostic significance of OCT-detected TCFA in diabetic patients?" is a valid probe.
- **Step 1.2 — Meta-path decomposition.** Parse the question into a meta-path — a sequence of node types and relation types that, if instantiated, would answer the question. For example, the diabetic-TCFA-prognosis question decomposes into `[Condition: Diabetes] → [Modifies] → [Plaque: TCFA] → [Has Prognostic Marker] → [Outcome: MACE]`. If the question implies a path the ontology does not yet support, this is itself a gap (an ontology gap, not just a content gap).
- **Step 1.3 — Gap analysis.** Walk the current graph along the meta-path. Record every node that is missing, every relation that is absent, every entity that exists but lacks the required attribute, and every evidence/citation that is absent. The output is a **gap list** — a structured inventory of what the graph needs in order to answer this probe.
- **Step 1.4 — Gap triage.** Classify each gap by severity:
  - **Blocking gap:** the meta-path is broken; the question cannot even be partially answered.
  - **Partial gap:** the path exists but is missing intermediate nodes or evidence; the answer is directionally available but not fully supported.
  - **Enrichment gap:** the path is complete but additional context (e.g., boundary conditions, alternative thresholds) would strengthen the answer.

The probe phase ends with a gap list that is the input to Phase 2.

### Phase 2: Recall

The recall phase retrieves the external knowledge needed to fill the gaps identified in Phase 1.

- **Step 2.1 — Search-strategy generation.** For each gap, generate a search strategy: which databases to query (PubMed, arXiv, legal databases, financial filings), what query terms to use (derived from the meta-path nodes), and what time window is relevant. The strategy is explicit and reproducible.
- **Step 2.2 — Literature retrieval.** Execute the searches. Collect candidate sources. The goal is **recall**, not precision — it is acceptable to retrieve more than needed, because Phase 3 will filter. What is unacceptable is missing a key paper that the gap list predicted.
- **Step 2.3 — Predicted-paper verification.** This is a distinctive KG-PDG step. Before reading the retrieved papers, the skill predicts which specific papers *should* exist based on the gap structure. For example, if the gap list says "missing the FFR threshold origin," the skill predicts that a landmark trial establishing the FFR≤0.80 threshold must exist. After retrieval, the hit rate of these predictions is measured. A high hit rate means the gap analysis is accurate; a low hit rate means the meta-path decomposition was wrong and Phase 1 must be revisited.
- **Step 2.4 — Source grading.** Each retrieved source is assigned an evidence tier (see Evidence Hierarchy Ontology below). This grading happens at intake, not at writing time, so that every fact entering the graph carries its credibility level from the start.

The recall phase ends with a graded corpus of sources mapped to specific gaps.

### Phase 3: Complete

The completion phase writes new entities, relations, attributes, evidence, and citation links into the graph, following a strict tiered priority.

- **Step 3.1 — Tier 1 completion (structural nodes).** Add the entities and relations that are required to close the blocking gaps — the broken meta-path segments. These are the minimum additions needed for the probe to be answerable at all. Example: if the graph has no "Diabetes" → "TCFA" modifier relation, adding it is Tier 1.
- **Step 3.2 — Tier 2a completion (evidence and thresholds).** Add the evidence tiers, threshold values, and quantitative results that the Tier 1 nodes require. Example: the hazard ratio for MACE in diabetic TCFA patients, with its P0-level source. This is where the graph gains its *factual density*.
- **Step 3.3 — Tier 2b/3 completion (citation paths and context).** Close citation-network paths — link the new evidence to the landmark trials that established it, and trace threshold origins. Add boundary conditions, exclusion criteria, and domain context that qualify the answer. This is where the graph gains its *provenance depth*.
- **Step 3.4 — Bidirectional link integrity.** For every relation added in Tier 1–3, verify that the reverse relation exists. If A → B is added as "modifies," then B → A must exist as "is modified by" (or the ontology-specific inverse). The graph must be traversable in both directions. Broken reverse links are a completion error, not an optimization target.
- **Step 3.5 — Coverage audit.** Re-walk the meta-path. Confirm that every gap in the Phase 1 gap list is now closed. If any gap remains, return to the appropriate tier. The probe cannot proceed to verification until the gap list is empty.

The completion phase ends with a graph that *should* be able to answer the probe, and a coverage audit confirming it.

### Phase 4: Verify

The verification phase tests whether the completed graph actually answers the probe and whether the completion introduced no regressions.

- **Step 4.1 — Forward probe backtest.** Re-ask the original probe question. Walk the graph along the meta-path. Does the graph now produce a coherent, evidence-backed answer? If yes, the probe passed. If no, return to Phase 3.
- **Step 4.2 — Backward probe backtest.** Ask the reverse question. If the probe was "Does diabetes worsen TCFA prognosis?", the backward probe is "What conditions worsen TCFA prognosis?" The graph should return diabetes among the answers, along with any other conditions discovered during completion. This tests bidirectional integrity.
- **Step 4.3 — Random probe backtest.** Select 2–3 previously answered probes at random and re-run them. If any previously passing probe now fails, the completion introduced a regression (e.g., a new relation overwrote an old one, or a node was renamed without updating inbound links). Regressions must be fixed before the cycle is accepted.
- **Step 4.4 — Growth metric recording.** Record the pre- and post-probe graph statistics: entity count, relation count, meta-path count, coverage rate, evidence-tier distribution. These metrics track the graph's growth trajectory and are the empirical basis for judging whether the methodology is working.

The verification phase ends with a passed backtest and a recorded growth metric. The cycle is closed. The next probe can begin.

## Four-Dimensional Ontology

KG-PDG uses a four-dimensional ontology to ensure that every piece of knowledge in the graph is classified, connected, graded, and sourced. The four dimensions are orthogonal: a single fact has a value on each dimension, and the combination of values uniquely determines how that fact should be treated in reasoning.

### Dimension 1: Knowledge Type Ontology (Vertical)

Every entity belongs to one of five knowledge types, which determine the entity's depth standard and trigger rules:

| Type | Label | Description | Depth Standard |
|------|-------|-------------|----------------|
| A | Problem/Question | An open question, clinical problem, or research gap | Must have ≥1 associated meta-path; must link to at least one Consensus or Frontier entity |
| B | Consensus/Empirical | Established, widely accepted knowledge (guidelines, landmark trials) | Must have ≥1 T0 or P0 evidence; must cite the originating source |
| C | Method/Technique | A method, device, or analytical technique | Must link to ≥1 Capability and ≥1 Limitation; must have an Evidence-Condition range |
| D | Concept/Term | A defined term or concept (may evolve) | Must have a definition source; must track concept evolution (supersession links) |
| E | Data/Metric | A quantitative metric, threshold, or dataset | Must have a unit, a reference range, and a source trial/study |

### Dimension 2: Meta-Path Ontology (Horizontal)

The graph is not a free-form network. It is organized around **meta-paths** — 5-node templates that represent canonical reasoning chains in the domain. The canonical template is:

```
[Node 1: Condition/Context] → [Node 2: Modifier/Bridge] → [Node 3: Core Entity] → [Node 4: Mechanism/Marker] → [Node 5: Outcome/Evaluation]
```

A concrete instantiation from the cardiovascular domain:

```
[Diabetes] → [modifies] → [TCFA] → [has marker: LCR] → [predicts MACE, HR=42.73]
```

Instantiation rules:
- Every meta-path must have all 5 nodes filled (or explicitly marked as "unknown — gap").
- The relation between adjacent nodes must use a relation type from the controlled vocabulary.
- A meta-path is the minimum unit of reasoning. If any node is missing, the path is broken and the question cannot be answered.

### Dimension 3: Evidence Hierarchy Ontology (Credibility)

Every factual claim in the graph carries an evidence tier:

| Tier | Label | Description |
|------|-------|-------------|
| T0 | Guideline/Consensus | Practice guidelines, systematic reviews, expert consensus statements |
| P0 | Landmark RCT | Pivotal randomized controlled trial establishing a threshold or standard |
| P1 | RCT/Cohort | Additional RCTs, prospective cohorts, large registries |
| P2 | Observational/Expert | Retrospective studies, case series, expert opinion, conference abstracts |

Rules:
- A threshold or standard of care must be backed by T0 or P0 evidence. If only P1/P2 exists, the claim is labeled "emerging" and cannot be used as a deterministic reasoning anchor.
- **Reverse reconstruction trigger:** if a graph contains a threshold that is widely cited but whose originating trial is missing, the evidence hierarchy is violated. This triggers a mandatory recall cycle to find and cite the original P0 source. Example: the FFR ≤ 0.80 threshold is universally cited; if the graph lacks a link to the FAME 1 trial, reverse reconstruction is triggered.
- The evidence hierarchy integrates with the GRADE framework for domains (like medicine) that use it. T0 maps to GRADE "High," P0/P1 to "Moderate/High," P2 to "Low/Very Low."

### Dimension 4: Citation Network Ontology (Provenance)

Every entity and relation in the graph is linked to its source(s) through a citation network with five relation types:

| Relation Type | Label | Meaning |
|---------------|-------|---------|
| `originates_from` | Origin | The entity/relation was first established in this source |
| `supported_by` | Support | The entity/relation is corroborated by this source |
| `challenged_by` | Challenge | The entity/relation is disputed or contradicted by this source |
| `supersedes` | Supersession | This source replaces an earlier source (concept evolution) |
| `reviewed_in` | Synthesis | This source is a review/synthesis that integrates the entity/relation |

Path closure rules:
- Every factual entity must have at least one `originates_from` or `supported_by` link.
- If a `challenged_by` link exists, the entity must be marked as "contested" in its attributes.
- `supersedes` links must form a chain, not a cycle. If a cycle is detected, it indicates a data error.
- Citation paths must be **closed**: if entity A is supported by paper X, and paper X itself relies on paper Y, the graph should contain the A → X → Y path, not just A → X. This is the **bidirectional link requirement** for the citation dimension — the graph must be traversable from any entity to its ultimate evidentiary root.

## 7 Meta-Rules

The KG-PDG methodology is governed by seven meta-rules. Each rule has an observation (what is seen in practice), a mechanism (why it happens), an example (from the cardiovascular case), and a generalization condition (when the rule applies beyond the original domain).

### Rule 1: Probe-Driven Growth

- **Observation:** Graphs that grow by answering questions are structurally denser and more useful than graphs that grow by topic-area filling.
- **Mechanism:** Questions force meta-path traversal, which exposes exactly which nodes and relations are missing. Topic-area filling, by contrast, adds entities in bulk without testing whether they connect into reasoning chains.
- **Example:** In the cardiovascular OCT case, Probe 5 ("OCT + diabetic TCFA prognosis") added 19 entities in one cycle, all of which were immediately connected into functional meta-paths. A topic-area approach to "OCT prognosis" would have added the same entities but without verifying they formed answerable paths.
- **Generalization condition:** This rule holds in any domain where knowledge is used for reasoning (answering questions, making decisions), not merely for lookup. It may be relaxed in domains where the graph is purely a catalog (e.g., a product inventory), where top-down filling is sufficient.

### Rule 2: Tiered Completion

- **Observation:** Completing all gaps simultaneously leads to errors and regressions. Completing in tiers (structural → evidence → citation/context) is more reliable.
- **Mechanism:** Tier 1 establishes the skeleton (nodes and relations). Tier 2 attaches the facts (evidence, thresholds). Tier 3 attaches the provenance (citation paths, boundary conditions). Building skeleton-first means that when evidence is added, the graph already knows *where* it goes, reducing misplacement errors.
- **Example:** In Probe 5, Tier 1 added 4 entities (the diabetic-TCFA modifier path), Tier 2a added 5 evidence entities (HR values, LCR definition), and Tier 2b/3 added 10 citation/context entities (FAME 1 tracing, PREVENT/PECTUS-AI links, boundary conditions). No regression was introduced because the skeleton was validated before evidence was attached.
- **Generalization condition:** This rule holds in any domain with a multi-level knowledge structure (facts have sources, sources have origins). In a domain where all facts are atomic and sourceless (e.g., a mathematical constant table), tiered completion collapses to a single tier.

### Rule 3: Evidence Grading

- **Observation:** Graphs that do not grade evidence produce false-confidence answers. A guideline recommendation and a single retrospective study are not interchangeable.
- **Mechanism:** Evidence tiers (T0–P2) are attached at intake. When the graph reasons along a meta-path, the weakest evidence tier on the path determines the confidence of the answer. This prevents a P2-anchored claim from being presented with T0-level certainty.
- **Example:** The FFR ≤ 0.80 threshold is backed by the FAME 1 trial (P0). Before the graph traced this origin, the threshold existed as an ungraded fact, and the graph could not distinguish it from a P2-anchored threshold. After grading, the meta-path "FFR threshold → ischemia decision" carries P0 confidence.
- **Generalization condition:** This rule holds in any domain with a credibility hierarchy. In domains where all sources are equally credible (e.g., a formal logic knowledge base where all axioms have equal status), evidence grading is vacuous but harmless.

### Rule 4: Granularity Adaptation

- **Observation:** A single entity sometimes needs to split into multiple entities as the graph matures. The granularity at which the graph was first built is not necessarily the correct granularity.
- **Mechanism:** Probes reveal when a concept is overloaded. If two distinct sub-concepts always appear in different meta-paths with different evidence, they are not one entity — they are two. The graph must support entity splitting: one node becomes two, all inbound and outbound relations are redistributed, and the `supersedes` citation link records the split.
- **Example:** "TCFA" (thin-cap fibroatheroma) was initially a single entity. Probe 5 revealed that OCT-derived TCFA (AI-TCFA, algorithmically detected) and classical histology-derived TCFA (CL-TCFA) have different prognostic implications and appear in different meta-paths. The entity was split into AI-TCFA and CL-TCFA, each with its own evidence and citation network.
- **Generalization condition:** This rule holds in any domain where concepts evolve through refinement. In a domain with a fixed, closed vocabulary (e.g., the periodic table), granularity is stable and this rule does not trigger.

### Rule 5: Coverage Audit

- **Observation:** Without an explicit audit, the graph's coverage is unknown. "We have 87 entities" is not a coverage metric; "90.5% of meta-path nodes are filled" is.
- **Mechanism:** After every probe cycle, the coverage audit re-walks all known meta-paths and computes the percentage of filled nodes. This produces a single, reproducible number that tracks graph maturity. The audit also identifies which meta-paths are weakest, directing the next probe.
- **Example:** After 5 probes, the cardiovascular OCT graph had 87 entities across 9 categories and 4 discovered meta-paths. The coverage audit reported 90.5% node-fill, with the remaining 9.5% concentrated in the "frontier/emerging evidence" paths — correctly signaling that the next probes should target frontier literature, not established consensus.
- **Generalization condition:** This rule holds in any domain where meta-paths are the reasoning unit. In a domain without meta-paths (e.g., a pure entity-attribute store), coverage must be redefined as "percentage of attributes filled," but the audit principle is the same.

### Rule 6: Bidirectional Link Integrity

- **Observation:** Graphs with broken reverse links produce asymmetric answers. The graph can answer "Does diabetes worsen TCFA?" but not "What worsens TCFA?" — even though both answers are in the data.
- **Mechanism:** For every directed relation A → B, the inverse relation B → A must exist. This is enforced in Step 3.4 of the completion phase and re-checked in Step 4.2 (backward probe backtest). The requirement is not just about convenience — it is about reasoning completeness. A graph that can only be traversed in one direction can only answer half the questions its data supports.
- **Example:** In the cardiovascular graph, adding "Diabetes → modifies → TCFA" required adding "TCFA → is modified by → Diabetes." The backward probe "What conditions modify TCFA prognosis?" then correctly returned diabetes, along with CKD and inflammatory states discovered in the same cycle.
- **Generalization condition:** This rule holds in any directed graph used for multi-directional reasoning. In a purely hierarchical taxonomy (e.g., a file system tree), the inverse relation ("is a child of" / "is a parent of") is trivially derivable and bidirectional integrity is automatic. The rule is most consequential in many-to-many relation networks.

### Rule 7: Concept Evolution Tracking

- **Observation:** Domain concepts change over time. A threshold that was 0.75 becomes 0.80. A term that meant one thing in 2010 means something more specific in 2024. Graphs that do not track this evolution present outdated information as current.
- **Mechanism:** The `supersedes` citation relation records concept evolution. When a threshold changes or a concept splits, the old entity is not deleted — it is linked to the new entity via `supersedes`, with a timestamp and a source. The graph retains the full history and can answer both "What is the current threshold?" and "How has the threshold evolved?"
- **Example:** The FFR threshold for ischemia was historically 0.75 (derived from coronary pressure measurement studies), then revised to 0.80 (FAME 1 trial). The graph contains both, linked by `supersedes`, so a meta-path can traverse the evolution. Similarly, the AI-TCFA / CL-TCFA split is recorded as a concept evolution event.
- **Generalization condition:** This rule holds in any domain where knowledge is revised over time. In a domain with timeless truths (e.g., pure mathematics), concepts do not evolve and this rule does not trigger. In fast-moving domains (AI research, regulatory law), this rule is among the most important.

## Domain Adaptation

The KG-PDG loop and four-dimensional ontology are domain-agnostic. What changes across domains is the *content* of each dimension: the knowledge-type taxonomy, the meta-path template, the evidence hierarchy, and the citation conventions. The table below shows how the four dimensions adapt across four representative domains.

| Dimension | Medical (Cardiovascular) | Engineering (Materials) | Legal (Regulatory) | Finance (Quantitative) |
|-----------|--------------------------|------------------------|--------------------|-----------------------|
| **Knowledge Types** | Problem, Consensus (guideline), Method (OCT/FFR), Concept (TCFA), Data (HR, threshold) | Problem, Consensus (standard), Method (test protocol), Concept (alloy class), Data (yield strength) | Problem, Consensus (statute/precedent), Method (legal test), Concept (doctrine), Data (penalty range) | Problem, Consensus (market norm), Method (model), Concept (factor), Data (Sharpe, threshold) |
| **Meta-Path Template** | [Condition] → [Modifier] → [Plaque] → [Marker] → [Outcome] | [Environment] → [Stress] → [Material] → [Property] → [Failure Mode] | [Fact Pattern] → [Legal Test] → [Doctrine] → [Precedent] → [Holding] | [Market Regime] → [Signal] → [Factor] → [Model] → [Return/Risk] |
| **Evidence Hierarchy** | T0 (guideline) → P0 (landmark RCT) → P1 (RCT/cohort) → P2 (observational) | T0 (ISO/ASTM standard) → P0 (landmark study) → P1 (replicated study) → P2 (single test/expert) | T0 (binding statute) → P0 (SCOTUS/precedent) → P1 (appellate) → P2 (trial court/commentary) | T0 (regulatory filing) → P0 (landmark paper) → P1 (replicated study) → P2 (working paper/opinion) |
| **Citation Relations** | originates_from, supported_by, challenged_by, supersedes, reviewed_in | Same five types; "originates_from" = first standardization | Same five types; "originates_from" = enacting authority | Same five types; "originates_from" = first disclosure |
| **Reverse Reconstruction Trigger** | Threshold without originating trial (e.g., FFR ≤ 0.80 without FAME 1) | Property without originating test standard | Doctrine without originating case | Factor without originating paper/filing |
| **Concept Evolution Example** | FFR 0.75 → 0.80; TCFA → AI-TCFA/CL-TCFA | Yield strength redefinition across standard revisions | Doctrine refinement across appellate circuits | Factor decay and replacement over market regimes |

The adaptation process is itself a mini-probe cycle: apply the loop to the new domain's first probe, observe which knowledge types and meta-paths emerge, and instantiate the four-dimensional ontology accordingly. The ontology is *derived from practice*, not imposed from theory — this is the same probe-driven principle applied to ontology design itself.

## Loop Engineering Outlook

The current KG-PDG methodology is **human-in-the-loop**: a human (or human-directed agent) formulates probes, interprets gap analyses, and decides completion actions. This is the correct starting point — the methodology must be validated in the human-in-the-loop regime before any autonomy is introduced.

The long-term vision is **Loop Engineering**: a state in which the knowledge graph, the probe engine, and the consensus tracker form a self-sustaining system that discovers its own gaps, retrieves its own literature, completes its own structures, and verifies its own growth — with human oversight reduced to reviewing flagged anomalies.

Key capabilities of mature Loop Engineering include:

- **Consensus boundary detection:** the graph knows where established consensus ends and active debate begins, and marks the boundary.
- **Academic frontier tracking:** automated monitoring of arXiv/PubMed with citation-network analysis to identify emerging entities before they are manually probed.
- **Automated gap discovery:** the graph self-identifies missing entities and relations through link prediction on meta-path patterns, without waiting for a human probe.
- **Consensus formation observation:** the graph tracks how citation networks converge toward (or diverge from) consensus over time, producing a temporal view of paradigm evolution.
- **Paradigm shift early warning:** the graph detects threshold drift, concept restructuring signals, and citation-velocity anomalies that precede paradigm shifts.

A full technical roadmap (Phase 1: human-in-the-loop [current], Phase 2: semi-autonomous [base KG complete], Phase 3: fully autonomous [Loop Engineering]) and integration with graph learning and the Feynman learning loop is provided in `docs/loop-engineering-outlook.md`.

--- 中文 ---

# KG-PDG：知识图谱探针驱动增长技能

## 何时调用

当满足以下任一条件时，调用本技能：

1. **从零构建新知识图谱。** 你需要构建一个领域知识图谱，并希望它从第一天起就在结构上完整、有证据支撑、且具备自审计能力，而不是一个扁平的事实集合。
2. **对已有图谱进行缺口分析。** 你已经有一个知识图谱（或草稿），需要系统性地发现缺失的内容——实体、关系、证据或引用路径——在将其用于下游推理之前。
3. **文献召回验证。** 你想测试图谱是否能回答真实的领域问题，以及支撑文献是否已被充分捕获。这就是探针驱动增长中的"探针"。
4. **本体设计或重构。** 你正在设计知识图谱的模式（知识类型、元路径、证据层级、引用关系），需要一个有原则的四维框架，而非临时建模。
5. **覆盖度审计。** 你需要衡量图谱的完整程度，识别薄弱区域，并生成可复现的补全计划。
6. **跨领域知识图谱适配。** 你想将方法论从一个领域（如医学）移植到另一个领域（如工程、法律、金融），需要一份领域适配清单。

**不要**在以下情况调用本技能：简单事实查询、单文档摘要、或不涉及图谱构建或结构化知识建模的一次性问答。本技能是一种*增长方法论*，不是搜索引擎。

## 核心理念

KG-PDG 建立在对传统知识工程工作流的一个根本性反转之上：

> **不要自上而下地规划图谱。要以问题（探针）为驱动，自下而上地增长它。**

在传统的自上而下知识图谱构建中，团队首先设计一个全面的本体，然后用实体和关系填充它。这种方法存在三个结构性缺陷：

- **过度工程化：** 本体预期了永远不会出现的关系，产生空槽，降低信噪比。
- **盲区：** 本体无法预期只有在真实领域问题中才会涌现的关系，因此关键连接被完全遗漏。
- **停滞：** 一旦初始填充完成，图谱就没有内部机制来发现自身的缺口。它是一个冻结的快照。

KG-PDG 反转了这一点。图谱从很小开始——有时只有30-60个种子实体——通过**探针循环**增长。每个探针是一个真实的领域问题，要求图谱回答。当图谱无法回答（或回答不完整）时，缺口恰好就是增长目标。然后，图谱*只在探针揭示的缺口处*进行补全，补全通过回测验证：图谱现在能回答探针了吗？

这产生了自上而下图谱所不具备的三个特性：

1. **每个实体和关系都有问题作为理由。** 没有投机性内容。信号密度高。
2. **图谱具有结构自意识。** 它知道哪里是完整的（探针通过）和哪里是不完整的（探针失败）。覆盖度是可测量的，而非猜测的。
3. **图谱是活的。** 每个新探针都可以触发增长。图谱不需要重建；它沿着探针暴露的精确轴线延伸。

探针驱动理念是领域无关的。无论领域是心脏病学、材料科学、税法还是量化金融，循环都是相同的：**探针 → 召回 → 补全 → 验证**。变化的是知识类型分类法、证据层级和引用网络约定——这些都是四维本体的参数，而非循环本身的参数。

## 四阶段循环

KG-PDG 方法论运行为一个重复的四阶段循环。每次迭代称为一个**探针循环**。循环的设计使得每个阶段都产生可验证的产物，且任何阶段都不能跳过，否则图谱将处于不一致状态。

### 阶段1：探针（Probe）

探针阶段将一个真实的领域问题转化为对图谱的结构性需求。

- **步骤1.1——问题接收。** 接收一个自然语言领域问题。问题可以来自人类专家、文献扫描，或（在成熟的回路工程中）自主探针引擎。问题必须足够具体，以有可确定的答案空间。"OCT是什么？"过于模糊。"OCT检测到的TCFA在糖尿病患者中的预后意义是什么？"是一个有效的探针。
- **步骤1.2——元路径分解。** 将问题解析为元路径——一系列节点类型和关系类型，如果被实例化，将回答该问题。例如，糖尿病-TCFA-预后问题分解为 `[Condition: Diabetes] → [Modifies] → [Plaque: TCFA] → [Has Prognostic Marker] → [Outcome: MACE]`。如果问题暗示了一个本体尚不支持的路径，这本身就是一个缺口（本体缺口，而不仅仅是内容缺口）。
- **步骤1.3——缺口分析。** 沿元路径遍历当前图谱。记录每个缺失的节点、每个缺失的关系、每个存在但缺少必需属性的实体、以及每个缺失的证据/引用。输出是一个**缺口列表**——图谱回答该探针所需内容的结构化清单。
- **步骤1.4——缺口分级。** 按严重程度对每个缺口分类：
  - **阻断性缺口：** 元路径断裂；问题甚至无法部分回答。
  - **部分缺口：** 路径存在但缺少中间节点或证据；答案方向上可用但未完全支撑。
  - **增强性缺口：** 路径完整但额外的上下文（如边界条件、替代阈值）将增强答案。

探针阶段以缺口列表结束，该列表是阶段2的输入。

### 阶段2：召回（Recall）

召回阶段检索填补阶段1识别的缺口所需的外部知识。

- **步骤2.1——搜索策略生成。** 为每个缺口生成搜索策略：查询哪些数据库（PubMed、arXiv、法律数据库、金融文件）、使用什么查询词（从元路径节点派生）、以及什么时间窗口相关。策略是显式且可复现的。
- **步骤2.2——文献检索。** 执行搜索。收集候选来源。目标是**召回率**，而非精确率——检索多于所需是可以接受的，因为阶段3会过滤。不可接受的是遗漏了缺口列表预测的关键论文。
- **步骤2.3——预测论文验证。** 这是KG-PDG的独特步骤。在阅读检索到的论文之前，技能根据缺口结构预测*应该*存在哪些具体论文。例如，如果缺口列表说"缺少FFR阈值来源"，技能预测必须存在一个建立FFR≤0.80阈值的标志性试验。检索后，测量这些预测的命中率。高命中率意味着缺口分析准确；低命中率意味着元路径分解有误，需返回阶段1。
- **步骤2.4——来源分级。** 每个检索到的来源被赋予一个证据层级（见下文证据层级本体）。该分级在入库时完成，而非写作时，使得进入图谱的每个事实从一开始就携带其可信度级别。

召回阶段以一个分级的语料库结束，映射到具体缺口。

### 阶段3：补全（Complete）

补全阶段将新实体、关系、属性、证据和引用链接写入图谱，遵循严格的分层优先级。

- **步骤3.1——第一层补全（结构节点）。** 添加闭合阻断性缺口所需的实体和关系——断裂的元路径段。这是探针可被回答的最低限度添加。例如：如果图谱没有"Diabetes" → "TCFA"修饰关系，添加它就是第一层。
- **步骤3.2——第二层a补全（证据与阈值）。** 添加第一层节点所需的证据层级、阈值和定量结果。例如：糖尿病TCFA患者的MACE风险比，及其P0级来源。这是图谱获得*事实密度*的地方。
- **步骤3.3——第二层b/3补全（引用路径与上下文）。** 闭合引用网络路径——将新证据链接到建立它的标志性试验，并追踪阈值来源。添加限定答案的边界条件、排除标准和领域上下文。这是图谱获得*溯源深度*的地方。
- **步骤3.4——双向链接完整性。** 对于在第一至三层添加的每个关系，验证反向关系存在。如果添加了A → B作为"modifies"，则B → A必须作为"is modified by"（或本体特定的逆关系）存在。图谱必须在两个方向上可遍历。断裂的反向链接是补全错误，而非优化目标。
- **步骤3.5——覆盖度审计。** 重新遍历元路径。确认阶段1缺口列表中的每个缺口现已闭合。如果任何缺口仍在，返回相应层级。在缺口列表清空之前，探针不能进入验证。

补全阶段以一个*应该*能回答探针的图谱和确认它的覆盖度审计结束。

### 阶段4：验证（Verify）

验证阶段测试补全后的图谱是否确实回答了探针，以及补全是否引入了回归。

- **步骤4.1——正向探针回测。** 重新提出原始探针问题。沿元路径遍历图谱。图谱现在是否产生连贯的、有证据支撑的答案？如果是，探针通过。如果否，返回阶段3。
- **步骤4.2——反向探针回测。** 提出反向问题。如果探针是"糖尿病是否恶化TCFA预后？"，反向探针是"哪些条件恶化TCFA预后？"图谱应在答案中返回糖尿病，以及补全期间发现的任何其他条件。这测试双向完整性。
- **步骤4.3——随机探针回测。** 随机选择2-3个先前已回答的探针并重新运行。如果任何先前通过的探针现在失败，说明补全引入了回归（例如，新关系覆盖了旧关系，或节点被重命名但未更新入站链接）。回归必须修复，循环才能被接受。
- **步骤4.4——增长指标记录。** 记录探针前后的图谱统计：实体数、关系数、元路径数、覆盖率、证据层级分布。这些指标跟踪图谱的增长轨迹，是判断方法论是否有效的经验基础。

验证阶段以通过的回测和记录的增长指标结束。循环关闭。下一个探针可以开始。

## 四维本体

KG-PDG使用四维本体来确保图谱中的每条知识都被分类、连接、分级和溯源。四个维度是正交的：单个事实在每个维度上都有一个值，值的组合唯一地决定了该事实在推理中应如何处理。

### 维度1：知识类型本体（纵向）

每个实体属于五种知识类型之一，决定实体的深度标准和触发规则：

| 类型 | 标签 | 描述 | 深度标准 |
|------|------|------|----------|
| A | 问题/疑问 | 开放性问题、临床问题或研究缺口 | 必须有≥1关联元路径；必须链接到至少一个共识或前沿实体 |
| B | 共识/经验 | 已建立的、广泛接受的知识（指南、标志性试验） | 必须有≥1 T0或P0证据；必须引用来源 |
| C | 方法/技术 | 一种方法、设备或分析技术 | 必须链接到≥1能力和≥1局限性；必须有证据-条件范围 |
| D | 概念/术语 | 定义的术语或概念（可能演化） | 必须有定义来源；必须跟踪概念演化（替代链接） |
| E | 数据/指标 | 定量指标、阈值或数据集 | 必须有单位、参考范围和来源试验/研究 |

### 维度2：元路径本体（横向）

图谱不是自由形式的网络。它围绕**元路径**组织——5节点模板，代表领域中的规范推理链。规范模板是：

```
[节点1：条件/上下文] → [节点2：修饰/桥接] → [节点3：核心实体] → [节点4：机制/标志物] → [节点5：结局/评估]
```

来自心血管领域的具体实例化：

```
[糖尿病] → [修饰] → [TCFA] → [有标志物：LCR] → [预测MACE, HR=42.73]
```

实例化规则：
- 每个元路径必须填满所有5个节点（或明确标记为"未知——缺口"）。
- 相邻节点之间的关系必须使用受控词汇中的关系类型。
- 元路径是推理的最小单位。如果任何节点缺失，路径断裂，问题无法回答。

### 维度3：证据层级本体（可信度）

图谱中的每个事实声明都携带一个证据层级：

| 层级 | 标签 | 描述 |
|------|------|------|
| T0 | 指南/共识 | 实践指南、系统综述、专家共识声明 |
| P0 | 标志性RCT | 建立阈值或标准的关键随机对照试验 |
| P1 | RCT/队列 | 额外的RCT、前瞻性队列、大型注册研究 |
| P2 | 观察性/专家 | 回顾性研究、病例系列、专家意见、会议摘要 |

规则：
- 阈值或标准护理必须有T0或P0证据支撑。如果只有P1/P2存在，该声明被标记为"新兴"，不能用作确定性推理锚点。
- **逆向重构触发条件：** 如果图谱包含一个被广泛引用但其来源试验缺失的阈值，证据层级被违反。这触发强制召回循环以找到并引用原始P0来源。例如：FFR ≤ 0.80阈值被普遍引用；如果图谱缺少与FAME 1试验的链接，则触发逆向重构。
- 证据层级与GRADE框架集成，适用于使用它的领域（如医学）。T0映射到GRADE"高"，P0/P1映射到"中/高"，P2映射到"低/极低"。

### 维度4：引用网络本体（溯源）

图谱中的每个实体和关系通过具有五种关系类型的引用网络链接到其来源：

| 关系类型 | 标签 | 含义 |
|----------|------|------|
| `originates_from` | 来源 | 实体/关系首次在此来源中建立 |
| `supported_by` | 支撑 | 实体/关系被此来源佐证 |
| `challenged_by` | 挑战 | 实体/关系被此来源争议或反驳 |
| `supersedes` | 替代 | 此来源替代了早期来源（概念演化） |
| `reviewed_in` | 综合 | 此来源是整合该实体/关系的综述 |

路径闭合规则：
- 每个事实实体必须有至少一个`originates_from`或`supported_by`链接。
- 如果存在`challenged_by`链接，该实体必须在其属性中标记为"有争议"。
- `supersedes`链接必须形成链，而非环。如果检测到环，说明存在数据错误。
- 引用路径必须**闭合**：如果实体A被论文X支撑，而论文X本身依赖论文Y，图谱应包含A → X → Y路径，而不仅仅是A → X。这是引用维度的**双向链接要求**——图谱必须可从任何实体遍历到其最终证据根源。

## 7条元规则

KG-PDG方法论受七条元规则约束。每条规则有观察（实践中所见）、机制（为何发生）、示例（来自心血管案例）和泛化条件（规则何时适用于原始领域之外）。

### 规则1：探针驱动增长

- **观察：** 通过回答问题来增长的图谱比通过主题区域填充来增长的图谱在结构上更密集、更有用。
- **机制：** 问题强制元路径遍历，精确暴露哪些节点和关系缺失。主题区域填充则相反，批量添加实体而不测试它们是否连接成推理链。
- **示例：** 在心血管OCT案例中，探针5（"OCT + 糖尿病TCFA预后"）在一个循环中添加了19个实体，所有实体都立即连接到功能性元路径。对"OCT预后"的主题区域方法会添加相同的实体，但不会验证它们形成了可回答的路径。
- **泛化条件：** 该规则适用于知识用于推理（回答问题、做决策）而非仅用于查询的任何领域。在图谱纯粹是目录（如产品库存）的领域，可以放宽，自上而下填充即可。

### 规则2：分层补全

- **观察：** 同时补全所有缺口会导致错误和回归。分层补全（结构 → 证据 → 引用/上下文）更可靠。
- **机制：** 第一层建立骨架（节点和关系）。第二层附着事实（证据、阈值）。第三层附着溯源（引用路径、边界条件）。先建骨架意味着当添加证据时，图谱已经知道它*去哪里*，减少错位错误。
- **示例：** 在探针5中，第一层添加了4个实体（糖尿病-TCFA修饰路径），第二层a添加了5个证据实体（HR值、LCR定义），第二层b/3添加了10个引用/上下文实体（FAME 1追踪、PREVENT/PECTUS-AI链接、边界条件）。没有引入回归，因为在附着证据之前骨架已验证。
- **泛化条件：** 该规则适用于任何具有多层级知识结构的领域（事实有来源，来源有起源）。在所有事实都是原子且无来源的领域（如数学常数表），分层补全退化为单层。

### 规则3：证据分级

- **观察：** 不分级证据的图谱产生虚假置信度答案。指南推荐和单个回顾性研究不可互换。
- **机制：** 证据层级（T0-P2）在入库时附着。当图谱沿元路径推理时，路径上最弱的证据层级决定答案的置信度。这防止了P2锚定的声明以T0级别的确定性呈现。
- **示例：** FFR ≤ 0.80阈值由FAME 1试验（P0）支撑。在图谱追踪该来源之前，阈值作为一个未分级的事实存在，图谱无法将其与P2锚定的阈值区分。分级后，元路径"FFR阈值 → 缺血决策"携带P0置信度。
- **泛化条件：** 该规则适用于任何具有可信度层级的领域。在所有来源可信度相同的领域（如所有公理地位相等的形式逻辑知识库），证据分级是空洞的但无害。

### 规则4：粒度适配

- **观察：** 随着图谱成熟，单个实体有时需要分裂为多个实体。图谱最初构建时的粒度不一定是正确的粒度。
- **机制：** 探针揭示概念何时被过载。如果两个不同的子概念总是出现在不同元路径中并伴有不同证据，它们不是一个实体——它们是两个。图谱必须支持实体分裂：一个节点变为两个，所有入站和出站关系重新分配，`supersedes`引用链接记录分裂。
- **示例：** "TCFA"（薄帽纤维粥样硬化斑块）最初是单个实体。探针5揭示OCT衍生的TCFA（AI-TCFA，算法检测）和经典组织学衍生的TCFA（CL-TCFA）具有不同的预后意义，出现在不同元路径中。实体分裂为AI-TCFA和CL-TCFA，各有自己的证据和引用网络。
- **泛化条件：** 该规则适用于概念通过细化演化的任何领域。在具有固定、封闭词汇的领域（如元素周期表），粒度稳定，该规则不触发。

### 规则5：覆盖度审计

- **观察：** 没有显式审计，图谱的覆盖度是未知的。"我们有87个实体"不是覆盖度指标；"90.5%的元路径节点已填充"是。
- **机制：** 每个探针循环后，覆盖度审计重新遍历所有已知元路径并计算填充节点百分比。这产生一个单一、可复现的数字来跟踪图谱成熟度。审计还识别哪些元路径最弱，指导下一个探针。
- **示例：** 5个探针后，心血管OCT图谱有87个实体，跨9个类别和4个发现的元路径。覆盖度审计报告90.5%的节点填充率，剩余9.5%集中在"前沿/新兴证据"路径——正确信号表明下一个探针应针对前沿文献，而非已建立的共识。
- **泛化条件：** 该规则适用于元路径是推理单位的任何领域。在没有元路径的领域（如纯实体-属性存储），覆盖度必须重新定义为"已填充属性百分比"，但审计原则相同。

### 规则6：双向链接完整性

- **观察：** 反向链接断裂的图谱产生不对称答案。图谱能回答"糖尿病是否恶化TCFA？"但不能回答"什么恶化TCFA？"——尽管两个答案都在数据中。
- **机制：** 对于每个有向关系A → B，必须存在逆关系B → A。这在补全阶段的步骤3.4中强制执行，并在步骤4.2（反向探针回测）中重新检查。该要求不仅关乎便利性——关乎推理完整性。只能在一个方向遍历的图谱只能回答其数据支持的一半问题。
- **示例：** 在心血管图谱中，添加"Diabetes → modifies → TCFA"需要添加"TCFA → is modified by → Diabetes"。反向探针"什么条件修饰TCFA预后？"随后正确返回了糖尿病，以及同一循环中发现的CKD和炎症状态。
- **泛化条件：** 该规则适用于用于多方向推理的任何有向图。在纯层次分类法（如文件系统树）中，逆关系（"是...的子项"/"是...的父项"）可平凡导出，双向完整性是自动的。该规则在多对多关系网络中最具影响力。

### 规则7：概念演化追踪

- **观察：** 领域概念随时间变化。曾是0.75的阈值变为0.80。2010年意味着一件事的术语在2024年意味着更具体的东西。不追踪这种演化的图谱将过时信息呈现为当前信息。
- **机制：** `supersedes`引用关系记录概念演化。当阈值改变或概念分裂时，旧实体不被删除——它通过`supersedes`链接到新实体，附带时间戳和来源。图谱保留完整历史，可同时回答"当前阈值是什么？"和"阈值如何演化？"
- **示例：** FFR缺血阈值历史上是0.75（源自冠脉压力测量研究），后来修订为0.80（FAME 1试验）。图谱包含两者，通过`supersedes`链接，使元路径可遍历演化。同样，AI-TCFA / CL-TCFA分裂被记录为概念演化事件。
- **泛化条件：** 该规则适用于知识随时间修订的任何领域。在具有永恒真理的领域（如纯数学），概念不演化，该规则不触发。在快速变化的领域（AI研究、监管法律），该规则是最重要的之一。

## 领域适配

KG-PDG循环和四维本体是领域无关的。跨领域变化的是每个维度的*内容*：知识类型分类法、元路径模板、证据层级和引用约定。下表展示四个维度在四个代表性领域中如何适配。

| 维度 | 医学（心血管） | 工程（材料） | 法律（监管） | 金融（量化） |
|------|----------------|--------------|--------------|--------------|
| **知识类型** | 问题、共识（指南）、方法（OCT/FFR）、概念（TCFA）、数据（HR、阈值） | 问题、共识（标准）、方法（测试协议）、概念（合金类别）、数据（屈服强度） | 问题、共识（法规/先例）、方法（法律检验）、概念（学说）、数据（处罚范围） | 问题、共识（市场惯例）、方法（模型）、概念（因子）、数据（夏普比率、阈值） |
| **元路径模板** | [条件] → [修饰] → [斑块] → [标志物] → [结局] | [环境] → [应力] → [材料] → [属性] → [失效模式] | [事实模式] → [法律检验] → [学说] → [先例] → [裁决] | [市场状态] → [信号] → [因子] → [模型] → [收益/风险] |
| **证据层级** | T0（指南）→ P0（标志性RCT）→ P1（RCT/队列）→ P2（观察性） | T0（ISO/ASTM标准）→ P0（标志性研究）→ P1（重复研究）→ P2（单次测试/专家） | T0（约束性法规）→ P0（最高法院/先例）→ P1（上诉法院）→ P2（初审法院/评论） | T0（监管文件）→ P0（标志性论文）→ P1（重复研究）→ P2（工作论文/意见） |
| **引用关系** | originates_from, supported_by, challenged_by, supersedes, reviewed_in | 同五种类型；"originates_from" = 首次标准化 | 同五种类型；"originates_from" = 制定机构 | 同五种类型；"originates_from" = 首次披露 |
| **逆向重构触发条件** | 无来源试验的阈值（如FFR ≤ 0.80无FAME 1） | 无来源测试标准的属性 | 无来源案例的学说 | 无来源论文/文件的因子 |
| **概念演化示例** | FFR 0.75 → 0.80；TCFA → AI-TCFA/CL-TCFA | 屈服强度跨标准版本的重新定义 | 学说跨上诉巡回区的细化 | 因子跨市场状态的衰减与替代 |

适配过程本身是一个迷你探针循环：将循环应用于新领域的第一个探针，观察涌现哪些知识类型和元路径，并据此实例化四维本体。本体*从实践中派生*，而非从理论中施加——这是将探针驱动原则应用于本体设计本身。

## 回路工程展望

当前KG-PDG方法论是**人在回路中**：人类（或人类指挥的代理）制定探针、解释缺口分析并决定补全行动。这是正确的起点——方法论必须在人在回路中的机制下验证，才能引入任何自主性。

长期愿景是**回路工程**（Loop Engineering）：知识图谱、探针引擎和共识追踪器形成一个自维持系统，自行发现缺口、检索文献、补全结构并验证增长——人的监督减少为审查标记的异常。

成熟回路工程的关键能力包括：

- **共识边界检测：** 图谱知道已建立共识在哪里结束、活跃辩论在哪里开始，并标记边界。
- **学术前沿追踪：** 自动监控arXiv/PubMed，进行引用网络分析，在人工探针之前识别新兴实体。
- **自动缺口发现：** 图谱通过元路径模式上的链接预测自行识别缺失的实体和关系，无需等待人工探针。
- **共识形成观察：** 图谱追踪引用网络随时间如何趋向（或偏离）共识，产生范式演化的时间视图。
- **范式转移早期预警：** 图谱检测阈值漂移、概念重构信号和引用速度异常，这些先于范式转移。

完整的技术路线图（阶段1：人在回路中[当前]、阶段2：半自主[基础KG完成]、阶段3：全自主[回路工程]）以及与图学习和费曼学习回路的集成，详见 `docs/loop-engineering-outlook.md`。
