## Tasks

### Phase 1: 核心脚本
- [x] 在 `gkh.py` 中新增 `scan-iterations` 子命令
- [x] 实现分支发现: `git branch -r` + 日期提取 + 排序
- [x] 实现迭代对比: shortlog、diff --shortstat、commit messages
- [x] 实现主要事项提取: commit keywords + 热点目录
- [x] 实现评分逻辑: 稳定性、规范性
- [x] 实现 Markdown 表格输出: 总表 + 提交明细
- [x] 实现 --output wiki 沉淀到 `wiki/projects/<project>/iterations.md`
- [x] 处理边界情况: 非日期分支、单分支、无 main、非 git 仓库

### Phase 2: Skill 文档
- [x] 新增 `references/scan-iterations.md` 工作流参考
- [x] 更新 `SKILL.md` 意图映射表

### Phase 3: 测试
- [x] 单元测试: 分支发现、日期解析、评分计算
- [x] 集成测试: 完整扫描流程 (用临时 git 仓库)
- [x] 边界测试: 各种异常场景
