---
name: "evidence-trust-scoring"
description: "Multi-dimensional evidence evaluation for literature: 11-level provenance taxonomy (L1-L11) + integrity metadata + 0-100 trust score with anti-fraud modifiers (retraction, predatory journals, citation cartel, self-citation, spin, sponsor-run). Invoke when grading literature quality, evaluating a paper/study, building evidence-backed knowledge graphs, or assessing whether a source can be trusted as a reasoning anchor."
---

# Evidence Trust Scoring

A two-axis model for evaluating literature evidence. It separates **what kind of source** the evidence is (provenance) from **how much the source can be trusted** (integrity), then combines both into a single 0-100 trust score.

This skill is the anti-fraud / anti-"academic cliquishness" layer that a coarse evidence-level taxonomy cannot express. Two sources with the same provenance level can receive very different trust scores: a clean double-blind trial with disclosed conflicts scores high, while a conflicted open-label trial with a negative objective endpoint and a hidden corrigendum scores low.

## When to Invoke

Invoke this skill when any of the following apply:

1. **Grading a paper or study.** You need to evaluate the quality and trustworthiness of a literature source, not just classify its design.
2. **Building an evidence-backed knowledge graph.** Every entity/claim entering the graph needs a credibility level attached at intake, not at writing time.
3. **Assessing whether a claim can anchor reasoning.** A threshold, standard of care, or decision rule must be backed by sufficiently trustworthy evidence before it can be used as a deterministic reasoning anchor.
4. **Auditing an existing evidence base.** You suspect citation fraud, self-citation abuse, predatory venues, or spin, and need a systematic way to surface red flags.
5. **Comparing competing sources.** Two studies make opposite claims; you need a principled way to decide which is more trustworthy.

Do **not** invoke this skill for simple fact lookup, or when the source's provenance alone (e.g., "it is an RCT") is sufficient for the decision at hand.

## Core Philosophy

Traditional evidence hierarchies grade the **study design** and stop there. This skill argues that design is only half the story:

> **Provenance tells you what kind of source it is. Integrity tells you whether to believe it. Both are required.**

The model is deliberately two-dimensional:

| Dimension | Question | Output |
|-----------|----------|--------|
| Provenance | What kind of source is it? | `EvidenceLevel` (L1-L11) |
| Integrity | Can it be trusted? | `SourceMetadata` signals |
| Combined | How much should we rely on it? | `TrustScore` (0-100) |

The provenance dimension is a **pure taxonomy** — it never changes based on who wrote the paper or where it was published. The integrity dimension captures everything the taxonomy cannot: conflicts, retraction, blinding, sponsor influence, spin, self-citation, citation cartels, and predatory venues.

## Axis 1: Provenance Taxonomy (EvidenceLevel L1-L11)

A pure classification of study design / source type, ordered from the most rigorous synthesis to the weakest evidence. The same level can carry very different trust scores depending on integrity.

| Level | Label | Description |
|-------|-------|-------------|
| L1 | Systematic Review | Meta-analysis / systematic review synthesizing multiple trials |
| L2 | Multicenter RCT | Randomized controlled trial across multiple centers |
| L3 | Single-Center RCT | Randomized controlled trial at a single center |
| L4 | Guideline | Practice guideline / clinical practice recommendation |
| L5 | Multicenter Cohort | Prospective/retrospective cohort across multiple centers |
| L6 | Single-Center Cohort | Cohort study at a single center |
| L7 | Consensus | Expert consensus statement |
| L8 | Textbook | Textbook / reference work |
| L9 | Narrative Review | Non-systematic narrative review |
| L10 | Case Series | Series of cases without a control group |
| L11 | Case Report | Single case report |

### Provenance rules

- A threshold or standard of care must be backed by L1-L4 evidence. If only L5+ exists, the claim is labeled "emerging" and cannot be used as a deterministic reasoning anchor.
- **Reverse reconstruction trigger:** if a widely cited threshold exists in the graph but its originating trial is missing, the provenance hierarchy is violated. This triggers a mandatory retrieval cycle to find and cite the original source.
- The taxonomy integrates with GRADE: L1-L2 map to GRADE "High," L3-L6 to "Moderate," L7-L11 to "Low/Very Low" — before integrity modifiers are applied.

## Axis 2: Integrity Metadata (SourceMetadata)

Captures the signals that determine whether a source can be believed. Each field has a default (neutral) value that applies no penalty when unknown.

