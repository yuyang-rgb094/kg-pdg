# Loop Engineering: From Probe-Driven Growth to Autonomous Knowledge Evolution

## Current State: Human-in-the-Loop

KG-PDG, in its current and validated form, operates as a **human-in-the-loop** system. The methodology has been proven through a 5-probe practice in the cardiovascular OCT domain, where each probe cycle required direct human intervention at four critical junctures:

1. **Probe formulation.** A human expert (or a human directing an AI agent) crafts each probe question. The quality of the probe determines the quality of the growth. A vague probe produces shallow growth; a sharp probe produces structural growth. Currently, there is no automated mechanism for generating probes that target the graph's weakest meta-paths. The human must read the coverage audit, identify the most consequential gap, and phrase it as a traversable question.

2. **Gap interpretation.** After the gap analysis runs, a human interprets the gap list. The gap list is structured, but its triage — deciding which gaps are blocking, which are partial, and which are enrichment — requires domain judgment. An automated gap triage would need to understand not just the graph structure but the *epistemic stakes*: which missing node would invalidate an entire reasoning chain versus which would merely weaken it.

3. **Literature curation.** The recall phase retrieves candidate sources, but a human selects which sources to incorporate, assigns evidence tiers, and decides how to map source content onto graph entities. Automated retrieval is feasible (and already partially implemented via database queries), but automated *curation* — deciding that paper X is a P0 landmark while paper Y is a P2 observational study — requires domain expertise that current LLMs approximate but do not reliably possess.

4. **Completion arbitration.** When multiple completion strategies are possible (e.g., should this concept be split into two entities, or kept as one with sub-types?), a human arbitrates. The graph's structural integrity depends on these decisions, and a wrong choice can introduce regressions that are expensive to detect and undo.

**What works well in the human-in-the-loop regime:** the graph grows with high signal density, every addition is justified by a probe, and the four-dimensional ontology ensures structural consistency. The 5-probe practice demonstrated a growth from 68 to 87 entities with 90.5% meta-path coverage and zero regressions — a result that would be difficult to achieve with fully automated growth at the current state of technology.

**What limits the human-in-the-loop regime:** the growth rate is bounded by human throughput. A single expert can run perhaps 1–3 probe cycles per day. For a domain with hundreds of meta-paths, this means months of dedicated effort to reach a mature base graph. The entire point of Loop Engineering is to remove this bottleneck without sacrificing the quality guarantees.

## The Mature Graph Vision

When the base knowledge graph reaches maturity — defined as ≥95% meta-path coverage across all known paths, with all T0/P0 evidence links closed and all citation paths traced to their origins — a qualitative change occurs. The graph transitions from a *passive knowledge store* to an *active reasoning substrate*. Four capabilities become possible that are impossible in an immature graph:

1. **Consensus boundary detection.** A mature graph contains both consensus entities (T0/P0-backed, unchallenged) and frontier entities (P1/P2-backed, possibly challenged). The graph can compute, for any given topic, exactly where established consensus ends and active debate begins. This boundary is not a static line — it shifts as new evidence arrives. The graph can mark it, track it, and alert when it moves. In medicine, this means the graph can answer "Is this treatment recommendation guideline-level or emerging-evidence-level?" without a human reading the guideline.

2. **Academic frontier tracking.** A mature graph, combined with automated literature monitoring (arXiv, PubMed, domain-specific preprint servers), can detect when a new paper introduces an entity or relation that the graph does not yet contain, or when a new paper challenges an existing graph entity. This converts the graph from a *snapshot* to a *live feed*. The key insight is that a mature graph provides the context needed to judge whether a new paper is significant: a paper that fills a known gap in a high-priority meta-path is significant; a paper that adds detail to an already-saturated path is less so.

