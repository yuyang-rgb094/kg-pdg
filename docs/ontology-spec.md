# KG-PDG Ontology Specification

This document provides a formal specification of the four-dimensional ontology used by the Knowledge Graph Probe-Driven Growth (KG-PDG) methodology. The four dimensions are orthogonal: every entity and relation in the graph has a value on each dimension, and the combination of values determines how that knowledge is treated in reasoning, completion, and verification.

---

## 1. Knowledge Type Ontology (Vertical Dimension)

The vertical dimension classifies every entity into one of five knowledge types. The type determines the entity's depth standard (what attributes and relations it must have) and its trigger rules (when the entity must be revisited or expanded).

| Type | Label | Description | Depth Standard | Trigger Rules |
|------|-------|-------------|----------------|---------------|
| **A** | Problem/Question | An open question, clinical problem, research gap, or unresolved issue in the domain | Must have ≥1 associated meta-path; must link to ≥1 Consensus (Type B) or Frontier entity; must have a status field: open / partially resolved / resolved | Triggered when a probe reveals a meta-path that cannot be completed. Must be revisited when a linked Consensus entity is superseded. |
| **B** | Consensus/Empirical | Established, widely accepted knowledge — practice guidelines, landmark trial results, systematic reviews, expert consensus statements | Must have ≥1 T0 or P0 evidence link; must cite the originating source via `originates_from`; must have a timestamp of consensus establishment | Triggered when a new `challenged_by` citation appears. If challenges accumulate, status shifts to "contested" and a Type A Problem entity is spawned. |
| **C** | Method/Technique | A method, device, analytical technique, or procedural approach used in the domain | Must link to ≥1 Capability (what it can do) and ≥1 Limitation (what it cannot do); must have an Evidence-Condition range (under what conditions it is validated) | Triggered when a probe requires evaluating a method's applicability. Must be revisited when new validation studies emerge. |
| **D** | Concept/Term | A defined term, concept, or conceptual category that may evolve over time | Must have a definition source (`originates_from`); must track concept evolution via `supersedes` links; must have a current-status field: active / superseded / split | Triggered when a probe reveals that a concept is overloaded (appears in incompatible meta-paths). May trigger granularity adaptation (entity split). |
| **E** | Data/Metric | A quantitative metric, threshold value, dataset, or numerical standard | Must have: a unit, a reference range, a source trial/study (`originates_from`), and an evidence tier (T0–P2) | Triggered when a probe requires a quantitative answer. Must be revisited when threshold drift is detected (newer sources cite modified values). |

### Type Interaction Rules

- A Type A entity (Problem) that is "resolved" must link to the Type B entity (Consensus) that resolved it.
- A Type B entity (Consensus) must be backed by at least one Type E entity (Data/Metric) if it involves a quantitative standard.
- A Type C entity (Method) that produces Type E data must link to that data via a "produces" relation.
- A Type D entity (Concept) that has been split must retain `supersedes` links to all successor entities, and all successor entities must link back via "succeeds."
- A Type E entity (Data/Metric) whose evidence tier is below P0 cannot anchor a Type B entity (Consensus) — the consensus would be "emerging," not "established."

---

## 2. Meta-Path Ontology (Horizontal Dimension)

The horizontal dimension organizes the graph around **meta-paths** — 5-node templates that represent canonical reasoning chains. The graph is not a free-form network; it is a collection of instantiated meta-paths, and every entity's primary value comes from the meta-paths it participates in.

### The 5-Node Template

The canonical meta-path template has five node positions, each with a structural role:

```
[Node 1: Condition/Context] → [Node 2: Modifier/Bridge] → [Node 3: Core Entity] → [Node 4: Mechanism/Marker] → [Node 5: Outcome/Evaluation]
```

| Position | Role | Description | Typical Knowledge Type |
|----------|------|-------------|----------------------|
| Node 1 | Condition/Context | The situational context or precondition that frames the reasoning chain | A (Problem) or D (Concept) |
| Node 2 | Modifier/Bridge | A factor that modifies, mediates, or bridges the condition to the core entity | D (Concept) or E (Data) |
| Node 3 | Core Entity | The central entity under investigation — the subject of the probe | B (Consensus), C (Method), or D (Concept) |
| Node 4 | Mechanism/Marker | The mechanism, marker, or intermediate property that connects the core entity to the outcome | C (Method) or E (Data) |
| Node 5 | Outcome/Evaluation | The result, conclusion, or evaluation — the answer to the probe | B (Consensus) or E (Data) |

### Instantiation Rules

1. **Completeness.** Every meta-path must have all 5 nodes instantiated. If a node is unknown, it must be explicitly marked as `[UNKNOWN — GAP]` and linked to a Type A (Problem) entity. An meta-path with a silent gap (a missing node that is not marked) is a data integrity error.

2. **Relation type vocabulary.** The relation between adjacent nodes must use a relation type from the controlled vocabulary. The vocabulary is domain-specific but must include, at minimum: `modifies`, `is_modified_by`, `has_marker`, `is_marker_of`, `produces`, `is_produced_by`, `predicts`, `is_predicted_by`, `causes`, `is_caused_by`, `evaluates`, `is_evaluated_by`.

3. **Directionality.** Each meta-path has a canonical direction (Node 1 → Node 5). The reverse direction must also be traversable (see Bidirectional Link Integrity below), but the canonical direction defines the "forward probe" and the reverse defines the "backward probe."

4. **Meta-path identity.** A meta-path is identified by its node-type sequence, not by its specific entity values. Two instantiations with the same node-type sequence but different entities are instances of the same meta-path pattern. This allows the graph to recognize recurring structural patterns and use them for link prediction.

5. **Nesting.** A node in one meta-path may be the core entity (Node 3) of another meta-path. This creates a nested reasoning structure. The graph must track these nestings to avoid circular reasoning (a meta-path that eventually references itself).

### Link Integrity Checks

For every meta-path instantiation, the following integrity checks are enforced:

- **Forward traversal.** Starting from Node 1, following the canonical relations, the traversal must reach Node 5 without dead ends. A dead end (a node with no outgoing relation of the required type) is a blocking gap.

