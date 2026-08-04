# KG-PDG: Knowledge Graph Probe-Driven Growth

> An Agent Skill framework that turns static knowledge graphs into living, self-growing ecosystems through probe-driven methodology.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

---

## Key Features

- **Probe-Driven Growth**: Clinical or domain questions act as "probes" that discover knowledge gaps, triggering targeted knowledge acquisition rather than bulk ingestion.
- **4-Phase Closed Loop**: A repeatable workflow — *Probe → Recall → Complete → Verify* — that iteratively enriches the graph with verified, citation-backed knowledge.
- **Four-Dimensional Ontology**: Every node and edge is typed along four orthogonal axes — *Knowledge Type × Meta-Path × Evidence Hierarchy × Citation Network* — enabling precise retrieval and conflict resolution.
- **7 Meta-Rules as Executable Constraints**: Domain governance principles are formalized as machine-checkable constraints (e.g., single-source-of-truth, evidence grading, citation provenance), enforced at every graph mutation.
- **Domain-Agnostic Core with Pluggable Adapters**: The probe engine, ontology schema, and verification pipeline are domain-neutral; swapping from cardiology to genomics, finance, or law requires only a new adapter — not a rewrite.

---

## Quick Start

### Installation

```bash
pip install kg-pdg
```

### Basic Usage

```python
from kg_pdg import ProbeEngine, KnowledgeGraph
from kg_pdg.adapters import MedicalAdapter

# 1. Load or create a knowledge graph
kg = KnowledgeGraph.from_jsonld("cardiovascular_kg.jsonld")

# 2. Attach a domain adapter (medical, financial, legal, ...)
engine = ProbeEngine(kg, adapter=MedicalAdapter())

# 3. Fire a probe — a real-world question that stress-tests the graph
probe = engine.probe(
    "What OCT findings differentiate plaque erosion from plaque rupture, "
    "and what is the recommended stenting strategy for each?"
)

# 4. The engine returns a completion report with citations
print(probe.summary())
# > Gap found: No edge linking `plaque_erosion` → `no_stent_strategy`.
# > Added 3 verified triples from 2 sources (evidence level: A).
# > 1 conflict resolved (stent vs. no-stent for erosion).

# 5. Verify the updated graph against the 7 Meta-Rules
report = engine.verify()
print(report.to_markdown())
```

---

## How It Works

KG-PDG treats a knowledge graph not as a static artifact but as a living system that grows in response to the questions asked of it. The core is a four-phase closed loop:

```
                          KG-PDG Closed-Loop Architecture
 ┌──────────────────────────────────────────────────────────────────────┐
 │                                                                      │
 │   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌─────────┐ │
 │   │  PHASE 1 │      │  PHASE 2 │      │  PHASE 3 │      │ PHASE 4 │ │
 │   │  PROBE   │ ───► │  RECALL  │ ───► │ COMPLETE │ ───► │ VERIFY  │ │
 │   └──────────┘      └──────────┘      └──────────┘      └─────────┘ │
 │        │                  │                  │                  │    │
 │   Domain question   Query existing KG   Fill gaps with     Enforce 7 │
 │   acts as a probe   along 4 dimensions  verified, cited    Meta-Rules│
 │   exposing gaps     (Type × Meta-Path   triples from       & flag    │
 │                                          literature/sources conflicts  │
 │                                                                      │
 │   ◄─────────────── Feedback loop: gaps feed the next probe ◄────────│
 └──────────────────────────────────────────────────────────────────────┘

   Four-Dimensional Ontology (applied in every phase):
   ┌─────────────────┬──────────────┬───────────────────┬──────────────────┐
   │ Knowledge Type  │  Meta-Path   │ Evidence Hierarchy│ Citation Network │
   ├─────────────────┼──────────────┼───────────────────┼──────────────────┤
   │ Fact / Rule /   │ Entity→Rel→  │ A (RCT/Meta) →    │ Source graph with│
   │ Hypothesis /    │ Entity path  │ B (Cohort) →      │ provenance, DOI, │
   │ Procedure /     │ templates    │ C (Case) →        │ and conflict     │
   │ Context         │              │ D (Expert)        │ resolution edges │
   └─────────────────┴──────────────┴───────────────────┴──────────────────┘
```

**Phase 1 — Probe**: A real-world question (e.g., a clinical query) is decomposed into sub-questions that traverse the graph along typed meta-paths.

**Phase 2 — Recall**: The engine queries the existing graph across all four dimensions. Missing edges, under-supported nodes, and citation gaps are logged as *growth targets*.

**Phase 3 — Complete**: For each growth target, the engine acquires knowledge from configured sources (literature databases, APIs, domain experts), extracts verified triples, grades the evidence, and links citations.