| Field | Meaning | Red flag when |
|-------|---------|---------------|
| `venue_type` | Top journal / regular journal / predatory | `PREDATORY` |
| `conflicts_disclosed` | Whether COI is disclosed | `False` |
| `retraction_status` | Not retracted / retracted / partial | `RETRACTED` |
| `has_expression_of_concern` | Journal issued an EoC | `True` |
| `has_corrigendum` | Corrigendum/erratum issued | `True` |
| `sponsor_run` | Study run entirely by the sponsor (all authors are sponsor employees), conflicts disclosed | `True` |
| `blinded` | Blinded vs open-label | `False` |
| `objective_endpoint_positive` | Whether the objective endpoint was positive | `False` (spin risk) |
| `self_citation_ratio` | Author self-citation ratio in [0,1] | `> 0.3` |
| `citation_clusters_detected` | Citation-cartel clusters found | `True` |
| `publication_year` | Year of publication | old (age decay) |
| `journal_warning` | Warning-list level | `HIGH_ALERT` / `LOW_ALERT` |

### Sponsor-run governance correction

A study run entirely by the sponsor (e.g., all authors are sponsor employees) with disclosed conflicts is **not** fraudulent — the conflicts are on the table. But it still warrants a small governance correction and an independent-verification flag:

- Penalty: `-5` (small, because conflicts are disclosed)
- Flags: `sponsor_run`, `needs_independent_verification`

The correction is deliberately small. The intent is not to zero out industry-funded research (much of it is methodologically excellent) but to make the graph aware that the evidence has not yet been independently replicated.

## Axis 3: Trust Score (0-100)

`TrustScore = clamp(base_score + sum(modifiers), 0, 100)`

### Base scores by (EvidenceLevel, VenueType)

| Level | Top journal | Regular journal |
|-------|-------------|-----------------|
| L1 Systematic Review | 90 | 85 |
| L2 Multicenter RCT | 95 | 90 |
| L3 Single-Center RCT | 85 | 82 |
| L4 Guideline | 90 | 88 |
| L5 Multicenter Cohort | 82 | 80 |
| L6 Single-Center Cohort | 68 | 65 |
| L7 Consensus | — | 50 |
| L8 Textbook | — | 60 |
| L9 Narrative Review | — | 45 |
| L10 Case Series | — | 55 |
| L11 Case Report | — | 30 |

Missing combinations fall back to the regular-journal entry, then to a conservative default of 40.

### Modifiers (integrity penalties)

| Modifier | Delta | Trigger |
|----------|-------|---------|
| `RETRACTED` | -100 (hard zero) | Retraction is irreversible |
| `HIGH_ALERT` | -100 (hard zero) | Journal on high-alert warning list |
| `LOW_ALERT` | -50 | Journal on low-alert warning list |
| `UNDISCLOSED_COI` | -20 | Conflicts not disclosed |
| `EXPRESSION_OF_CONCERN` | -30 | Journal issued an EoC |
| `CORRIGENDUM` | -10 | Corrigendum issued for governance issues |
| `OPEN_LABEL` | -15 | Open-label design (subjective endpoints at risk) |
| `NEGATIVE_OBJECTIVE_ENDPOINT` | -10 | Objective endpoint negative (spin risk) |
| `SPONSOR_RUN` | -5 | Sponsor-run governance correction |
| `HIGH_SELF_CITATION` | -10 | Self-citation ratio > 0.3 |
| `CITATION_CARTEL` | -15 | Citation-cartel clusters detected |
| `AGE_DECAY` | -5 to -30 | Textbook >5y, guideline/consensus >3y, others >5y |

### Hard-zero rules

Two conditions zero out a source regardless of provenance: **retraction** and **high-alert predatory venue**. These are irreversible integrity failures. A retracted trial is not "slightly less trustworthy" — it is untrustworthy.

## Usage Workflow

### Step 1: Classify provenance

Map the source's publication type to an `EvidenceLevel`. This is a mechanical mapping (see the adapter reference in the KG-PDG repo: `src/kg_pdg/adapters/medical.py`).

### Step 2: Collect integrity signals

Gather the metadata fields. For each field, prefer the primary source (the paper's COI statement, the journal's retraction/EoC records, the funding statement). Unknown fields default to neutral (no penalty) — do not guess.

### Step 3: Compute the trust score

Apply the base score, then each modifier in order. Record the modifiers and flags so the score is **explainable** — a bare number without its modifier trail is not actionable.

### Step 4: Interpret

| Score | Interpretation |
|-------|----------------|
| 85-100 | Trustworthy anchor; safe for deterministic reasoning |
| 60-84 | Usable with caveats; note the flags |
| 40-59 | Weak; treat as directional, not deterministic |
| 0-39 | Do not anchor reasoning; investigate integrity |