- **Backward traversal.** Starting from Node 5, following the inverse relations, the traversal must reach Node 1. A dead end in the backward direction is a bidirectional link failure (Meta-Rule 6 violation).

- **Evidence coverage.** Every relation in the meta-path must have at least one citation link (`originates_from` or `supported_by`). A relation with no citation is an unsupported claim and must be flagged.

- **Evidence tier minimum.** The minimum evidence tier across all relations in the meta-path determines the meta-path's confidence level. If any relation is backed only by P2 evidence, the entire meta-path's answer is capped at P2 confidence, regardless of how strong other segments are.

- **Path closure.** If Node 5 references a threshold or standard that originates from a specific source, the citation path from Node 5 to that source must be fully closed (no missing intermediate citation links). This is the citation-network path closure rule, enforced at the meta-path level.

---

## 3. Evidence Hierarchy Ontology (Credibility Dimension)

The credibility dimension assigns every factual claim in the graph an evidence tier that reflects the strength and reliability of its supporting evidence. The tier is attached at intake (when the fact first enters the graph) and is re-evaluated when new evidence emerges.

### Evidence Tiers

| Tier | Label | Description | Typical Source Types | Confidence Level |
|------|-------|-------------|---------------------|-----------------|
| **T0** | Guideline/Consensus | Practice guidelines, systematic reviews, meta-analyses, expert consensus statements | ESC guidelines, ACC/AHA guidelines, Cochrane reviews | High — suitable for deterministic reasoning anchors |
| **P0** | Landmark RCT | Pivotal randomized controlled trial that establishes a threshold, standard, or paradigm | FAME 1, PREVENT, ISCHEMIA | High — suitable for threshold and standard-of-care claims |
| **P1** | RCT/Cohort | Additional RCTs, prospective cohort studies, large registries | PECTUS-AI, VULNERABLE, CLIMA study | Moderate — suitable for directional claims, not for threshold anchoring |
| **P2** | Observational/Expert | Retrospective studies, case series, case-control studies, expert opinion, conference abstracts | Single-center retrospective analyses, editorial commentary | Low — suitable for hypothesis generation only; cannot anchor reasoning |

### Tier Assignment Rules

1. **Threshold anchoring.** A Type E entity (threshold/metric) that serves as a reasoning anchor (appears in a Node 4 or Node 5 position of a meta-path) must be backed by T0 or P0 evidence. If only P1/P2 evidence exists, the entity is labeled "emerging threshold" and cannot be used as a deterministic anchor.

2. **Consensus backing.** A Type B entity (Consensus) must be backed by T0 evidence (guideline/consensus statement) or by a convergence of ≥2 P0 sources. A single P0 source alone establishes a "provisional consensus" that requires either guideline confirmation or independent replication to be upgraded to full consensus.

3. **Challenge handling.** If a `challenged_by` citation is attached to an entity, the entity's effective evidence tier is downgraded by one level for reasoning purposes, regardless of its nominal tier. A T0 entity with a `challenged_by` link is treated as P0 for confidence calculation. This prevents a contested guideline recommendation from being treated with the same confidence as an unchallenged one.

4. **Multi-source entities.** When an entity is supported by multiple sources at different tiers, the *highest* tier determines the entity's nominal tier, but the *distribution* of tiers is recorded. An entity backed by 1× P0 and 5× P2 is nominally P0 but has a weaker evidence base than an entity backed by 3× P0 and 0× P2. The distribution is used for consensus-formation tracking.

### Reverse Reconstruction Trigger Conditions

Reverse reconstruction is a mandatory recall cycle triggered when the graph contains a claim that is widely cited but whose originating source is missing. The conditions are:

| Condition | Trigger | Required Action |
|-----------|---------|-----------------|
| **Missing origin.** A Type E threshold is present in the graph with a `supported_by` link but no `originates_from` link | The threshold's origin is unknown — the graph cannot trace it to its establishing source | Mandatory recall cycle: search for the landmark trial/study that established the threshold. Add `originates_from` link. Example: FFR ≤ 0.80 without FAME 1 link triggers reconstruction. |
| **Broken citation chain.** A citation path from an entity to its ultimate source has a missing intermediate link (A → X → ??? → Y, where Y is the origin) | The citation chain is incomplete — the graph cannot verify the provenance | Mandatory recall cycle: trace the intermediate citations. Close the chain. |
| **Unsupported consensus.** A Type B entity (Consensus) has no T0 or P0 backing — only P1 or P2 | The consensus is not properly grounded — it may be conventional wisdom rather than evidence-based | Mandatory recall cycle: search for the guideline or landmark trial that should exist. If none exists, downgrade the entity from "Consensus" to "Emerging." |
| **Orphaned challenge.** A `challenged_by` citation exists but the challenging source is not in the graph | The challenge cannot be evaluated — the graph does not know what the challenge says | Mandatory recall cycle: retrieve the challenging source, add it to the graph, and evaluate the challenge's credibility. |

### GRADE Integration

For domains that use the GRADE (Grading of Recommendations Assessment, Development and Evaluation) framework, the KG-PDG evidence tiers map to GRADE quality levels:

| KG-PDG Tier | GRADE Quality | Interpretation |
|-------------|---------------|----------------|
| T0 | High | Further research is very unlikely to change confidence in the estimate of effect |
| P0 | High–Moderate | Further research may have an important impact on confidence |
| P1 | Moderate | Further research is likely to have an important impact on confidence |
| P2 | Low–Very Low | Further research is very likely to have an important impact; estimate is uncertain |

This mapping is a parameter of the domain adaptation, not a fixed property of the ontology. In domains that do not use GRADE (e.g., engineering, law), the evidence tiers are used directly without GRADE mapping.

---

## 4. Citation Network Ontology (Provenance Dimension)

The provenance dimension links every entity and relation in the graph to its source(s) through a citation network with five controlled relation types. The citation network is what makes the graph *auditable*: any claim can be traced to its origin, its supporting evidence, and its challenges.

### Citation Relation Types