**Phase 4 — Verify**: The 7 Meta-Rules are applied as executable constraints. Conflicts are flagged, weak evidence is downgraded, and only rule-compliant triples are committed. The verification report feeds back into the next probe cycle.

---

## Project Structure

```
kg-pdg/
├── README.md                   # This file (bilingual EN / 中文)
├── LICENSE                     # MIT License
├── pyproject.toml              # Project metadata & dependencies
├── setup.cfg                   # Tool configuration (flake8, mypy, etc.)
│
├── kg_pdg/                     # Core package
│   ├── __init__.py
│   ├── engine.py               # ProbeEngine — orchestrates the 4-phase loop
│   ├── graph.py                # KnowledgeGraph — in-memory graph store
│   ├── probe.py                # Probe decomposition & meta-path traversal
│   ├── recall.py               # Four-dimensional recall logic
│   ├── complete.py             # Gap-completion & source acquisition
│   ├── verify.py               # 7 Meta-Rules enforcement
│   ├── ontology.py             # Four-Dimensional Ontology schema
│   ├── meta_rules.py           # Executable constraint definitions
│   └── report.py               # Probe & verification report generation
│
├── kg_pdg/adapters/            # Pluggable domain adapters
│   ├── __init__.py
│   ├── base.py                 # Abstract adapter interface
│   ├── medical.py              # Cardiovascular / OCT adapter (reference impl)
│   ├── finance.py              # Placeholder adapter
│   └── legal.py                # Placeholder adapter
│
├── kg_pdg/sources/             # Knowledge source connectors
│   ├── __init__.py
│   ├── base.py
│   ├── pubmed.py               # PubMed / biomedical literature
│   └── custom.py               # Custom CSV / JSON / API connectors
│
├── tests/                      # Test suite
│   ├── test_engine.py
│   ├── test_meta_rules.py
│   └── test_adapters.py
│
├── examples/                   # Usage examples
│   ├── cardiovascular_oct.py   # 5-round OCT probe test reproduction
│   └── custom_domain.py        # Adapting to a new domain
│
└── docs/                       # Documentation
    ├── architecture.md
    ├── meta_rules.md           # The 7 Meta-Rules in detail
    └── domain_adaptation.md
```

---

## Domain Adaptation

KG-PDG was derived from 5 rounds of medical OCT (Optical Coherence Tomography) probe tests on a cardiovascular knowledge graph, but its core is domain-agnostic. The table below illustrates how the same framework maps across domains:

| Dimension | Medical (Cardiology / OCT) | Finance | Legal | Genomics |
|---|---|---|---|---|
| **Probe example** | "OCT findings differentiating plaque erosion vs. rupture" | "Risk factors for late-stage default in SMB loans" | "Precedents for fair-use in AI training data" | "Variant-gene-disease associations for BRCA1" |
| **Knowledge Types** | Fact, Rule, Hypothesis, Procedure, Context | Fact, Rule, Hypothesis, Procedure, Context | (same — domain-neutral) | (same — domain-neutral) |
| **Meta-Paths** | `Plaque → has_subtype → TCFA → treated_by → Stent` | `Borrower → has_profile → RiskTier → defaults_at → Rate` | `Case → cites → Statute → interpreted_by → Ruling` | `Variant → affects → Gene → linked_to → Disease` |
| **Evidence Hierarchy** | A: RCT / Meta-analysis → D: Expert opinion | A: Audited data → D: Analyst estimate | A: Binding precedent → D: Dicta | A: GWAS → D: Single case report |
| **Citation Network** | DOI, PubMed ID, guideline version | SEC filing, audit report ID | Case citation, statute number | dbSNP ID, ClinVar accession |
| **Adapter needed** | `MedicalAdapter` (provided) | `FinanceAdapter` | `LegalAdapter` | `GenomicsAdapter` |
| **Source connectors** | PubMed, ClinicalTrials.gov | EDGAR, Bloomberg API | CourtListener, Westlaw | ClinVar, GWAS Catalog |

To adapt KG-PDG to a new domain, implement a single adapter class and configure source connectors — the probe engine, four-dimensional ontology, and 7 Meta-Rules work unchanged.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.

---

## Citation

If you use KG-PDG in your research or project, please cite it as follows:

```bibtex
@misc{kgpdg2026,
  title  = {KG-PDG: Knowledge Graph Probe-Driven Growth},
  author = {KG-PDG Contributors},
  year   = {2026},
  url    = {https://github.com/yuyang-rgb094/kg-pdg},
  note   = {An Agent Skill framework for self-growing knowledge graphs.}
}
```

> A full academic paper describing the probe-driven methodology and the 5-round cardiovascular OCT validation is in preparation. This section will be updated upon publication.

---

## Contact

| Channel | Handle |
|---------|--------|
| Email | yy18612255323@163.com |
| WeChat | yy1083124645 |

Feel free to reach out for collaboration, questions, or domain adapter contributions.