### Step 5: Record the modifier trail

Always store `(score, base, modifiers, flags)` together. The flags (`sponsor_run`, `needs_independent_verification`, `retracted`, `high_alert`) are the actionable output — they tell downstream consumers what to verify next.

## Anti-Fraud Playbook

This skill is designed against the real failure modes of academic publishing:

- **Predatory / paper-mill venues:** caught by `venue_type` + `journal_warning`. High-alert venues are hard-zeroed.
- **Citation cartels:** caught by `citation_clusters_detected` (clusters of mutually citing authors). Penalty -15.
- **Self-citation abuse:** caught by `self_citation_ratio` > 0.3. Penalty -10.
- **Spin:** caught by `objective_endpoint_positive=False` while subjective endpoints are positive. Penalty -10, plus the open-label penalty if applicable.
- **Hidden conflicts:** caught by `conflicts_disclosed=False`. Penalty -20. This is the single most common integrity failure and the largest non-fatal penalty.
- **Retraction / EoC / corrigendum:** caught by the retraction and governance fields. Retraction is a hard zero.

## Domain Adaptation

The taxonomy and scoring are domain-agnostic. The `EvidenceLevel` labels are medical-flavored but map cleanly to other domains:

| Domain | L1-L2 equivalent | L4 equivalent | L7 equivalent |
|--------|------------------|---------------|---------------|
| Medicine | Systematic review / multicenter RCT | Guideline | Consensus |
| Engineering | Replicated standard test | ISO/ASTM standard | Industry consensus |
| Law | Binding precedent synthesis | Statute / SCOTUS | Appellate consensus |
| Finance | Replicated factor study | Regulatory filing | Market convention |

The integrity dimension (conflicts, retraction, sponsor-run, self-citation, cartel) applies unchanged in every domain — academic cliquishness is not a medical problem, it is a human problem.

## Reference Implementation

The reference implementation lives in the KG-PDG repo:

- `src/kg_pdg/models/evidence.py` — `EvidenceLevel` enum (L1-L11)
- `src/kg_pdg/models/source.py` — `SourceMetadata`, `VenueType`, `RetractionStatus`
- `src/kg_pdg/core/trust.py` — `TrustScorer` (base scores + modifiers + flags)
- `src/kg_pdg/adapters/medical.py` — `grade_evidence()` + `build_source_metadata()`
- `tests/test_trust.py` — full test coverage of base scores, every modifier, hard-zero rules, and real-world validation

---

--- 中文 ---

# 证据信任评分

一个用于文献证据评价的双轴模型。它把证据的**来源类型**（溯源）与**可信程度**（诚信）分离，再合并为一个 0-100 的信任评分。

本技能是粗粒度证据等级无法表达的防学术造假 / 防"学术江湖"层。两个溯源等级相同的来源可以拿到截然不同的信任分：一个披露了利益冲突的双盲试验得分高，而一个有利益冲突、开放标签、客观终点阴性且存在隐藏勘误的试验得分低。

## 何时调用

满足以下任一条件时调用本技能：

1. **评价一篇论文或研究。** 你需要评估文献来源的质量与可信度，而不只是给研究设计分类。
2. **构建有证据支撑的知识图谱。** 进入图谱的每个实体/声明都需要在入库时（而非写作时）携带可信度级别。
3. **判断某声明能否作为推理锚点。** 阈值、标准护理或决策规则在被用作确定性推理锚点之前，必须有足够可信的证据支撑。
4. **审计既有证据库。** 你怀疑存在引用造假、自引滥用、掠夺性期刊或旋转（spin），需要系统化地暴露红旗信号。
5. **比较竞争性来源。** 两项研究得出相反结论，你需要一个有原则的方法判断哪个更可信。

**不要**在简单事实查询、或仅凭来源溯源（如"它是RCT"）就足以做决定时调用本技能。

## 核心理念

传统证据层级只给**研究设计**分级就停止了。本技能认为设计只是故事的一半：

> **溯源告诉你它是什么类型的来源。诚信告诉你是否该相信它。两者缺一不可。**

模型刻意做成二维的：

| 维度 | 问题 | 输出 |
|------|------|------|
| 溯源 | 它是什么类型的来源？ | `EvidenceLevel`（L1-L11） |
| 诚信 | 它能被信任吗？ | `SourceMetadata` 信号 |
| 合并 | 我们该在多大程度上依赖它？ | `TrustScore`（0-100） |