| Relation Type | Label | Direction | Meaning | Required Attributes |
|---------------|-------|-----------|---------|---------------------|
| `originates_from` | Origin | Entity → Source | The entity/relation was first established in this source. Every factual entity must have exactly one `originates_from` link (its primary origin). | Source ID, page/section reference, timestamp of publication |
| `supported_by` | Support | Entity → Source | The entity/relation is corroborated by this source. An entity may have multiple `supported_by` links. | Source ID, agreement level (full / partial), timestamp |
| `challenged_by` | Challenge | Entity → Source | The entity/relation is disputed, contradicted, or qualified by this source. Presence of this link marks the entity as "contested." | Source ID, challenge type (contradiction / qualification / refutation), timestamp |
| `supersedes` | Supersession | Old Entity → New Entity | The new entity replaces the old entity. Used for concept evolution and threshold updates. Forms a chain, never a cycle. | Timestamp of supersession, reason, superseding source ID |
| `reviewed_in` | Synthesis | Entity → Source | The entity/relation is integrated or synthesized in this review/meta-analysis source. | Source ID, synthesis type (systematic review / narrative review / meta-analysis), timestamp |

### Path Closure Rules

Citation paths must be **closed** — every entity must be traceable to its ultimate evidentiary root through a complete chain of citation links.

1. **Primary origin closure.** Every factual entity must have an `originates_from` link to a source. If the source itself is a review that synthesizes earlier work, the graph must contain the path: Entity → (originates_from) → Review → (cites) → Original Study. The path must be closed — no missing links.

2. **Support chain closure.** If an entity has a `supported_by` link to Source X, and Source X's support depends on Source Y (e.g., X is a meta-analysis that includes Y), the graph should contain the path: Entity → (supported_by) → X → (includes) → Y. This allows the graph to distinguish between independent support (X and Y are separate studies) and dependent support (X is a meta-analysis that includes Y).

3. **Challenge chain closure.** If an entity has a `challenged_by` link to Source X, the graph must contain enough information about Source X to evaluate the challenge: what specifically is challenged, on what evidence, and whether the challenge has itself been challenged. A `challenged_by` link without context is an open citation path.

4. **Supersession chain integrity.** `supersedes` links must form a linear chain: Entity_v1 → (superseded by) → Entity_v2 → (superseded by) → Entity_v3. Cycles are data errors. Branches (one entity superseded by two independent entities) are allowed only when the entity was split (granularity adaptation), in which case both successors must link back via "succeeds."

### Bidirectional Link Requirements

The citation network must be traversable in both directions, just like the meta-path network:

- For every `originates_from` link (Entity → Source), the source must have a reverse link: Source → (is_origin_of) → Entity.
- For every `supported_by` link (Entity → Source), the source must have a reverse link: Source → (supports) → Entity.
- For every `challenged_by` link (Entity → Source), the source must have a reverse link: Source → (challenges) → Entity.
- For every `supersedes` link (Old → New), the new entity must have a reverse link: New → (supersedes) → Old (or "succeeds").
- For every `reviewed_in` link (Entity → Source), the source must have a reverse link: Source → (reviews) → Entity.

This bidirectionality is verified in Phase 4 (verification) of every probe cycle. A citation network with broken reverse links produces asymmetric provenance: the graph can trace from entity to source but not from source to entity, making it impossible to answer "What entities does this source establish?" — a critical question for literature-based reasoning.

---

## 5. Cross-Dimensional Validation Rules

The four dimensions are not independent in practice — they interact through validation rules that constrain how entities can be combined. These rules are enforced at write time (when an entity or relation is added to the graph) and re-checked during the coverage audit.

### Rule 5.1: Knowledge Type → Evidence Tier

The knowledge type of an entity determines which evidence tiers are acceptable:

| Knowledge Type | Minimum Acceptable Tier | Rationale |
|----------------|------------------------|-----------|
| B (Consensus) | T0 or convergence of ≥2× P0 | Consensus must be guideline-backed or multi-landmark-trial-backed |
| E (Data/Metric, anchoring) | P0 | A threshold used as a reasoning anchor must come from a landmark trial |
| E (Data/Metric, non-anchoring) | P1 | Non-anchoring metrics (e.g., a reported hazard ratio in a specific cohort) may be P1 |
| C (Method/Technique) | P1 | A method must be validated in at least a cohort study; P2 (single case series) is insufficient |
| D (Concept/Term) | P2 | A concept definition may originate from an expert opinion or editorial, but must be supported by at least one empirical source |
| A (Problem/Question) | N/A | A problem does not require evidence — it requires a meta-path association |

**Violation handling:** If an entity is written with an evidence tier below its type's minimum, the write is rejected. The entity must either be upgraded to a higher tier (by finding better evidence) or its type must be downgraded (e.g., a "Consensus" entity with only P2 evidence becomes an "Emerging" entity, which is a sub-type of Type D).

### Rule 5.2: Meta-Path → Evidence Coverage

Every relation in a meta-path must have at least one citation link. Additionally, the meta-path's overall confidence is determined by its weakest link:

- If all relations in the meta-path have T0/P0 evidence, the meta-path confidence is **High**.
- If any relation has only P1 evidence (and none have P2), the meta-path confidence is **Moderate**.
- If any relation has P2 evidence, the meta-path confidence is **Low** — the answer is a hypothesis, not a conclusion.

**Violation handling:** A meta-path with a relation that has no citation link is considered "broken" — it cannot be used to answer probes until the citation is added. This is enforced in the coverage audit (Phase 3, Step 3.5).

### Rule 5.3: Evidence Tier → Citation Path Closure

The higher the evidence tier, the more stringent the citation path closure requirement:

- **T0 entities:** The `originates_from` source must be fully traced. If the T0 source is a guideline, the guideline's own evidence base (the trials it cites) must be represented in the graph, at least as P0/P1 entities with `reviewed_in` links to the guideline.
- **P0 entities:** The `originates_from` source (the landmark trial) must be in the graph with its key results (Type E entities) linked via `produces`.
- **P1 entities:** The `originates_from` source must be in the graph. Citation path closure to secondary sources is recommended but not mandatory.
- **P2 entities:** The `originates_from` source must be in the graph. No further closure is required.

**Violation handling:** A T0 or P0 entity with an unclosed citation path triggers reverse reconstruction (see Section 3). The entity is marked "provenance incomplete" and cannot be used as a reasoning anchor until the path is closed.