---
---

<!-- --- 中文 --- -->

# KG-PDG：知识图谱探针驱动增长

> 一个 Agent Skill 框架，通过探针驱动方法论将静态知识图谱转变为活态、自生长的生态系统。

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

---

## 核心特性

- **探针驱动增长**：临床或领域问题作为"探针"发现知识缺口，从而触发有针对性的知识获取，而非批量导入。
- **四阶段闭环**：可重复的工作流 —— *探针 → 召回 → 补全 → 验证* —— 逐步用经过验证、带有引用的知识丰富图谱。
- **四维本体**：每个节点和边沿四个正交维度进行类型标注 —— *知识类型 × 元路径 × 证据等级 × 引用网络* —— 实现精准检索与冲突消解。
- **7 条元规则作为可执行约束**：领域治理原则被形式化为机器可检查的约束（如单一事实来源、证据分级、引用溯源），在每次图谱变更时强制执行。
- **领域无关内核 + 可插拔适配器**：探针引擎、本体模式和验证管线均与领域无关；从心血管切换到基因组学、金融或法律只需新增适配器，无需重写。

---

## 快速开始

### 安装

```bash
pip install kg-pdg
```

### 基本用法

```python
from kg_pdg import ProbeEngine, KnowledgeGraph
from kg_pdg.adapters import MedicalAdapter

# 1. 加载或创建知识图谱
kg = KnowledgeGraph.from_jsonld("cardiovascular_kg.jsonld")

# 2. 挂载领域适配器（医疗、金融、法律……）
engine = ProbeEngine(kg, adapter=MedicalAdapter())

# 3. 发射探针 —— 一个对图谱进行压力测试的真实问题
probe = engine.probe(
    "哪些 OCT 表现可区分斑块侵蚀与斑块破裂，"
    "各自推荐的支架策略是什么？"
)

# 4. 引擎返回带有引用的补全报告
print(probe.summary())
# > 发现缺口：缺少 `plaque_erosion` → `no_stent_strategy` 的边。
# > 从 2 个来源新增 3 条已验证三元组（证据等级：A）。
# > 解决 1 个冲突（侵蚀的支架 vs. 无支架策略）。

# 5. 依据 7 条元规则验证更新后的图谱
report = engine.verify()
print(report.to_markdown())
```

---

## 工作原理

KG-PDG 不将知识图谱视为静态产物，而是视为一个根据所提问题不断生长的活态系统。其核心是一个四阶段闭环：

```
                        KG-PDG 闭环架构
 ┌──────────────────────────────────────────────────────────────────────┐
 │                                                                      │
 │   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌─────────┐ │
 │   │ 阶段一   │      │ 阶段二   │      │ 阶段三   │      │ 阶段四  │ │
 │   │  探针    │ ───► │  召回    │ ───► │  补全    │ ───► │  验证   │ │
 │   └──────────┘      └──────────┘      └──────────┘      └─────────┘ │
 │        │                  │                  │                  │    │
 │   领域问题作为      沿四维查询          用已验证、带         强制执行 7 │
 │   探针，暴露缺口    现有图谱            引用的三元组         条元规则  │
 │                                          填补缺口            并标记冲突│
 │                                          （来自文献/数据源）             │
 │                                                                      │
 │   ◄─────────────── 反馈回路：缺口驱动下一轮探针 ◄────────────────────│
 └──────────────────────────────────────────────────────────────────────┘

   四维本体（应用于每个阶段）：
   ┌─────────────────┬──────────────┬───────────────────┬──────────────────┐
   │   知识类型      │   元路径     │    证据等级       │    引用网络      │
 ├─────────────────┼──────────────┼───────────────────┼──────────────────┤
   │ 事实 / 规则 /  │ 实体→关系→   │ A（RCT/荟萃）→    │ 带溯源、DOI 和    │
   │ 假设 / 流程 /  │ 实体 路径    │ B（队列）→        │ 冲突消解边的       │
   │ 情境           │ 模板         │ C（病例）→        │ 来源图谱          │
   │                │              │ D（专家意见）     │                  │
   └─────────────────┴──────────────┴───────────────────┴──────────────────┘
```

**阶段一 — 探针**：将一个真实问题（如临床查询）分解为若干子问题，沿类型化元路径遍历图谱。

**阶段二 — 召回**：引擎沿四个维度查询现有图谱。缺失的边、支撑不足的节点和引用缺口被记录为*增长目标*。

**阶段三 — 补全**：针对每个增长目标，引擎从已配置的来源（文献数据库、API、领域专家）获取知识，提取已验证三元组，评定证据等级，并关联引用。

**阶段四 — 验证**：将 7 条元规则作为可执行约束加以应用。冲突被标记，弱证据被降级，仅符合规则的三元组被提交。验证报告反馈至下一轮探针循环。