溯源维度是**纯分类法**——它不因作者是谁或发表在哪个期刊而改变。诚信维度捕获分类法无法表达的一切：利益冲突、撤稿、盲法、赞助商影响、旋转、自引、引用小团体和掠夺性期刊。

## 轴1：溯源分类法（EvidenceLevel L1-L11）

对研究设计/来源类型的纯分类，从最严谨的综合到最弱的证据排序。同一级别可因诚信不同而携带截然不同的信任分。

| 级别 | 标签 | 描述 |
|------|------|------|
| L1 | 系统综述 | 综合多项试验的荟萃分析/系统综述 |
| L2 | 多中心RCT | 跨多中心的随机对照试验 |
| L3 | 单中心RCT | 单中心随机对照试验 |
| L4 | 指南 | 临床实践指南/推荐 |
| L5 | 多中心队列 | 跨多中心的前瞻/回顾性队列 |
| L6 | 单中心队列 | 单中心队列研究 |
| L7 | 共识 | 专家共识声明 |
| L8 | 教材 | 教科书/参考著作 |
| L9 | 叙述性综述 | 非系统性的叙述综述 |
| L10 | 病例系列 | 无对照组的系列病例 |
| L11 | 病例报告 | 单个病例报告 |

### 溯源规则

- 阈值或标准护理必须有 L1-L4 证据支撑。若只有 L5+，该声明标记为"新兴"，不能用作确定性推理锚点。
- **逆向重构触发条件：** 图谱中存在被广泛引用但其来源试验缺失的阈值时，溯源层级被违反。这触发强制检索循环以找到并引用原始来源。
- 分类法与 GRADE 集成：L1-L2 映射 GRADE"高"，L3-L6 映射"中"，L7-L11 映射"低/极低"——在应用诚信修正之前。

## 轴2：诚信元数据（SourceMetadata）

捕获决定来源是否可信的信号。每个字段都有中性默认值，未知时不施加惩罚。

| 字段 | 含义 | 红旗条件 |
|------|------|----------|
| `venue_type` | 顶刊/普通期刊/掠夺性 | `PREDATORY` |
| `conflicts_disclosed` | 是否披露利益冲突 | `False` |
| `retraction_status` | 未撤稿/已撤稿/部分撤稿 | `RETRACTED` |
| `has_expression_of_concern` | 期刊是否发布关注声明 | `True` |
| `has_corrigendum` | 是否发布勘误 | `True` |
| `sponsor_run` | 研究完全由赞助商运行（所有作者均为赞助商员工），冲突已披露 | `True` |
| `blinded` | 盲法 vs 开放标签 | `False` |
| `objective_endpoint_positive` | 客观终点是否阳性 | `False`（旋转风险） |
| `self_citation_ratio` | 作者自引比例 [0,1] | `> 0.3` |
| `citation_clusters_detected` | 是否发现引用小团体 | `True` |
| `publication_year` | 发表年份 | 过旧（时间衰减） |
| `journal_warning` | 预警名单级别 | `HIGH_ALERT` / `LOW_ALERT` |

### Sponsor-run 治理修正

完全由赞助商运行（如所有作者均为赞助商员工）且已披露冲突的研究**不是**造假——冲突摆在明面上。但它仍应受到一个小型治理修正和独立验证标记：

- 惩罚：`-5`（小，因为冲突已披露）
- 标记：`sponsor_run`、`needs_independent_verification`

修正刻意设得很小。意图不是清零产业资助的研究（其中很多方法学上非常优秀），而是让图谱意识到该证据尚未被独立复现。

## 轴3：信任评分（0-100）

`TrustScore = clamp(base_score + sum(modifiers), 0, 100)`

### 基础分（按 EvidenceLevel × VenueType）

| 级别 | 顶刊 | 普通期刊 |
|------|------|----------|
| L1 系统综述 | 90 | 85 |
| L2 多中心RCT | 95 | 90 |
| L3 单中心RCT | 85 | 82 |
| L4 指南 | 90 | 88 |
| L5 多中心队列 | 82 | 80 |
| L6 单中心队列 | 68 | 65 |
| L7 共识 | — | 50 |
| L8 教材 | — | 60 |
| L9 叙述性综述 | — | 45 |
| L10 病例系列 | — | 55 |
| L11 病例报告 | — | 30 |

缺失组合回退到普通期刊条目，再回退到保守默认值 40。

### 修正项（诚信惩罚）