### Rule 5.4: Concept Evolution → Supersession Chain Integrity

When a Type D entity (Concept) is split or revised (granularity adaptation, Meta-Rule 4), the supersession chain must be maintained:

- The old entity must have a `supersedes` link to each new entity.
- Each new entity must have a reverse `succeeds` link to the old entity.
- The old entity's status must be changed to "superseded" or "split."
- All meta-paths that referenced the old entity must be updated to reference the appropriate new entity.
- All citation links on the old entity must be evaluated: `originates_from` links may need to be transferred to the new entity that actually originated from the splitting source; `supported_by` and `challenged_by` links must be redistributed based on which new entity each source actually supports or challenges.

**Violation handling:** A supersession event that leaves orphaned meta-paths (meta-paths still referencing the superseded entity) or broken citation links is a data integrity error. The coverage audit detects these by checking that all meta-path nodes have status "active" and all citation links point to active entities.

### Rule 5.5: Citation Challenge → Knowledge Type Downgrade

When a `challenged_by` citation is attached to an entity:

- If the entity is Type B (Consensus), its status shifts to "contested." A Type A (Problem) entity is spawned, representing the open question created by the challenge. The meta-paths that use this entity as a reasoning anchor must be re-evaluated.
- If the entity is Type E (Data/Metric), its effective evidence tier is downgraded by one level for confidence calculation purposes (see Section 3, Challenge handling).
- If the entity is Type D (Concept), the challenge may trigger a granularity review — is the concept overloaded, such that different sources are challenging different sub-concepts?

**Violation handling:** A `challenged_by` link that is not accompanied by the required status change and meta-path re-evaluation is a validation error. The challenge is recorded but not propagated, which means the graph continues to use the challenged entity with full confidence — a false-confidence risk.

---

## 6. Meta-Path Patterns Observed

The 5-probe cardiovascular OCT practice revealed four recurring meta-path patterns. These patterns are not designed a priori — they emerged from the probe-driven growth process and were recognized retrospectively through coverage auditing. They are presented here as observed regularities that may generalize to other domains.

### Pattern 1: Problem → Consensus Lifecycle

```
[Open Problem (A)] → [Investigated by (C)] → [Core Entity (B/D)] → [Establishes (E)] → [Resolves Problem (A→resolved)]
```

**Description:** This pattern captures the lifecycle of a domain question from open problem to resolved consensus. An open problem (Type A) is investigated by a method (Type C), which examines a core entity (Type B or D), produces data (Type E), and the data resolves the problem (Type A status changes to "resolved").

**Observed instance:** "What is the prognostic significance of OCT-detected TCFA?" (Type A) → investigated by OCT imaging (Type C) → examining TCFA (Type D) → produces hazard ratios and LCR metrics (Type E) → resolves to "TCFA is an independent predictor of MACE" (Type A → resolved, Type B consensus established).

**Generalization condition:** This pattern appears in any domain where questions are resolved through empirical investigation. In law: an open legal question (A) is investigated by a legal test (C), examining a doctrine (D), producing a holding (E), resolving the question (A → resolved). In finance: an open market question (A) is investigated by a model (C), examining a factor (D), producing a risk/return metric (E), resolving the question.

### Pattern 2: Technique → Concept Co-evolution

```
[New Technique (C)] → [Enables detection of (D)] → [Concept refined/split (D→D₁+D₂)] → [Has differential prognosis (E)] → [Changes clinical practice (B)]
```

**Description:** This pattern captures how new measurement techniques drive concept refinement. A new technique (Type C) enables detection of a feature that was previously undistinguishable, causing a concept (Type D) to split into sub-concepts (D₁, D₂), each with different prognostic implications (Type E), ultimately changing practice (Type B).

**Observed instance:** OCT imaging (Type C) → enables detection of algorithmically-defined TCFA → TCFA concept splits into AI-TCFA and CL-TCFA (Type D → D₁ + D₂) → AI-TCFA and CL-TCFA have different prognostic implications (Type E) → updates clinical understanding of vulnerable plaque (Type B).

**Generalization condition:** This pattern appears in any domain where measurement technology advances faster than conceptual taxonomy. In materials science: a new microscopy technique enables detection of a substructure, causing an alloy class to split, each with different failure modes. In law: a new analytical framework enables distinction between previously conflated legal doctrines, each with different outcomes.

### Pattern 3: Threshold Drift

```
[Established Threshold (E, v1)] → [Challenged by new data (P1/P2)] → [Threshold revised (E, v2)] → [Supersedes v1 (supersedes link)] → [New consensus established (B)]
```

**Description:** This pattern captures how quantitative thresholds evolve. An established threshold (Type E, version 1) is challenged by newer data (P1/P2 evidence), leading to a revised threshold (Type E, version 2) that supersedes the old one, eventually establishing a new consensus (Type B).

**Observed instance:** FFR ≤ 0.75 (Type E, v1, from early pressure measurement studies) → challenged by FAME 1 trial data → threshold revised to FFR ≤ 0.80 (Type E, v2) → v2 supersedes v1 → new consensus established in guidelines (Type B, T0).

**Generalization condition:** This pattern appears in any domain with quantitative standards that are revised as evidence accumulates. In engineering: a material strength threshold is revised as new test data accumulates. In finance: a risk threshold is revised as new market data challenges the old calibration. In law: a legal standard (e.g., "reasonable doubt" thresholds in quantitative evidence) is refined through appellate decisions.

### Pattern 4: Risk Factor Stratification Symmetry

```
[Condition₁ (D)] → [Modifies (D)] → [Core Entity (B/D)] → [Has Marker (E)] → [Outcome₁ (E)]
[Condition₂ (D)] → [Modifies (D)] → [Core Entity (B/D)] → [Has Marker (E)] → [Outcome₂ (E)]
```

**Description:** This pattern captures the symmetric structure of risk factor stratification: multiple conditions (Type D) modify the same core entity, each producing a different outcome (Type E). The symmetry is structural — the meta-path shape is identical for each condition, only the condition and outcome values differ.

