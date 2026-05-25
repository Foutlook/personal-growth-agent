## 算法设计

### 分支发现

```
1. git branch -r --list "origin/<prefix>/*"
2. 提取分支名中的日期 (YYYYMMDD 格式)
3. 按日期升序排序
4. 跳过非日期格式分支，记录 warning
```

### 迭代对比链

```
main ─────────────────────────────────────────────▶
  │
  ├─ release/20250601   ← 对比 main (基线)
  ├─ release/20250621   ← 对比 release/20250601 (增量)
  ├─ release/20250701   ← 对比 release/20250621 (增量)
  └─ release/20250715   ← 对比 release/20250701 (增量)
```

### 数据采集 (git 命令)

| 指标 | git 命令 |
|------|---------|
| 提交列表 | `git log --oneline --no-merges A..B` |
| 每人提交数/行数 | `git shortlog -sn --no-merges A..B` + `git diff --shortstat A..B` |
| 改动文件数 | `git diff --stat A..B \| tail -1` |
| commit messages | `git log --format="%s" --no-merges A..B` |
| 每提交文件数 | `git log --numstat --format="" A..B` 聚合 |

### 主要事项提取

1. 从 commit messages 提取高频关键词（去停用词）
2. 取改动量最大的 top-3 目录/文件作为热点
3. 组合为一行摘要：`关键词 + 热点目录`

### 评分逻辑

**稳定性** (基于 fixup!/revert: 占比):

| 占比 | 评分 |
|------|------|
| <5% | ★★★★★ |
| <10% | ★★★★ |
| <20% | ★★★ |
| <30% | ★★ |
| ≥30% | ★ |

**规范性** (基于 conventional commit 占比):

| 占比 | 评分 |
|------|------|
| ≥80% | ★★★★★ |
| ≥60% | ★★★★ |
| ≥40% | ★★★ |
| ≥20% | ★★ |
| <20% | ★ |

Conventional commit 格式: `^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+`

### 输出格式

```markdown
# <Project> 迭代记录

| 迭代分支 | 时段 | 主要事项 | 提交人数 | 新增行 | 删除行 | 改动文件 | 平均文件/提交 | 稳定性 | 规范性 |
|---------|------|---------|---------|-------|-------|---------|-------------|-------|-------|
| release/20250601 | 06.01 | 初始化项目骨架 | 2 | +1,200 | -50 | 35 | 8.2 | ★★★ | ★★ |

## 提交明细

### release/20250621

| 作者 | 提交数 | 新增行 | 删除行 |
|------|-------|-------|-------|
| 张三 | 12 | +1,800 | -600 |
```

### 边界处理

| 场景 | 处理 |
|------|------|
| 分支名非日期格式 | 跳过 + 输出 warning |
| 只有一个 release 分支 | 对比 main，只输出一行 |
| 无 main/master | 报错，跳过该仓库 |
| release 分支已删除 | `git branch -r` 抓不到，自然跳过 |
| 目录不是 git 仓库 | 跳过 + 输出 warning |
| --dir 下无 git 仓库 | 报错提示 |

### CLI 接口

```bash
# 单项目
python gkh.py scan-iterations --repo /path/to/project

# 多项目目录
python gkh.py scan-iterations --dir /path/to/projects

# 自定义分支前缀
python gkh.py scan-iterations --dir /path/to/projects --branch-prefix sprint

# 输出到知识库
python gkh.py scan-iterations --dir /path/to/projects --output wiki
```

### 与现有功能关系

```
gkh.py
├── init          (现有)
├── capture       (现有)
├── ingest        (现有)
├── review        (现有)
├── project       (现有 - 主观经验)
├── scan-iterations (新增 - 客观 git 数据)
├── search        (现有)
├── context       (现有)
├── read          (现有)
└── dashboard     (现有)
```
