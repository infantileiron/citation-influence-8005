# 砚林文献 · 引文影响传播

为14人论文编辑组锁定引文网络，分开核对PageRank传播概率与HITS枢纽/权威结构，再由编辑批准归档。

## 工作场景

上游 `yanlin_citations_202611.json` 为48篇具名模拟文献与160条引用。编辑组原用表格按被引次数排序，常漏掉悬空节点回流、混用来源权重、把Hub与Authority混为一谈。本工程替代口径登记、研究锁定、算法计算与复核；下游站内索引编辑消费批准结果和CSV。排名仅描述所给网络结构，不衡量论文质量，不声称因果。

六实体：CitationDataset原始网络、CitationPolicy回流口径、InfluenceStudy锁定研究、InfluenceRun运行、CitationReview编辑复核、Report归档报告。六领域页为引文图谱、文献来源、回流口径、锁定与运行、双向排序、编辑复核；另有登录页。图谱和结果页复用CitationNetwork、InfluenceSummary与RankComparison。

## 快速启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18230 ，API http://localhost:19230/docs ，PostgreSQL17730。恰好frontend/backend/worker/db/redis五服务；健康检查与依赖健康门禁齐全，Nginx反代/api。命名卷保存数据库、Redis及共享结果。清理 `docker compose down -v --remove-orphans`。

| 角色 / 账号 | 主要页面 | 权限 / 典型动作 |
|---|---|---|
| admin@yanlin.test / 引文复核编辑 | 全部六页 | 读写、批准/退回、审计 |
| analyst@yanlin.test / 文献网络分析员 | 来源、口径、研究、结果、复核 | 导入、配置、运行、提审、生成批准报告 |
| viewer@yanlin.test / 索引阅览员 | 六页只读 | 查看、下载已批准CSV |

统一演示密码 `Citation2026!`。PBKDF2密码、JWT HS256、角色依赖、持久actor审计、全局错误恢复；最多10个排队/运行任务。默认密钥与账号仅本地演示，部署需改环境配置。

## 一天的编辑剧本

1. 09:00 导入yanlin_citations_202611.json，核查48文献、160引用。
2. 09:05 确认边为“引用者→被引者”，重复/未知/自引边拒绝。
3. 09:10 登记d=0.85、均匀回流；专题版本可用YL01:3、YL02:1个性化权重。
4. 09:15 创建研究，锁定文献、边、归一化权重、阈值和迭代上限并计算SHA256。
5. 09:20 提交Redis，由独立Python worker计算PageRank与HITS，结果落PostgreSQL及共享JSON。
6. 09:25 点击孤立YL48查看其悬空回流，分别读三种排序与收敛证据。
7. 09:30 分析员提审，编辑检查概率和、L2范数、非唯一与未收敛提示。
8. 09:40 批准后归档，阅览员下载含快照哈希、所有分数、原始边与来源账本的CSV。

## 网络输入与锁定

JSON含nodes:[{id,title,year,area}]、edges:[[citing,cited]]。ID为1—30位字母数字下划线连字符，标题1—120字；year为1900—2100整数，area1—30字。1—200文献、最多2000边；JSON文本最多350000字符。拒绝空网络、重复ID、重复边、自引和未知端点。网络边无权重，不做隐式去重，不做时间衰减。

空个性化对象{}表示全节点均匀。非空权重对象未列节点为0，数值须有限非负≤1e9且总和正，后端归一化。d在(0,1)，容差[1e-14,1e-3]，最多2000轮；默认1e-10/1000轮。个性化用于PageRank跳转和悬空回流，HITS不使用它。

研究存完整不可变快照：nodes/edges/个性化/参数/源文件与方向。worker仅读该快照；数据集后来重命名不改变已有研究。规范JSON SHA256绑定完整口径，结果和CSV保留。接口未提供修改网络或既有口径/快照的方法。

## PageRank