**Observed instance:** Diabetes modifies TCFA → has LCR marker → predicts MACE (HR=42.73). CKD modifies TCFA → has LCR marker → predicts MACE (HR=different). Inflammatory state modifies TCFA → has LCR marker → predicts MACE (HR=different). The structural symmetry allows the graph to predict that if a new condition is discovered that modifies TCFA, it should also have an LCR marker and a MACE outcome — a link prediction target.

**Generalization condition:** This pattern appears in any domain with multiple modifiers of the same core entity. In engineering: multiple environmental conditions modify the same material, each producing a different failure mode. In law: multiple fact patterns modify the same legal doctrine, each producing a different holding. In finance: multiple market regimes modify the same factor, each producing a different return profile. The symmetry is what makes link prediction effective: if the graph sees the pattern repeated, it can predict missing instances.

--- 中文 ---

# KG-PDG 本体规范

本文档提供了知识图谱探针驱动增长（KG-PDG）方法论使用的四维本体的正式规范。四个维度是正交的：图谱中的每个实体和关系在每个维度上都有一个值，值的组合决定了该知识在推理、补全和验证中如何处理。

---

## 1. 知识类型本体（纵向维度）

纵向维度将每个实体分类为五种知识类型之一。类型决定实体的深度标准（必须具有哪些属性和关系）及其触发规则（何时必须重新审视或扩展）。

| 类型 | 标签 | 描述 | 深度标准 | 触发规则 |
|------|------|------|----------|----------|
| **A** | 问题/疑问 | 领域中的开放性问题、临床问题、研究缺口或未解决的问题 | 必须有≥1关联元路径；必须链接到≥1共识（B型）或前沿实体；必须有状态字段：开放/部分解决/已解决 | 当探针揭示无法完成的元路径时触发。当关联的共识实体被替代时必须重新审视。 |
| **B** | 共识/经验 | 已建立的、广泛接受的知识——实践指南、标志性试验结果、系统综述、专家共识声明 | 必须有≥1 T0或P0证据链接；必须通过`originates_from`引用来源；必须有共识建立时间戳 | 当新的`challenged_by`引用出现时触发。如果挑战积累，状态转为"有争议"并生成A型问题实体。 |
| **C** | 方法/技术 | 领域中使用的方法、设备、分析技术或程序方法 | 必须链接到≥1能力（能做什么）和≥1局限性（不能做什么）；必须有证据-条件范围（在什么条件下验证） | 当探针需要评估方法适用性时触发。当新验证研究出现时必须重新审视。 |
| **D** | 概念/术语 | 定义的术语、概念或可能随时间演化的概念类别 | 必须有定义来源（`originates_from`）；必须通过`supersedes`链接追踪概念演化；必须有当前状态字段：活跃/被替代/已分裂 | 当探针揭示概念被过载（出现在不兼容的元路径中）时触发。可能触发粒度适配（实体分裂）。 |
| **E** | 数据/指标 | 定量指标、阈值、数据集或数值标准 | 必须有：单位、参考范围、来源试验/研究（`originates_from`）和证据层级（T0-P2） | 当探针需要定量答案时触发。当检测到阈值漂移（较新来源引用修改后的值）时必须重新审视。 |

### 类型交互规则

- 状态为"已解决"的A型实体（问题）必须链接到解决它的B型实体（共识）。
- 涉及定量标准的B型实体（共识）必须有至少一个E型实体（数据/指标）支撑。
- 产生E型数据的C型实体（方法）必须通过"produces"关系链接到该数据。
- 已分裂的D型实体（概念）必须保留到所有后继实体的`supersedes`链接，所有后继实体必须通过"succeeds"反向链接。
- 证据层级低于P0的E型实体（数据/指标）不能锚定B型实体（共识）——该共识将是"新兴"的，而非"已建立"的。

---

## 2. 元路径本体（横向维度）

横向维度围绕**元路径**组织图谱——5节点模板代表规范推理链。图谱不是自由形式的网络；它是实例化元路径的集合，每个实体的主要价值来自它参与的元路径。

### 5节点模板

规范元路径模板有五个节点位置，每个具有结构角色：

```
[节点1：条件/上下文] → [节点2：修饰/桥接] → [节点3：核心实体] → [节点4：机制/标志物] → [节点5：结局/评估]
```

| 位置 | 角色 | 描述 | 典型知识类型 |
|------|------|------|-------------|
| 节点1 | 条件/上下文 | 构成推理链框架的情境上下文或前提 | A（问题）或D（概念） |
| 节点2 | 修饰/桥接 | 修饰、中介或桥接条件到核心实体的因素 | D（概念）或E（数据） |
| 节点3 | 核心实体 | 调查的中心实体——探针的主题 | B（共识）、C（方法）或D（概念） |
| 节点4 | 机制/标志物 | 连接核心实体到结局的机制、标志物或中间属性 | C（方法）或E（数据） |
| 节点5 | 结局/评估 | 结果、结论或评估——探针的答案 | B（共识）或E（数据） |

### 实例化规则

1. **完整性。** 每个元路径必须实例化所有5个节点。如果节点未知，必须明确标记为`[UNKNOWN — GAP]`并链接到A型（问题）实体。具有静默缺口（未标记的缺失节点）的元路径是数据完整性错误。

2. **关系类型词汇。** 相邻节点之间的关系必须使用受控词汇中的关系类型。词汇是领域特定的，但必须至少包括：`modifies`、`is_modified_by`、`has_marker`、`is_marker_of`、`produces`、`is_produced_by`、`predicts`、`is_predicted_by`、`causes`、`is_caused_by`、`evaluates`、`is_evaluated_by`。

3. **方向性。** 每个元路径有规范方向（节点1 → 节点5）。反向也必须可遍历（见下文双向链接完整性），但规范方向定义"正向探针"，反向定义"反向探针"。

4. **元路径身份。** 元路径由其节点类型序列标识，而非特定实体值。两个具有相同节点类型序列但不同实体的实例化是同一元路径模式的实例。这使图谱能够识别重复的结构模式并用于链接预测。

5. **嵌套。** 一个元路径中的节点可能是另一个元路径的核心实体（节点3）。这创建了嵌套推理结构。图谱必须追踪这些嵌套以避免循环推理（最终引用自身的元路径）。