3. **Automated gap discovery.** With a mature graph, link prediction models (trained on the graph's own meta-path patterns) can identify missing links with measurable confidence. A link prediction that scores high but is not in the graph is a *predicted gap* — a structural absence that the graph's own patterns suggest should be filled. This is the autonomous analogue of the human probe: instead of a human asking "What's missing here?", the graph's own topology asks the question. The human role shifts from formulating probes to *reviewing* predicted gaps and deciding which to pursue.

4. **Consensus formation observation.** A mature graph that is continuously updated can track how citation networks converge toward (or diverge from) consensus over time. When a new entity first appears, it may be supported by a single P2 source. Over months, if additional P1 and P0 sources accumulate and no `challenged_by` links appear, the entity is converging toward consensus. If `challenged_by` links appear and proliferate, the entity is contested. The graph can visualize this temporal dynamics and produce a "consensus trajectory" for any entity — a capability that is valuable for research planning, investment decisions, and regulatory foresight.

## Loop Engineering Architecture

Loop Engineering is architected as three layers, each building on the one below. The layers correspond to three levels of autonomy: the substrate is passive, the probe engine is semi-autonomous, and the consensus tracker is (in the limit) fully autonomous.

### Layer 1: Knowledge Graph Substrate

The foundational layer is the mature base knowledge graph, constructed and validated through the human-in-the-loop KG-PDG methodology. This layer has:

- **Ontology compliance.** Every entity conforms to the four-dimensional ontology (knowledge type, meta-path, evidence tier, citation relation). Non-conforming entities are rejected at write time.
- **Structural completeness.** Meta-path coverage ≥95%. All blocking gaps closed. All citation paths traced to origin. Bidirectional link integrity verified.
- **Growth history.** The graph retains a full audit trail of every probe cycle: which probe triggered which growth, which evidence was added, which citation paths were closed. This history is the training data for Layer 2's link prediction models.

The substrate is not static — it continues to grow — but its growth is now *guided* by Layers 2 and 3 rather than solely by human probes. The substrate enforces the rules; the upper layers generate the growth targets.

### Layer 2: Autonomous Probe Engine

The second layer is the probe engine, which automates Phases 1 and 2 of the KG-PDG loop. It has two modes:

- **Reactive mode.** When Layer 3 (the consensus tracker) detects a new paper, a citation-velocity anomaly, or a threshold drift, it forwards a signal to the probe engine. The probe engine converts this signal into a meta-path decomposition and runs gap analysis — exactly as a human would in Phase 1, but autonomously. The gap list is then used to generate search strategies and retrieve literature (Phase 2). The retrieved literature is graded using a learned evidence-tier classifier (trained on the graph's existing T0–P2 annotations).

- **Proactive mode.** The probe engine runs link prediction on the substrate's meta-path patterns. High-confidence predicted links that do not exist in the graph are treated as predicted gaps. Each predicted gap is converted into a probe question, and the reactive pipeline runs: meta-path decomposition, gap analysis, literature retrieval. If the literature confirms the predicted link, the gap is added to the completion queue. If the literature contradicts it, the link prediction model is updated.

The probe engine does not perform completion (Phase 3) autonomously in the current architecture. Completion requires structural decisions (entity splitting, relation type selection) that still benefit from human review. The probe engine produces a *completion proposal* — a structured recommendation of what to add and where — which a human reviews and approves, modifies, or rejects. This is the "semi-autonomous" state in the technical roadmap.

### Layer 3: Consensus Formation Tracker

The third layer monitors the dynamics of the knowledge graph over time, tracking how consensus forms, shifts, and breaks. It operates on three signals:

- **Citation velocity.** For each entity, the tracker measures the rate at which new `supported_by` and `challenged_by` links accumulate. A sudden spike in `supported_by` links suggests convergence toward consensus. A sudden spike in `challenged_by` links suggests emerging controversy. The tracker maintains a time-series of citation velocity for every entity and flags statistically significant deviations.

- **Agreement convergence.** When multiple independent sources begin to support the same entity or relation, the tracker measures the *convergence rate*: how quickly the supporting evidence accumulates relative to a baseline. Rapid convergence from independent sources is a strong consensus signal. Slow convergence with dependence on a single research group is a weak signal.

- **Paradigm shift signals.** The tracker watches for three paradigm shift precursors:
  1. **Threshold drift:** an established threshold (Type E entity) begins to be cited with modified values in newer sources, without a formal guideline update.
  2. **Concept restructuring:** a Type D entity begins to appear in meta-paths that it did not previously occupy, or begins to be used in conjunction with qualifiers ("classical," "traditional," "narrow-sense") that suggest impending subdivision.
  3. **Citation network reorganization:** the citation network around an entity shifts from a hub-and-spoke pattern (one landmark source, many dependents) to a multi-hub pattern (multiple independent sources), which often precedes a paradigm shift.

The consensus tracker does not modify the graph. It produces *observations* and *alerts* that are consumed by the probe engine (Layer 2) and by human reviewers. Its value is in making the *dynamics* of knowledge visible — not in automating the knowledge itself.

## Key Capabilities of Mature Loop Engineering

### Consensus Boundary Detection

The graph knows where established consensus ends and active debate begins.

In an immature graph, every entity is equally "settled" — there is no mechanism to distinguish a guideline-level recommendation from a single-cohort observation. In a mature graph with Loop Engineering, each entity carries a *consensus status* computed from its evidence-tier distribution, its citation-network topology, and its citation-velocity trajectory:

- **Established consensus:** T0/P0 evidence, multiple independent `supported_by` links, no `challenged_by` links, stable or increasing citation velocity.
- **Emerging consensus:** P1 evidence accumulating, `supported_by` links growing, minimal `challenged_by`, rising citation velocity.
- **Active debate:** `challenged_by` links present and growing, evidence tiers split (some P0, some P2 with contradictory findings), high citation velocity but divergent directions.
- **Frontier speculation:** P2 evidence only, single-source or few-source `supported_by`, low citation velocity, no T0/P0 backing.

The consensus boundary is the line between "emerging consensus" and "active debate." The graph can mark this boundary for any topic, sub-topic, or meta-path, and can track how the boundary moves over time. This is the single most valuable capability for decision-makers who need to know not just *what* the evidence says, but *how settled* it is.

### Academic Frontier Tracking

Automated arXiv/PubMed monitoring with citation network analysis.

The probe engine's reactive mode continuously monitors literature databases for new publications that intersect the graph's entity space. The monitoring pipeline:

1. **Entity extraction.** Each new paper is processed to extract named entities, which are matched against the graph's existing entities (fuzzy matching with human-reviewable confidence thresholds).
2. **Novelty detection.** If a paper introduces entities not in the graph, or makes claims that contradict existing graph relations, the paper is flagged as a *frontier signal*.
3. **Priority scoring.** Each frontier signal is scored by the significance of the gap it would fill. A paper that introduces a new entity into a high-priority, low-coverage meta-path scores high. A paper that adds a 10th `supported_by` link to an already-saturated entity scores low.
4. **Citation network analysis.** The paper's own citation network is analyzed: does it cite landmark sources already in the graph? Does it cite sources that *challenge* graph entities? This analysis contextualizes the paper within the graph's existing knowledge structure.

The output is a prioritized queue of frontier signals, each mapped to a specific gap in the graph, ready for the probe engine's reactive pipeline.

### Automated Gap Discovery

The graph self-identifies missing entities/relations without human probes.

The probe engine's proactive mode uses link prediction to discover gaps. The link prediction pipeline:

1. **Meta-path pattern extraction.** The graph's existing meta-paths are mined for recurring structural patterns: which node-type sequences appear frequently, which relation types co-occur, which evidence tiers are typically associated with which path segments.
2. **Embedding training.** Graph embeddings (e.g., meta-path2vec, R-GCN) are trained on the substrate. The embedding space captures structural similarity: entities that occupy similar positions in similar meta-paths are close in embedding space.
3. **Link prediction.** For every pair of entities that are *not* currently linked but whose embeddings suggest they should be (high similarity, plausible relation type), a predicted link is generated with a confidence score.
4. **Gap validation.** High-confidence predicted links are converted into probe questions and run through the reactive pipeline (literature retrieval, evidence grading). If the literature confirms the predicted link, it enters the completion queue. If not, the link prediction model is updated with the negative example.

This is the most ambitious capability of Loop Engineering. It means the graph can discover its own gaps — not because a human asked a question, but because the graph's own structure implies a connection that is not yet instantiated. The human role is reduced to reviewing predicted gaps and arbitrating completion proposals.

### Consensus Formation Observation

Tracks how citation networks converge toward consensus over time.

For every entity in the graph, the consensus tracker maintains a *consensus trajectory*: a time-series of the entity's consensus status (established / emerging / debated / frontier) computed from its evolving evidence and citation network. This trajectory reveals patterns:

- **Rapid convergence:** an entity moves from "frontier" to "established consensus" within 1–2 years, typically driven by a landmark P0 source that resolves prior uncertainty.
- **Slow convergence:** an entity moves gradually over 5–10 years, accumulating P1 evidence until a T0 synthesis (guideline, systematic review) consolidates it.
- **Stalled debate:** an entity remains in "active debate" for extended periods, with `challenged_by` links accumulating at the same rate as `supported_by` links. This often indicates a fundamental methodological disagreement that no amount of additional data will resolve without a paradigm shift.
- **Consensus reversal:** an entity that was "established" begins to accumulate `challenged_by` links, signaling that prior consensus is eroding. This is the precursor to a paradigm shift.

The consensus trajectory is the temporal dimension of the knowledge graph. It transforms the graph from a *snapshot of current knowledge* into a *movie of knowledge evolution*.

### Paradigm Shift Early Warning

Detects threshold drift, concept restructuring signals, and citation-velocity anomalies.

The consensus tracker's paradigm-shift detection operates on three precursors:

1. **Threshold drift detection.** For every Type E entity (threshold/metric), the tracker monitors newer sources for modified values. If a threshold that has been stable at 0.80 begins to appear as 0.78 or 0.82 in recent sources without a formal guideline update, this is threshold drift — a signal that the field is implicitly revising the standard before explicitly doing so.

2. **Concept restructuring detection.** For every Type D entity (concept/term), the tracker monitors its meta-path usage patterns. If a concept that previously appeared in one type of meta-path begins appearing in a different type, or begins appearing with qualifiers ("classical," "broad-sense," "narrow-sense"), this signals impending concept subdivision or redefinition.

3. **Citation-velocity anomaly detection.** For every entity, the tracker maintains a baseline citation velocity. Statistically significant deviations — sudden spikes or sudden drops — are flagged. A spike in `challenged_by` velocity on a previously consensus entity is a strong paradigm-shift signal. A drop in `supported_by` velocity on a previously active entity may indicate that the field has moved on (a "silent abandonment," which is itself a form of paradigm shift).

These early warnings do not predict paradigm shifts with certainty. They identify *where to look* — which entities, which meta-paths, which citation networks are showing signs of structural change. For a human researcher or decision-maker, this is actionable intelligence: it says "pay attention to this corner of the graph; something is changing."

## Technical Roadmap

The transition from the current human-in-the-loop state to fully autonomous Loop Engineering is planned in three phases. Each phase has a clear entry condition, a set of capabilities to develop, and a graduation criterion.

### Phase 1: Human-in-the-Loop (Current)

- **Entry condition:** None. This is the starting state.
- **Capabilities developed and validated:**
  - 4-phase probe cycle (Probe → Recall → Complete → Verify)
  - Four-dimensional ontology (knowledge type, meta-path, evidence tier, citation relation)
  - 7 meta-rules (probe-driven growth, tiered completion, evidence grading, granularity adaptation, coverage audit, bidirectional link integrity, concept evolution tracking)
  - Gap analysis, predicted-paper verification, tiered completion, backtest verification
- **Graduation criterion:** A base knowledge graph in at least one domain reaches ≥90% meta-path coverage with all T0/P0 citation paths closed and zero regressions across ≥5 probe cycles. The 5-probe cardiovascular OCT practice (68→87 entities, 90.5% coverage) has demonstrated this criterion is achievable.

### Phase 2: Semi-Autonomous (Base KG Complete)

- **Entry condition:** Phase 1 graduation criterion met. The base graph is mature enough to serve as a substrate.
- **Capabilities to develop:**
  - Layer 2 (Autonomous Probe Engine) in reactive mode: automated literature monitoring, entity extraction, frontier signal detection, priority scoring.
  - Link prediction models trained on the substrate's meta-path patterns: meta-path2vec or R-GCN embeddings, with human-reviewable confidence thresholds.
  - Automated evidence-tier classification: a classifier trained on the graph's existing T0–P2 annotations, used to pre-grade retrieved literature before human review.
  - Completion proposal generation: the probe engine produces structured completion proposals (which entities to add, which relations to create, which citation paths to close) for human review and approval.
- **Human role:** Shifts from probe formulation and gap interpretation to *completion arbitration* and *quality review*. The human reviews predicted gaps, approves or modifies completion proposals, and validates that autonomous additions do not introduce regressions.
- **Graduation criterion:** The probe engine's predicted gaps achieve ≥70% precision (of predicted gaps, ≥70% are confirmed by literature retrieval) and ≥50% recall (of gaps that a human would identify, ≥50% are independently identified by the probe engine). The evidence-tier classifier achieves ≥85% agreement with human graders.

### Phase 3: Fully Autonomous (Loop Engineering)

- **Entry condition:** Phase 2 graduation criterion met. The probe engine reliably identifies and fills gaps with human oversight.
- **Capabilities to develop:**
  - Layer 2 in proactive mode: the probe engine autonomously generates probes from link prediction, runs the full reactive pipeline, and produces completion proposals *without* a human-initiated trigger.
  - Layer 3 (Consensus Formation Tracker): full deployment of citation-velocity tracking, agreement convergence measurement, and paradigm-shift early warning.
  - Autonomous completion (Phase 3 of the loop): the system autonomously adds entities, relations, evidence, and citation links, with human oversight reduced to reviewing *flagged anomalies* (e.g., an autonomous completion that contradicts an existing entity, or a paradigm-shift alert that requires expert judgment).
  - Self-verification (Phase 4 of the loop): the system autonomously runs forward, backward, and random probe backtests, and flags any regression for human review.
- **Human role:** Shifts to *anomaly review* and *strategic direction*. The human reviews flagged anomalies (contested completions, paradigm-shift alerts, regression failures) and sets strategic priorities (which domains to expand, which meta-paths to prioritize). Day-to-day graph growth is autonomous.
- **Graduation criterion:** The system sustains autonomous graph growth for ≥30 days with ≤5% anomaly rate (≤5% of autonomous completions require human correction) and zero undetected regressions. The consensus tracker's paradigm-shift alerts achieve ≥60% precision (of alerts, ≥60% correspond to genuine consensus changes within 12 months).

## Integration with Graph Learning

Loop Engineering is deeply integrated with graph representation learning. The integration forms a feedback loop: the knowledge graph trains graph learning models, and the graph learning models discover gaps in the knowledge graph.

The integration pipeline:

1. **Meta-path patterns → graph embedding.** The graph's meta-path structure is the input to graph embedding algorithms. Meta-path2vec, which performs random walks guided by meta-path patterns, produces embeddings that capture the *structural role* of each entity: entities that occupy similar positions in similar meta-paths are close in embedding space. R-GCN (Relational Graph Convolutional Network) extends this by incorporating relation types, producing embeddings that capture not just structural similarity but relational semantics.

2. **Graph embedding → link prediction.** Once embeddings are trained, link prediction is performed by scoring candidate entity pairs. For each pair of entities that are not currently linked, the model computes a similarity score in embedding space and predicts the most likely relation type. High-scoring predictions that do not exist in the graph are *predicted gaps*.

3. **Link prediction → automated gap discovery.** Predicted gaps are the input to the probe engine's proactive mode. Each predicted gap is converted into a probe question, validated through literature retrieval, and — if confirmed — added to the completion queue. The completion, in turn, updates the graph, which retrains the embeddings, which produces new predictions. This is the **learning loop**: the graph teaches the model, the model discovers gaps, the gaps grow the graph, the grown graph teaches the model again.

4. **Negative feedback.** When a predicted gap is *not* confirmed by literature (the model predicted a link that the evidence does not support), this is a negative example. The negative example is fed back into the link prediction model, refining its embeddings. Over time, the model learns not just which links *should* exist, but which link predictions are reliable versus which are artifacts of embedding-space proximity without semantic grounding.

The key challenge in this integration is **cold start**: when the graph is small, embeddings are unreliable and link predictions are noisy. This is why Phase 1 (human-in-the-loop) must precede Phase 2 (semi-autonomous). The human-in-the-loop phase builds the substrate to a sufficient size and structural consistency that graph learning models can be trained reliably. Premature automation on a small, inconsistent graph produces noisy predictions that erode trust in the system.

## Connection to Feynman Learning Loop

Loop Engineering has a deep structural connection to the Feynman learning loop — the pedagogical principle that the best way to learn is to try to explain something, discover where your explanation breaks down, and fill the gap.

The KG-PDG 4-phase loop *is* a Feynman loop, applied to a knowledge graph instead of a human learner:

| Feynman Loop Step | KG-PDG Phase | What Happens |
|--------------------|--------------|--------------|
| Attempt to explain | Phase 1: Probe | The graph attempts to answer a question by traversing a meta-path |
| Discover the gap | Phase 1: Gap analysis | The meta-path traversal reveals missing nodes and relations |
| Study to fill the gap | Phase 2: Recall | Literature is retrieved to fill the identified gaps |
| Re-explain | Phase 3: Complete + Phase 4: Verify | The graph is completed and the probe is re-run to verify the answer |

This isomorphism has two profound implications:

### AI Self-Testing via Probe Backtest

In the Feynman loop, the learner tests their own understanding by attempting to explain. In KG-PDG, the graph tests its own completeness by attempting to answer probes. The **random probe backtest** (Phase 4, Step 4.3) is the graph-level analogue of self-testing: the graph re-answers previously-passed probes to check that new growth has not introduced regressions.

In Loop Engineering, this self-testing becomes continuous. The probe engine does not wait for a human to initiate a backtest — it continuously runs random probes against the graph, measuring whether autonomous growth maintains or degrades answer quality. A regression detected by continuous self-testing triggers an immediate alert and (in Phase 3) an automatic rollback of the offending completion.

This is **AI self-testing at the knowledge level**: not testing whether the AI can generate text, but testing whether the AI's *knowledge structure* remains coherent as it grows. It is the structural integrity guarantee that makes autonomous growth safe.

### Bidirectional AI-Human Feynman Learning

The Feynman loop in KG-PDG is bidirectional: the AI learns from humans, and humans learn from the AI.

- **AI learns from humans (Phase 1, current state):** Human-formulated probes teach the graph what questions matter. Human-curated literature teaches the graph what evidence is credible. Human-arbitrated completions teach the graph how to structure knowledge. This is the traditional direction of knowledge transfer.

- **Humans learn from AI (Phase 2–3, Loop Engineering):** The probe engine's predicted gaps teach humans *what they don't know they don't know*. A predicted gap that a human would not have identified is a blind spot made visible. The consensus tracker's paradigm-shift alerts teach humans *where the field is moving before it moves*. A threshold-drift signal that a human would not have noticed is a leading indicator made actionable.

This bidirectionality is the deepest promise of Loop Engineering. It is not merely that the graph grows autonomously — it is that the graph's autonomous growth becomes a *source of insight* for the humans who built it. The graph that was originally a student of human knowledge becomes, in maturity, a teacher that reveals the structure of human ignorance.

--- 中文 ---

# 回路工程：从探针驱动增长到自主知识演化

## 当前状态：人在回路中

KG-PDG在其当前已验证的形式中，以**人在回路中**系统运行。该方法论已通过心血管OCT领域的5探针实践得到验证，其中每个探针循环在四个关键环节需要直接人工干预：

1. **探针制定。** 人类专家（或指挥AI代理的人类）精心设计每个探针问题。探针的质量决定增长的质量。模糊的探针产生浅层增长；锐利的探针产生结构性增长。目前，没有自动化机制来生成针对图谱最弱元路径的探针。人类必须阅读覆盖度审计，识别最具影响力的缺口，并将其表述为可遍历的问题。

2. **缺口解释。** 缺口分析运行后，人类解释缺口列表。缺口列表是结构化的，但其分级——决定哪些缺口是阻断性的、哪些是部分的、哪些是增强性的——需要领域判断。自动化缺口分级不仅需要理解图谱结构，还需要理解*认知利害关系*：哪个缺失节点会使整个推理链失效，而哪个只会削弱它。

3. **文献策展。** 召回阶段检索候选来源，但人类选择纳入哪些来源、分配证据层级，并决定如何将来源内容映射到图谱实体。自动检索是可行的（且已通过数据库查询部分实现），但自动化*策展*——决定论文X是P0标志性研究而论文Y是P2观察性研究——需要当前大语言模型可以近似但不具备的领域专业知识。

4. **补全仲裁。** 当存在多种可能的补全策略时（例如，这个概念应该分裂为两个实体，还是保持为一个带子类型？），人类进行仲裁。图谱的结构完整性取决于这些决策，错误的选择可能引入检测和撤销成本高昂的回归。

**人在回路中机制下运作良好的方面：** 图谱以高信号密度增长，每次添加都有探针作为理由，四维本体确保结构一致性。5探针实践展示了从68个实体增长到87个实体、90.5%元路径覆盖率和零回归的成果——这一结果在当前技术状态下很难通过全自动化增长实现。

**人在回路中机制的限制：** 增长速率受限于人类吞吐量。单个专家每天可能运行1-3个探针循环。对于具有数百条元路径的领域，这意味着需要数月的专门努力才能达到成熟的基础图谱。回路工程的全部意义在于在不牺牲质量保证的前提下移除这一瓶颈。

## 成熟图谱愿景

当基础知识图谱达到成熟——定义为所有已知路径的元路径覆盖率≥95%，所有T0/P0证据链接闭合，所有引用路径追溯到来源——一个质变发生了。图谱从*被动知识存储*转变为*主动推理基底*。四种在未成熟图谱中不可能的能力成为可能：

1. **共识边界检测。** 成熟图谱同时包含共识实体（T0/P0支撑、无挑战）和前沿实体（P1/P2支撑、可能被挑战）。图谱可以针对任何给定主题，精确计算已建立共识在哪里结束、活跃辩论在哪里开始。这条边界不是静态的——它随着新证据的到来而移动。图谱可以标记它、追踪它，并在它移动时发出警报。在医学中，这意味着图谱可以回答"这个治疗推荐是指南级还是新兴证据级？"而无需人类阅读指南。

2. **学术前沿追踪。** 成熟图谱结合自动文献监控（arXiv、PubMed、领域特定预印本服务器），可以检测新论文何时引入了图谱尚未包含的实体或关系，或新论文何时挑战了已有图谱实体。这将图谱从*快照*转化为*实时馈送*。关键洞察是，成熟图谱提供了判断新论文是否重要的上下文：填补高优先级元路径已知缺口的论文是重要的；为已饱和路径添加细节的论文则不那么重要。

3. **自动缺口发现。** 在成熟图谱上，链接预测模型（在图谱自身的元路径模式上训练）可以以可测量的置信度识别缺失链接。高分但不在图谱中的链接预测是*预测缺口*——图谱自身模式暗示应该填充的结构性缺失。这是人类探针的自主对应物：不是人类问"这里缺什么？"，而是图谱自身的拓扑提出问题。人类角色从制定探针转变为*审查*预测缺口并决定追求哪些。

4. **共识形成观察。** 持续更新的成熟图谱可以追踪引用网络随时间如何趋向（或偏离）共识。当新实体首次出现时，它可能仅由单个P2来源支撑。数月内，如果额外的P1和P0来源积累且没有`challenged_by`链接出现，该实体正在趋向共识。如果`challenged_by`链接出现并扩散，该实体是有争议的。图谱可以可视化这种时间动态，并为任何实体生成"共识轨迹"——这一能力对研究规划、投资决策和监管前瞻都有价值。

## 回路工程架构

回路工程被架构为三层，每层建立在下层之上。各层对应三个自主级别：基底是被动的，探针引擎是半自主的，共识追踪器（在极限情况下）是完全自主的。

### 第1层：知识图谱基底

基础层是通过人在回路中KG-PDG方法论构建和验证的成熟基础知识图谱。该层具有：

- **本体合规性。** 每个实体符合四维本体（知识类型、元路径、证据层级、引用关系）。不符合的实体在写入时被拒绝。
- **结构完整性。** 元路径覆盖率≥95%。所有阻断性缺口已闭合。所有引用路径已追溯到来源。双向链接完整性已验证。
- **增长历史。** 图谱保留每个探针循环的完整审计跟踪：哪个探针触发了哪些增长、添加了哪些证据、闭合了哪些引用路径。这段历史是第2层链接预测模型的训练数据。

基底不是静态的——它继续增长——但其增长现在由第2层和第3层*引导*，而非仅由人类探针驱动。基底执行规则；上层生成增长目标。

### 第2层：自主探针引擎

第二层是探针引擎，自动化KG-PDG循环的阶段1和阶段2。它有两种模式：

- **反应模式。** 当第3层（共识追踪器）检测到新论文、引用速度异常或阈值漂移时，它向探针引擎转发信号。探针引擎将此信号转化为元路径分解并运行缺口分析——完全如人类在阶段1中所做的，但是自主的。缺口列表然后用于生成搜索策略和检索文献（阶段2）。检索到的文献使用学习的证据层级分类器（在图谱现有T0-P2标注上训练）进行分级。

- **主动模式。** 探针引擎在基底的元路径模式上运行链接预测。不存在于图谱中但高置信度的预测链接被视为预测缺口。每个预测缺口被转化为探针问题，反应管道运行：元路径分解、缺口分析、文献检索。如果文献确认预测链接，缺口被添加到补全队列。如果文献反驳它，链接预测模型被更新。

探针引擎在当前架构中不自主执行补全（阶段3）。补全需要结构性决策（实体分裂、关系类型选择），这些仍受益于人类审查。探针引擎产生一个*补全提案*——关于添加什么和添加到哪里的结构化建议——由人类审查并批准、修改或拒绝。这就是技术路线图中的"半自主"状态。

### 第3层：共识形成追踪器

第三层监控知识图谱随时间的动态，追踪共识如何形成、移动和破裂。它在三个信号上运作：

- **引用速度。** 对于每个实体，追踪器测量新`supported_by`和`challenged_by`链接积累的速率。`supported_by`链接的突然激增表明趋向共识。`challenged_by`链接的突然激增表明新兴争议。追踪器为每个实体维护引用速度的时间序列，并标记统计显著的偏差。

- **一致性趋同。** 当多个独立来源开始支撑同一实体或关系时，追踪器测量*趋同速率*：相对于基线，支撑证据积累的速度。来自独立来源的快速趋同是强共识信号。依赖单一研究组的缓慢趋同是弱信号。

- **范式转移信号。** 追踪器监视三种范式转移前兆：
  1. **阈值漂移：** 建立的阈值（E类实体）开始在较新来源中被引用为修改后的值，而没有正式的指南更新。
  2. **概念重构：** D类实体开始出现在它以前未占据的元路径中，或开始与限定词（"经典"、"传统"、"狭义"）一起使用，暗示即将到来的细分。
  3. **引用网络重组：** 实体周围的引用网络从枢纽-辐射模式（一个标志性来源，多个依赖）转变为多枢纽模式（多个独立来源），这通常先于范式转移。

共识追踪器不修改图谱。它产生*观察*和*警报*，被探针引擎（第2层）和人类审查者消费。其价值在于使知识的*动态*可见——而非自动化知识本身。

## 成熟回路工程的关键能力

### 共识边界检测

图谱知道已建立共识在哪里结束、活跃辩论在哪里开始。

在未成熟图谱中，每个实体都是同等"已定"的——没有机制区分指南级推荐和单队列观察。在具有回路工程的成熟图谱中，每个实体携带一个*共识状态*，从其证据层级分布、引用网络拓扑和引用速度轨迹计算：

- **已建立共识：** T0/P0证据，多个独立`supported_by`链接，无`challenged_by`链接，稳定或增长的引用速度。
- **新兴共识：** P1证据积累中，`supported_by`链接增长，最少`challenged_by`，引用速度上升。
- **活跃辩论：** 存在且增长的`challenged_by`链接，证据层级分裂（部分P0，部分P2有矛盾发现），高引用速度但方向分歧。
- **前沿推测：** 仅P2证据，单源或少源`supported_by`，低引用速度，无T0/P0支撑。

共识边界是"新兴共识"与"活跃辩论"之间的线。图谱可以为任何主题、子主题或元路径标记这条边界，并追踪它如何随时间移动。这是对决策者最有价值的能力——他们需要知道不仅是证据说了*什么*，而且是它*多稳定*。

### 学术前沿追踪

自动arXiv/PubMed监控与引用网络分析。

探针引擎的反应模式持续监控文献数据库中与图谱实体空间交叉的新出版物。监控管道：

1. **实体提取。** 每篇新论文被处理以提取命名实体，与图谱现有实体匹配（模糊匹配，具有人类可审查的置信度阈值）。
2. **新颖性检测。** 如果论文引入了图谱中不存在的实体，或做出了与现有图谱关系矛盾的声明，论文被标记为*前沿信号*。
3. **优先级评分。** 每个前沿信号按其将填补缺口的重要性评分。在高优先级、低覆盖元路径中引入新实体的论文得分高。在已饱和实体上添加第10个`supported_by`链接的论文得分低。
4. **引用网络分析。** 论文自身的引用网络被分析：它是否引用了图谱中已有的标志性来源？它是否引用了*挑战*图谱实体的来源？此分析将论文置于图谱现有知识结构的上下文中。

输出是一个优先排序的前沿信号队列，每个映射到图谱中的特定缺口，准备好供探针引擎的反应管道使用。

### 自动缺口发现

图谱自行识别缺失的实体/关系，无需人工探针。

探针引擎的主动模式使用链接预测来发现缺口。链接预测管道：

1. **元路径模式提取。** 图谱现有元路径被挖掘以发现重复的结构模式：哪些节点类型序列频繁出现、哪些关系类型共现、哪些证据层级通常与哪些路径段关联。
2. **嵌入训练。** 图嵌入（如meta-path2vec、R-GCN）在基底上训练。嵌入空间捕获结构相似性：在相似元路径中占据相似位置的实体在嵌入空间中相近。
3. **链接预测。** 对于每对*当前未链接*但嵌入表明应该链接的实体（高相似性、合理的关系类型），生成带有置信度分数的预测链接。
4. **缺口验证。** 高置信度的预测链接被转化为探针问题并运行反应管道（文献检索、证据分级）。如果文献确认预测链接，它进入补全队列。如果不确认，链接预测模型用负样本更新。

这是回路工程中最雄心勃勃的能力。它意味着图谱可以发现自身的缺口——不是因为人类问了一个问题，而是因为图谱自身的结构暗示了一个尚未实例化的连接。人类角色减少为审查预测缺口和仲裁补全提案。

### 共识形成观察

追踪引用网络随时间如何趋向共识。

对于图谱中的每个实体，共识追踪器维护一个*共识轨迹*：实体共识状态（已建立/新兴/辩论/前沿）的时间序列，从其演化的证据和引用网络计算。该轨迹揭示模式：

- **快速趋同：** 实体在1-2年内从"前沿"移动到"已建立共识"，通常由解决先前不确定性的标志性P0来源驱动。
- **缓慢趋同：** 实体在5-10年内逐渐移动，积累P1证据直到T0综合（指南、系统综述）巩固它。
- **停滞辩论：** 实体长期保持"活跃辩论"状态，`challenged_by`链接以与`supported_by`链接相同的速率积累。这通常表明根本性的方法论分歧，不发生范式转移则无法通过更多数据解决。
- **共识逆转：** 曾经"已建立"的实体开始积累`challenged_by`链接，信号表明先前共识正在侵蚀。这是范式转移的前兆。

共识轨迹是知识图谱的时间维度。它将图谱从*当前知识快照*转变为*知识演化电影*。

### 范式转移早期预警

检测阈值漂移、概念重构信号和引用速度异常。

共识追踪器的范式转移检测在三个前兆上运作：

1. **阈值漂移检测。** 对于每个E类实体（阈值/指标），追踪器监控较新来源中修改后的值。如果一个稳定在0.80的阈值开始在近期来源中以0.78或0.82出现而没有正式指南更新，这就是阈值漂移——信号表明该领域在正式修订标准之前正在隐式修订。

2. **概念重构检测。** 对于每个D类实体（概念/术语），追踪器监控其元路径使用模式。如果一个以前出现在一种类型元路径中的概念开始出现在不同类型中，或开始与限定词（"经典"、"广义"、"狭义"）一起使用，这信号表明即将到来的概念细分或重新定义。

3. **引用速度异常检测。** 对于每个实体，追踪器维护基线引用速度。统计显著的偏差——突然激增或突然下降——被标记。先前共识实体上`challenged_by`速度的激增是强范式转移信号。先前活跃实体上`supported_by`速度的下降可能表明该领域已转向（一种"静默放弃"，这本身就是一种范式转移形式）。

这些早期预警不能确定性地预测范式转移。它们识别*在哪里看*——哪些实体、哪些元路径、哪些引用网络显示结构变化迹象。对于人类研究者或决策者，这是可操作的情报：它说"注意图谱的这个角落；正在发生变化。"

## 技术路线图

从当前人在回路中状态到全自主回路工程的转型分三个阶段规划。每个阶段有明确的进入条件、要开发的能力集和毕业标准。

### 阶段1：人在回路中（当前）

- **进入条件：** 无。这是起始状态。
- **已开发和验证的能力：**
  - 4阶段探针循环（探针 → 召回 → 补全 → 验证）
  - 四维本体（知识类型、元路径、证据层级、引用关系）
  - 7条元规则（探针驱动增长、分层补全、证据分级、粒度适配、覆盖度审计、双向链接完整性、概念演化追踪）
  - 缺口分析、预测论文验证、分层补全、回测验证
- **毕业标准：** 至少一个领域的基础知识图谱达到≥90%元路径覆盖率，所有T0/P0引用路径闭合，跨≥5个探针循环零回归。5探针心血管OCT实践（68→87实体，90.5%覆盖率）已证明该标准可实现。

### 阶段2：半自主（基础KG完成）

- **进入条件：** 阶段1毕业标准已满足。基础图谱足够成熟，可作为基底。
- **要开发的能力：**
  - 第2层（自主探针引擎）反应模式：自动文献监控、实体提取、前沿信号检测、优先级评分。
  - 在基底元路径模式上训练的链接预测模型：meta-path2vec或R-GCN嵌入，具有人类可审查的置信度阈值。
  - 自动证据层级分类：在图谱现有T0-P2标注上训练的分类器，用于在人类审查前预分级检索文献。
  - 补全提案生成：探针引擎产生结构化补全提案（添加哪些实体、创建哪些关系、闭合哪些引用路径），供人类审查和批准。
- **人类角色：** 从探针制定和缺口解释转变为*补全仲裁*和*质量审查*。人类审查预测缺口、批准或修改补全提案、并验证自主添加不引入回归。
- **毕业标准：** 探针引擎的预测缺口达到≥70%精确率（预测缺口中≥70%被文献检索确认）和≥50%召回率（人类会识别的缺口中≥50%被探针引擎独立识别）。证据层级分类器达到与人类分级者≥85%的一致率。

### 阶段3：全自主（回路工程）

- **进入条件：** 阶段2毕业标准已满足。探针引擎在人类监督下可靠地识别和填补缺口。
- **要开发的能力：**
  - 第2层主动模式：探针引擎从链接预测自主生成探针，运行完整反应管道，并产生补全提案，*无需*人工触发。
  - 第3层（共识形成追踪器）：全面部署引用速度追踪、一致性趋同测量和范式转移早期预警。
  - 自主补全（循环阶段3）：系统自主添加实体、关系、证据和引用链接，人类监督减少为审查*标记的异常*（如与现有实体矛盾的自主补全，或需要专家判断的范式转移警报）。
  - 自验证（循环阶段4）：系统自主运行正向、反向和随机探针回测，并标记任何回归供人类审查。
- **人类角色：** 转向*异常审查*和*战略方向*。人类审查标记的异常（有争议的补全、范式转移警报、回归失败）并设定战略优先级（扩展哪些领域、优先哪些元路径）。日常图谱增长是自主的。
- **毕业标准：** 系统维持自主图谱增长≥30天，异常率≤5%（≤5%的自主补全需要人工修正）且零未检测回归。共识追踪器的范式转移警报达到≥60%精确率（警报中≥60%在12个月内对应真实的共识变化）。

## 与图学习的集成

回路工程与图表示学习深度集成。集成形成一个反馈回路：知识图谱训练图学习模型，图学习模型发现知识图谱中的缺口。

集成管道：

1. **元路径模式 → 图嵌入。** 图谱的元路径结构是图嵌入算法的输入。Meta-path2vec通过元路径模式引导的随机游走，产生捕获每个实体*结构角色*的嵌入：在相似元路径中占据相似位置的实体在嵌入空间中相近。R-GCN（关系图卷积网络）通过纳入关系类型扩展了这一点，产生不仅捕获结构相似性而且捕获关系语义的嵌入。

2. **图嵌入 → 链接预测。** 嵌入训练完成后，通过对候选实体对评分执行链接预测。对于每对当前未链接的实体，模型计算嵌入空间中的相似度分数并预测最可能的关系类型。不存在于图谱中的高分预测是*预测缺口*。

3. **链接预测 → 自动缺口发现。** 预测缺口是探针引擎主动模式的输入。每个预测缺口被转化为探针问题，通过文献检索验证，如果确认则添加到补全队列。补全反过来更新图谱，重新训练嵌入，产生新的预测。这是**学习回路**：图谱教模型，模型发现缺口，缺口增长图谱，增长后的图谱再教模型。

4. **负反馈。** 当预测缺口*未*被文献确认时（模型预测了证据不支持的链接），这是负样本。负样本被反馈到链接预测模型，精炼其嵌入。随时间推移，模型不仅学习哪些链接*应该*存在，还学习哪些链接预测是可靠的，哪些是嵌入空间接近性但没有语义基础的人工产物。

此集成中的关键挑战是**冷启动**：当图谱较小时，嵌入不可靠，链接预测有噪声。这就是为什么阶段1（人在回路中）必须先于阶段2（半自主）。人在回路中阶段将基底构建到足够的大小和结构一致性，使图学习模型可以可靠训练。在小型、不一致的图谱上过早自动化会产生噪声预测，侵蚀对系统的信任。

## 与费曼学习回路的联系

回路工程与费曼学习回路有深层的结构联系——费曼学习回路是教育学原则，即最好的学习方式是尝试解释某事，发现你的解释在哪里崩溃，然后填补缺口。

KG-PDG的4阶段循环*就是*费曼回路，应用于知识图谱而非人类学习者：

| 费曼回路步骤 | KG-PDG阶段 | 发生了什么 |
|-------------|-----------|-----------|
| 尝试解释 | 阶段1：探针 | 图谱通过遍历元路径尝试回答问题 |
| 发现缺口 | 阶段1：缺口分析 | 元路径遍历揭示缺失的节点和关系 |
| 学习填补缺口 | 阶段2：召回 | 检索文献以填补识别的缺口 |
| 重新解释 | 阶段3：补全 + 阶段4：验证 | 图谱被补全，探针被重新运行以验证答案 |

这种同构有两个深刻含义：

### AI通过探针回测自测试

在费曼回路中，学习者通过尝试解释来测试自己的理解。在KG-PDG中，图谱通过尝试回答探针来测试自身的完整性。**随机探针回测**（阶段4，步骤4.3）是图谱级别的自测试对应物：图谱重新回答先前通过的探针，检查新增长是否引入了回归。

在回路工程中，这种自测试变为持续的。探针引擎不等待人类发起回测——它持续对图谱运行随机探针，测量自主增长是否维持或降低答案质量。持续自测试检测到的回归触发即时警报，并（在阶段3中）自动回滚有问题的补全。

这是**知识层面的AI自测试**：不是测试AI能否生成文本，而是测试AI的*知识结构*在增长时是否保持连贯。这是使自主增长安全的结构完整性保证。

### 双向AI-人类费曼学习

KG-PDG中的费曼回路是双向的：AI从人类学习，人类从AI学习。

- **AI从人类学习（阶段1，当前状态）：** 人类制定的探针教会图谱什么问题重要。人类策展的文献教会图谱什么证据可信。人类仲裁的补全教会图谱如何结构化知识。这是知识传递的传统方向。

- **人类从AI学习（阶段2-3，回路工程）：** 探针引擎的预测缺口教会人类*他们不知道自己不知道什么*。人类不会识别的预测缺口是被可视化的盲区。共识追踪器的范式转移警报教会人类*领域向哪里移动，在它移动之前*。人类不会注意到的阈值漂移信号是被赋予行动性的领先指标。

这种双向性是回路工程最深层的承诺。不仅仅是图谱自主增长——而是图谱的自主增长成为构建它的人类*洞察的来源*。原本是人类知识学生的图谱，在成熟时，成为揭示人类无知结构的老师。