---

## 项目结构

```
kg-pdg/
├── README.md                   # 本文件（双语 EN / 中文）
├── LICENSE                     # MIT 许可证
├── pyproject.toml              # 项目元数据与依赖
├── setup.cfg                   # 工具配置（flake8、mypy 等）
│
├── kg_pdg/                     # 核心包
│   ├── __init__.py
│   ├── engine.py               # ProbeEngine —— 编排四阶段闭环
│   ├── graph.py                # KnowledgeGraph —— 内存图谱存储
│   ├── probe.py                # 探针分解与元路径遍历
│   ├── recall.py               # 四维召回逻辑
│   ├── complete.py             # 缺口补全与来源获取
│   ├── verify.py               # 7 条元规则强制执行
│   ├── ontology.py             # 四维本体模式
│   ├── meta_rules.py           # 可执行约束定义
│   └── report.py               # 探针与验证报告生成
│
├── kg_pdg/adapters/            # 可插拔领域适配器
│   ├── __init__.py
│   ├── base.py                 # 抽象适配器接口
│   ├── medical.py              # 心血管 / OCT 适配器（参考实现）
│   ├── finance.py              # 占位适配器
│   └── legal.py                # 占位适配器
│
├── kg_pdg/sources/             # 知识来源连接器
│   ├── __init__.py
│   ├── base.py
│   ├── pubmed.py               # PubMed / 生物医学文献
│   └── custom.py               # 自定义 CSV / JSON / API 连接器
│
├── tests/                      # 测试套件
│   ├── test_engine.py
│   ├── test_meta_rules.py
│   └── test_adapters.py
│
├── examples/                   # 使用示例
│   ├── cardiovascular_oct.py   # 5 轮 OCT 探针测试复现
│   └── custom_domain.py        # 适配到新领域
│
└── docs/                       # 文档
    ├── architecture.md
    ├── meta_rules.md           # 7 条元规则详解
    └── domain_adaptation.md
```

---

## 领域适配

KG-PDG 源自对心血管知识图谱进行的 5 轮医学 OCT（光学相干断层扫描）探针测试，但其内核与领域无关。下表展示同一框架如何跨领域映射：

| 维度 | 医学（心血管 / OCT） | 金融 | 法律 | 基因组学 |
|---|---|---|---|---|
| **探针示例** | "区分斑块侵蚀与破裂的 OCT 表现" | "中小企业贷款晚期违约的风险因素" | "AI 训练数据合理使用的判例" | "BRCA1 的变异-基因-疾病关联" |
| **知识类型** | 事实、规则、假设、流程、情境 | 事实、规则、假设、流程、情境 | （相同 —— 领域无关） | （相同 —— 领域无关） |
| **元路径** | `斑块 → has_subtype → TCFA → treated_by → 支架` | `借款人 → has_profile → 风险等级 → defaults_at → 利率` | `案件 → cites → 法条 → interpreted_by → 裁决` | `变异 → affects → 基因 → linked_to → 疾病` |
| **证据等级** | A：RCT/荟萃分析 → D：专家意见 | A：审计数据 → D：分析师估计 | A：约束性判例 → D：附带意见 | A：GWAS → D：单例报告 |
| **引用网络** | DOI、PubMed ID、指南版本 | SEC 文件、审计报告编号 | 案件引用、法条编号 | dbSNP ID、ClinVar 登录号 |
| **所需适配器** | `MedicalAdapter`（已提供） | `FinanceAdapter` | `LegalAdapter` | `GenomicsAdapter` |
| **来源连接器** | PubMed、ClinicalTrials.gov | EDGAR、Bloomberg API | CourtListener、Westlaw | ClinVar、GWAS Catalog |

要将 KG-PDG 适配到新领域，只需实现一个适配器类并配置来源连接器 —— 探针引擎、四维本体和 7 条元规则无需修改即可运行。

---

## 许可证

本项目基于 **MIT 许可证** 授权。完整文本见 [LICENSE](LICENSE)。

---

## 引用

如果您在研究或项目中使用 KG-PDG，请按以下方式引用：

```bibtex
@misc{kgpdg2026,
  title  = {KG-PDG: Knowledge Graph Probe-Driven Growth},
  author = {KG-PDG Contributors},
  year   = {2026},
  url    = {https://github.com/yuyang-rgb094/kg-pdg},
  note   = {An Agent Skill framework for self-growing knowledge graphs.}
}
```

> 描述探针驱动方法论及 5 轮心血管 OCT 验证的完整学术论文正在撰写中。本文将在论文发表后更新此部分。

---

## 联系方式

| 渠道 | 账号 |
|------|------|
| 邮箱 | yy18612255323@163.com |
| 微信 | yy1083124645 |

欢迎联系交流合作、提问或贡献领域适配器。