### 链接完整性检查

对于每个元路径实例化，强制执行以下完整性检查：

- **正向遍历。** 从节点1出发，沿规范关系，遍历必须到达节点5而无死端。死端（没有所需类型出站关系的节点）是阻断性缺口。

- **反向遍历。** 从节点5出发，沿逆关系，遍历必须到达节点1。反向的死端是双向链接失败（元规则6违规）。

- **证据覆盖。** 元路径中的每个关系必须有至少一个引用链接（`originates_from`或`supported_by`）。无引用的关系是不支持的声明，必须被标记。

- **证据层级最低值。** 元路径中所有关系的最低证据层级决定元路径的置信度。如果任何关系仅由P2证据支撑，整个元路径的答案被限制在P2置信度，无论其他段多强。

- **路径闭合。** 如果节点5引用了源自特定来源的阈值或标准，从节点5到该来源的引用路径必须完全闭合（无缺失的中间引用链接）。这是引用网络路径闭合规则，在元路径层面强制执行。

---

## 3. 证据层级本体（可信度维度）

可信度维度为图谱中的每个事实声明分配一个证据层级，反映其支撑证据的强度和可靠性。层级在入库时（事实首次进入图谱时）附着，并在新证据出现时重新评估。

### 证据层级

| 层级 | 标签 | 描述 | 典型来源类型 | 置信度水平 |
|------|------|------|-------------|-----------|
| **T0** | 指南/共识 | 实践指南、系统综述、荟萃分析、专家共识声明 | ESC指南、ACC/AHA指南、Cochrane综述 | 高——适合确定性推理锚点 |
| **P0** | 标志性RCT | 建立阈值、标准或范式的关键随机对照试验 | FAME 1、PREVENT、ISCHEMIA | 高——适合阈值和标准护理声明 |
| **P1** | RCT/队列 | 额外的RCT、前瞻性队列研究、大型注册研究 | PECTUS-AI、VULNERABLE、CLIMA研究 | 中——适合方向性声明，不适合阈值锚定 |
| **P2** | 观察性/专家 | 回顾性研究、病例系列、病例对照研究、专家意见、会议摘要 | 单中心回顾性分析、社论评论 | 低——仅适合假设生成；不能锚定推理 |

### 层级分配规则

1. **阈值锚定。** 作为推理锚点（出现在元路径的节点4或节点5位置）的E型实体（阈值/指标）必须有T0或P0证据支撑。如果只有P1/P2证据存在，实体被标记为"新兴阈值"，不能用作确定性锚点。

2. **共识支撑。** B型实体（共识）必须有T0证据（指南/共识声明）或≥2个P0来源的趋同支撑。单个P0来源单独建立"临时共识"，需要指南确认或独立复制才能升级为完全共识。

3. **挑战处理。** 如果`challenged_by`引用附着到实体，无论其名义层级如何，该实体在推理中的有效证据层级降一级。有`challenged_by`链接的T0实体在置信度计算中被视为P0。这防止有争议的指南推荐被以与无争议推荐相同的置信度处理。

4. **多源实体。** 当实体被不同层级的多个来源支撑时，*最高*层级决定实体的名义层级，但层级*分布*被记录。由1× P0和5× P2支撑的实体名义上是P0，但其证据基础比由3× P0和0× P2支撑的实体弱。分布用于共识形成追踪。

### 逆向重构触发条件

逆向重构是强制召回循环，当图谱包含被广泛引用但来源缺失的声明时触发。条件如下：

| 条件 | 触发 | 所需行动 |
|------|------|----------|
| **缺失来源。** E型阈值存在于图谱中有`supported_by`链接但无`originates_from`链接 | 阈值来源未知——图谱无法追溯到其建立来源 | 强制召回循环：搜索建立阈值的标志性试验/研究。添加`originates_from`链接。示例：FFR ≤ 0.80无FAME 1链接触发重构。 |
| **断裂引用链。** 从实体到其最终来源的引用路径有缺失的中间链接（A → X → ??? → Y，Y是来源） | 引用链不完整——图谱无法验证溯源 | 强制召回循环：追踪中间引用。闭合链条。 |
| **无支撑共识。** B型实体（共识）无T0或P0支撑——只有P1或P2 | 共识未被适当支撑——可能是传统认知而非证据支撑 | 强制召回循环：搜索应存在的指南或标志性试验。如果不存在，将实体从"共识"降级为"新兴"。 |
| **孤儿挑战。** `challenged_by`引用存在但挑战来源不在图谱中 | 挑战无法评估——图谱不知道挑战说了什么 | 强制召回循环：检索挑战来源，添加到图谱，评估挑战的可信度。 |

### GRADE集成

对于使用GRADE（推荐分级评估、制定与评价）框架的领域，KG-PDG证据层级映射到GRADE质量级别：

| KG-PDG层级 | GRADE质量 | 解释 |
|-----------|-----------|------|
| T0 | 高 | 进一步研究不太可能改变效应估计的置信度 |
| P0 | 高-中 | 进一步研究可能对置信度有重要影响 |
| P1 | 中 | 进一步研究可能对置信度有重要影响 |
| P2 | 低-极低 | 进一步研究极可能对置信度有重要影响；估计不确定 |

此映射是领域适配的参数，而非本体的固定属性。在不使用GRADE的领域（如工程、法律），证据层级直接使用，无需GRADE映射。

---

## 4. 引用网络本体（溯源维度）

溯源维度通过具有五种受控关系类型的引用网络，将图谱中的每个实体和关系链接到其来源。引用网络使图谱*可审计*：任何声明都可追溯到其来源、支撑证据和挑战。

### 引用关系类型

