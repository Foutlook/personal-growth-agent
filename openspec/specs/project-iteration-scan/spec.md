# project-iteration-scan

扫描指定目录下多个项目的 git 仓库，提取 release 分支迭代记录，生成结构化 Markdown 表格。

## 触发条件

用户说："扫描项目迭代记录"、"看看各项目的迭代情况"、"生成迭代报告"、"scan iterations"。

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| --repo | 否 | - | 单个项目路径 |
| --dir | 否 | - | 多项目扫描目录 |
| --branch-prefix | 否 | release | 分支名前缀 |
| --output | 否 | stdout | 输出目标: stdout 或 wiki |

--repo 和 --dir 二选一。

## 输出

1. **stdout**: Markdown 表格直接输出
2. **wiki**: 写入 `wiki/projects/<project>/iterations.md`

## 数据来源

纯本地 git，不调用远程 API。

## 约束

- 分支名必须包含 YYYYMMDD 日期格式，否则跳过
- 首个分支对比 main/master，后续对比前一个分支
- 仓库无 main/master 时跳过该项目
- 非 git 目录自动跳过