边从引用者i指向被引者j。每轮 x'_j=(1−d)p_j+d×[Σ有出边i→j x_i/outdegree_i + dangling_mass×p_j]；浮点计算后归一概率和1。初始x=p，L1差值小于tol才标记converged，history记录每轮概率和、残差与悬空质量。达到上限不伪称收敛。孤立节点参与回流与跳转；非空个性化允许零权重，因此某些不可达节点可为0。

## 来源账本

每篇文献的PageRank按锁定研究分解为互斥四桶：跳转(1−d)p、直接引用(1−d)d·Ep、多跳传播d²(E²x+DM·Ep)、悬空回流d·DM·p（(Ev)_j=Σ_{i→j} v_i/out_i，DM为悬空质量）。收敛点上四桶之和恰等于该文献概率；未收敛或重归一化产生的差额单列对账差，不并入任何桶。循环引用质量按跳数归入唯一桶，不重复计入；经回路返回自身的质量单独标注。主要来源按边流量d·x_i/out_i逐条对账（求和=直接+多跳），路径追查展示前5条二跳路径，更深层并入多跳合计。零权重文献的跳转与悬空回流为0；跨弱连通分量无引用传播，分量间影响仅来自跳转与悬空回流。GET /runs/{id}/ledger 由已存运行结果即时计算，不改动已存排名；新生成的归档报告CSV附同一账本，历史报告保持原样。

## HITS

A_ij=1表示i引用j；a←Aᵀh后L2归一，h←Aa后L2归一，初始两向量均为1/√n。残差为两次向量L2变化之和；达到tol标收敛，否则保留未收敛。Hub是指向高Authority的文献，Authority是被高Hub引用的文献。二者不是概率，和不必为1，不能与PageRank数值直接比较大小。

NumPy SVD检测最高奇异值重数（绝对1e-12或相对1e-10容差）。最高方向非唯一时明确警告，当前方向为全正均匀初始化选取，不声称唯一排序。空边返回零向量、degenerate=true、converged=false，不把零向量当归一排名。稳定ID确定同分展示顺序。

## 工程与开发

| 层 | 技术 |
|---|---|
| 前端 | React18 / TypeScript5.7 / Vite6 / Nginx1.28 |
| 后端 | Python3.12 / FastAPI / psycopg3 |
| 算法 | 自实现PageRank/HITS迭代，NumPy2.2.1做范数/奇异值 |
| 异步与数据库 | Redis7.4 / 独立worker / PostgreSQL16 |

backend/src包含routes/controllers/services/models/schemas/middlewares/utils/constants/config；frontend/src含api/stores/types/components/common/hooks/pages/router/utils/constants。JSON载荷业务表与DDL位于backend/migrations；advisory lock保护首次建表。种子固定2401、48篇/160边，含两个活动弱连通分量、悬空文献和孤立YL47/YL48。自然键insert-only，重复不新增、不覆盖用户编辑。

后端环境DATABASE_URL、REDIS_URL、JWT_SECRET、SEED_DEMO、TASK_MODE、ARTIFACT_DIR；Compose端口和DB_PASSWORD见.env.example。本地开发需PG/Redis，安装backend/requirements.txt后运行uvicorn src.main:app --reload；前端npm ci && npm run dev，API需经/api反代。npm使用已测配套lock，仅改根包名。

枚举位置：backend/src/constants/enums.py(Role/RunStatus/ReviewStatus)与domain.py(方向/配额)；frontend/src/constants/enums.ts(角色/状态展示)。共享组件含PageTitle/Notice/StatusBadge及业务图谱，hooks含useSession/useResource。

已知边界：模拟网络；无真实文献抓取或作者消歧。未设时间衰减/边权/自引分析。HITS近重根可能慢收敛，须结合残差和警告。Redis出队强杀无自动重投，JSON业务载荷无多人乐观锁或迁移回滚。真实测试证据只放批次test-artifacts/gb-2401。

## License

MIT，见LICENSE。