| 关系类型 | 标签 | 方向 | 含义 | 必需属性 |
|---------|------|------|------|----------|
| `originates_from` | 来源 | 实体 → 来源 | 实体/关系首次在此来源中建立。每个事实实体必须有且仅有一个`originates_from`链接（其主要来源）。 | 来源ID、页/节引用、发表时间戳 |
| `supported_by` | 支撑 | 实体 → 来源 | 实体/关系被此来源佐证。实体可以有多个`supported_by`链接。 | 来源ID、一致程度（完全/部分）、时间戳 |
| `challenged_by` | 挑战 | 实体 → 来源 | 实体/关系被此来源争议、反驳或限定。此链接的存在将实体标记为"有争议"。 | 来源ID、挑战类型（矛盾/限定/反驳）、时间戳 |
| `supersedes` | 替代 | 旧实体 → 新实体 | 新实体替代旧实体。用于概念演化和阈值更新。形成链，绝不形成环。 | 替代时间戳、原因、替代来源ID |
| `reviewed_in` | 综合 | 实体 → 来源 | 实体/关系在此综述/荟萃分析来源中被整合或综合。 | 来源ID、综合类型（系统综述/叙述性综述/荟萃分析）、时间戳 |

### 路径闭合规则

引用路径必须**闭合**——每个实体必须通过完整的引用链接链追溯到其最终证据根源。

1. **主要来源闭合。** 每个事实实体必须有`originates_from`链接到来源。如果来源本身是综述早期工作的综述，图谱必须包含路径：实体 → (originates_from) → 综述 → (cites) → 原始研究。路径必须闭合——无缺失链接。

2. **支撑链闭合。** 如果实体有到来源X的`supported_by`链接，而来源X的支撑依赖于来源Y（例如X是包含Y的荟萃分析），图谱应包含路径：实体 → (supported_by) → X → (includes) → Y。这使图谱能区分独立支撑（X和Y是独立研究）和依赖支撑（X是包含Y的荟萃分析）。

3. **挑战链闭合。** 如果实体有到来源X的`challenged_by`链接，图谱必须包含关于来源X的足够信息以评估挑战：具体挑战了什么、基于什么证据、挑战本身是否也被挑战。无上下文的`challenged_by`链接是开放引用路径。

4. **替代链完整性。** `supersedes`链接必须形成线性链：实体_v1 → (被替代) → 实体_v2 → (被替代) → 实体_v3。环是数据错误。分支（一个实体被两个独立实体替代）仅在实体被分裂（粒度适配）时允许，在这种情况下两个后继者必须通过"succeeds"反向链接。

### 双向链接要求

引用网络必须像元路径网络一样在两个方向上可遍历：

- 对于每个`originates_from`链接（实体 → 来源），来源必须有反向链接：来源 → (is_origin_of) → 实体。
- 对于每个`supported_by`链接（实体 → 来源），来源必须有反向链接：来源 → (supports) → 实体。
- 对于每个`challenged_by`链接（实体 → 来源），来源必须有反向链接：来源 → (challenges) → 实体。
- 对于每个`supersedes`链接（旧 → 新），新实体必须有反向链接：新 → (supersedes) → 旧（或"succeeds"）。
- 对于每个`reviewed_in`链接（实体 → 来源），来源必须有反向链接：来源 → (reviews) → 实体。

这种双向性在每个探针循环的阶段4（验证）中验证。反向链接断裂的引用网络产生不对称溯源：图谱可以从实体追溯到来源但不能从来源追溯到实体，使得无法回答"这个来源建立了哪些实体？"——这是基于文献推理的关键问题。

---

## 5. 跨维度验证规则

四个维度在实践中不是独立的——它们通过验证规则交互，这些规则约束实体如何组合。这些规则在写入时（实体或关系添加到图谱时）强制执行，并在覆盖度审计中重新检查。

### 规则5.1：知识类型 → 证据层级

实体的知识类型决定哪些证据层级可接受：

| 知识类型 | 最低可接受层级 | 理由 |
|---------|---------------|------|
| B（共识） | T0或≥2× P0趋同 | 共识必须有指南支撑或多标志性试验支撑 |
| E（数据/指标，锚定） | P0 | 用作推理锚点的阈值必须来自标志性试验 |
| E（数据/指标，非锚定） | P1 | 非锚定指标（如特定队列中报告的风险比）可以是P1 |
| C（方法/技术） | P1 | 方法必须至少在队列研究中验证；P2（单个病例系列）不足 |
| D（概念/术语） | P2 | 概念定义可源自专家意见或社论，但必须有至少一个经验来源支撑 |
| A（问题/疑问） | N/A | 问题不需要证据——需要元路径关联 |

**违规处理：** 如果实体以低于其类型最低要求的证据层级写入，写入被拒绝。实体必须要么升级到更高层级（通过找到更好的证据），要么其类型必须降级（例如，只有P2证据的"共识"实体变为"新兴"实体，这是D型的子类型）。

### 规则5.2：元路径 → 证据覆盖

元路径中的每个关系必须有至少一个引用链接。此外，元路径的整体置信度由其最弱链接决定：

- 如果元路径中所有关系有T0/P0证据，元路径置信度为**高**。
- 如果任何关系只有P1证据（且没有P2），元路径置信度为**中**。
- 如果任何关系有P2证据，元路径置信度为**低**——答案是假设，不是结论。

**违规处理：** 具有无引用关系的元路径被认为是"断裂的"——在引用添加之前不能用于回答探针。这在覆盖度审计（阶段3，步骤3.5）中强制执行。

### 规则5.3：证据层级 → 引用路径闭合

证据层级越高，引用路径闭合要求越严格：

- **T0实体：** `originates_from`来源必须完全追踪。如果T0来源是指南，指南自身的证据基础（它引用的试验）必须在图谱中表示，至少作为有到指南的`reviewed_in`链接的P0/P1实体。
- **P0实体：** `originates_from`来源（标志性试验）必须在图谱中，其关键结果（E型实体）通过`produces`链接。
- **P1实体：** `originates_from`来源必须在图谱中。到次要来源的引用路径闭合推荐但非强制。
- **P2实体：** `originates_from`来源必须在图谱中。不需要进一步闭合。

**违规处理：** 引用路径未闭合的T0或P0实体触发逆向重构（见第3节）。实体被标记为"溯源不完整"，在路径闭合之前不能用作推理锚点。

### 规则5.4：概念演化 → 替代链完整性

当D型实体（概念）被分裂或修订（粒度适配，元规则4）时，必须维护替代链：