| 修正 | 增量 | 触发条件 |
|------|------|----------|
| `RETRACTED` | -100（硬归零） | 撤稿不可逆 |
| `HIGH_ALERT` | -100（硬归零） | 期刊在高级预警名单 |
| `LOW_ALERT` | -50 | 期刊在低级预警名单 |
| `UNDISCLOSED_COI` | -20 | 未披露利益冲突 |
| `EXPRESSION_OF_CONCERN` | -30 | 期刊发布关注声明 |
| `CORRIGENDUM` | -10 | 因治理问题发布勘误 |
| `OPEN_LABEL` | -15 | 开放标签设计（主观终点有风险） |
| `NEGATIVE_OBJECTIVE_ENDPOINT` | -10 | 客观终点阴性（旋转风险） |
| `SPONSOR_RUN` | -5 | Sponsor-run 治理修正 |
| `HIGH_SELF_CITATION` | -10 | 自引比例 > 0.3 |
| `CITATION_CARTEL` | -15 | 检测到引用小团体 |
| `AGE_DECAY` | -5 至 -30 | 教材>5年、指南/共识>3年、其他>5年 |

### 硬归零规则

无论溯源如何，两种条件都会将来源归零：**撤稿**和**高级预警掠夺性期刊**。这些是不可逆的诚信失败。一篇被撤稿的试验不是"稍微不可信"——它就是不可信。

## 使用流程

### 第1步：分类溯源

将来源的发表类型映射到 `EvidenceLevel`。这是机械映射（参考 KG-PDG 仓库中的适配器：`src/kg_pdg/adapters/medical.py`）。

### 第2步：收集诚信信号

收集元数据字段。每个字段优先使用一手来源（论文的 COI 声明、期刊的撤稿/EoC 记录、资助声明）。未知字段默认中性（不惩罚）——不要猜测。

### 第3步：计算信任分

依次应用基础分和每个修正项。记录修正项和标记，使分数**可解释**——一个没有修正轨迹的裸数字不可操作。

### 第4步：解读

| 分数 | 解读 |
|------|------|
| 85-100 | 可信锚点；可安全用于确定性推理 |
| 60-84 | 可用但有保留；注意标记 |
| 40-59 | 弱；视为方向性而非确定性 |
| 0-39 | 不可作为推理锚点；调查诚信问题 |

### 第5步：记录修正轨迹

始终一起存储 `(score, base, modifiers, flags)`。标记（`sponsor_run`、`needs_independent_verification`、`retracted`、`high_alert`）是可操作的输出——它们告诉下游消费者下一步该验证什么。

## 防造假手册

本技能针对学术出版的真实失效模式设计：

- **掠夺性/论文工厂期刊：** 由 `venue_type` + `journal_warning` 捕获。高级预警期刊硬归零。
- **引用小团体：** 由 `citation_clusters_detected`（相互引用的作者集群）捕获。惩罚 -15。
- **自引滥用：** 由 `self_citation_ratio` > 0.3 捕获。惩罚 -10。
- **旋转（Spin）：** 由 `objective_endpoint_positive=False` 且主观终点阳性捕获。惩罚 -10，若适用再加开放标签惩罚。
- **隐藏冲突：** 由 `conflicts_disclosed=False` 捕获。惩罚 -20。这是最常见的诚信失败，也是最大的非致命惩罚。
- **撤稿/EoC/勘误：** 由撤稿与治理字段捕获。撤稿是硬归零。

## 领域适配

分类法和评分是领域无关的。`EvidenceLevel` 标签带有医学色彩，但可干净地映射到其他领域：

| 领域 | L1-L2 等价 | L4 等价 | L7 等价 |
|------|-----------|---------|---------|
| 医学 | 系统综述/多中心RCT | 指南 | 共识 |
| 工程 | 复现的标准测试 | ISO/ASTM 标准 | 行业共识 |
| 法律 | 约束性先例综合 | 法规/最高法院 | 上诉法院共识 |
| 金融 | 复现的因子研究 | 监管文件 | 市场惯例 |

诚信维度（冲突、撤稿、sponsor-run、自引、小团体）在每个领域都不变地适用——学术江湖不是医学问题，而是人类问题。

## 参考实现

参考实现位于 KG-PDG 仓库：

- `src/kg_pdg/models/evidence.py` — `EvidenceLevel` 枚举（L1-L11）
- `src/kg_pdg/models/source.py` — `SourceMetadata`、`VenueType`、`RetractionStatus`
- `src/kg_pdg/core/trust.py` — `TrustScorer`（基础分 + 修正 + 标记）
- `src/kg_pdg/adapters/medical.py` — `grade_evidence()` + `build_source_metadata()`
- `tests/test_trust.py` — 覆盖基础分、每个修正项、硬归零规则和真实世界验证的完整测试