- 旧实体必须有到每个新实体的`supersedes`链接。
- 每个新实体必须有到旧实体的反向`succeeds`链接。
- 旧实体的状态必须更改为"被替代"或"已分裂"。
- 所有引用旧实体的元路径必须更新为引用适当的新实体。
- 旧实体上的所有引用链接必须评估：`originates_from`链接可能需要转移到实际源自分裂来源的新实体；`supported_by`和`challenged_by`链接必须根据每个来源实际支撑或挑战哪个新实体来重新分配。

**违规处理：** 留下孤立元路径（仍引用被替代实体的元路径）或断裂引用链接的替代事件是数据完整性错误。覆盖度审计通过检查所有元路径节点状态为"活跃"且所有引用链接指向活跃实体来检测这些。

### 规则5.5：引用挑战 → 知识类型降级

当`challenged_by`引用附着到实体时：

- 如果实体是B型（共识），其状态转为"有争议"。生成A型（问题）实体，代表挑战创建的开放问题。使用此实体作为推理锚点的元路径必须重新评估。
- 如果实体是E型（数据/指标），其在置信度计算中的有效证据层级降一级（见第3节，挑战处理）。
- 如果实体是D型（概念），挑战可能触发粒度审查——概念是否被过载，使得不同来源挑战不同子概念？

**违规处理：** `challenged_by`链接未伴随必需的状态变更和元路径重新评估是验证错误。挑战被记录但未传播，这意味着图谱继续以完全置信度使用被挑战的实体——虚假置信风险。

---

## 6. 观察到的元路径模式

5探针心血管OCT实践揭示了四种重复的元路径模式。这些模式不是先验设计的——它们从探针驱动增长过程中涌现，并通过覆盖度审计回顾性识别。它们在此作为可能泛化到其他领域的观察规律呈现。

### 模式1：问题 → 共识生命周期

```
[开放问题 (A)] → [由...调查 (C)] → [核心实体 (B/D)] → [建立 (E)] → [解决问题 (A→已解决)]
```

**描述：** 此模式捕获领域问题从开放问题到已解决共识的生命周期。开放问题（A型）由方法（C型）调查，检查核心实体（B型或D型），产生数据（E型），数据解决问题（A型状态变为"已解决"）。

**观察实例：** "OCT检测到的TCFA的预后意义是什么？"（A型）→ 由OCT成像调查（C型）→ 检查TCFA（D型）→ 产生风险比和LCR指标（E型）→ 解决为"TCFA是MACE的独立预测因子"（A型→已解决，B型共识建立）。

**泛化条件：** 此模式出现在任何通过经验调查解决问题的领域。在法律中：开放法律问题（A）由法律检验（C）调查，检查学说（D），产生裁决（E），解决问题（A→已解决）。在金融中：开放市场问题（A）由模型（C）调查，检查因子（D），产生风险/收益指标（E），解决问题。

### 模式2：技术 → 概念协同演化

```
[新技术 (C)] → [能够检测 (D)] → [概念细化/分裂 (D→D₁+D₂)] → [有差异化预后 (E)] → [改变临床实践 (B)]
```

**描述：** 此模式捕获新测量技术如何驱动概念细化。新技术（C型）能够检测以前无法区分的特征，导致概念（D型）分裂为子概念（D₁、D₂），每个具有不同预后意义（E型），最终改变实践（B型）。

**观察实例：** OCT成像（C型）→ 能够检测算法定义的TCFA → TCFA概念分裂为AI-TCFA和CL-TCFA（D型→D₁+D₂）→ AI-TCFA和CL-TCFA有不同预后意义（E型）→ 更新易损斑块的临床理解（B型）。

**泛化条件：** 此模式出现在测量技术发展快于概念分类的任何领域。在材料科学中：新显微技术能够检测子结构，导致合金类别分裂，每个具有不同失效模式。在法律中：新分析框架能够区分以前混淆的法律学说，每个具有不同结果。

### 模式3：阈值漂移

```
[已建立阈值 (E, v1)] → [被新数据挑战 (P1/P2)] → [阈值修订 (E, v2)] → [替代v1 (supersedes链接)] → [新共识建立 (B)]
```

**描述：** 此模式捕获定量阈值如何演化。已建立阈值（E型，版本1）被较新数据挑战（P1/P2证据），导致修订阈值（E型，版本2）替代旧版本，最终建立新共识（B型）。

**观察实例：** FFR ≤ 0.75（E型，v1，来自早期压力测量研究）→ 被FAME 1试验数据挑战 → 阈值修订为FFR ≤ 0.80（E型，v2）→ v2替代v1 → 在指南中建立新共识（B型，T0）。

**泛化条件：** 此模式出现在任何有定量标准随证据积累而修订的领域。在工程中：材料强度阈值随新测试数据积累而修订。在金融中：风险阈值随新市场数据挑战旧校准而修订。在法律中：法律标准（如定量证据中的"合理怀疑"阈值）通过上诉判决细化。

### 模式4：风险因子分层对称性

```
[条件₁ (D)] → [修饰 (D)] → [核心实体 (B/D)] → [有标志物 (E)] → [结局₁ (E)]
[条件₂ (D)] → [修饰 (D)] → [核心实体 (B/D)] → [有标志物 (E)] → [结局₂ (E)]
```

**描述：** 此模式捕获风险因子分层的对称结构：多个条件（D型）修饰同一核心实体，每个产生不同结局（E型）。对称性是结构性的——每个条件的元路径形状相同，只有条件和结局值不同。

**观察实例：** 糖尿病修饰TCFA → 有LCR标志物 → 预测MACE（HR=42.73）。CKD修饰TCFA → 有LCR标志物 → 预测MACE（HR=不同）。炎症状态修饰TCFA → 有LCR标志物 → 预测MACE（HR=不同）。结构对称性使图谱能够预测：如果发现修饰TCFA的新条件，它也应该有LCR标志物和MACE结局——链接预测目标。

**泛化条件：** 此模式出现在任何有同一核心实体的多个修饰因子的领域。在工程中：多个环境条件修饰同一材料，每个产生不同失效模式。在法律中：多个事实模式修饰同一法律学说，每个产生不同裁决。在金融中：多个市场状态修饰同一因子，每个产生不同收益特征。对称性使链接预测有效：如果图谱看到模式重复，它可以预测缺失的实例。
