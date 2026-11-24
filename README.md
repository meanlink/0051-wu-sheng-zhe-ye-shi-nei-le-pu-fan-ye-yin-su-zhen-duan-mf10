# 无声折页 · 室内乐谱翻页因素诊断

比较翻页负荷里的可行动因素，验证新版分页有足够低的预计失误风险后签演出用谱。

**模拟客户**　澄池弦乐小组，六位室内乐手和两位节目谱务

**现有流程**　过去用排练笔记判断某页是不是难翻。双手占用和提醒提前量混在一起，反复尝试的同一位置被重复计，改好版后缺少演出准入依据。

**业务交接**　动作素材来自排练计时和署名校样记录。这里对识别因素和重新分页做确切验证，再把通过的版本交演出谱务。

## 一日工作剧本

1. 09:15 取出 FS-12「雨后的桥」中提琴总谱和两个已录入排练批。
2. 09:30 补录一次翻页训练和留批验证记录，核对短预告和双手占用。
3. 09:45 锁定证据，worker 独立验证基础模型和加入手位变量的模型。
4. 09:50 比较验证批 log loss，检查手位是否提供额外信息。
5. 10:10 把原来双手占用的翻页点移至空拍，重新估计失误风险。
6. 10:25 改谱员再试翻三次均成功，复核员为这个改版签演出使用。
7. 10:28 尝试释放仍占用双手的版本，查看风险门槛拒绝。

## 算法和演示边界

对二分类失误用确定性的梯度下降拟合带 L2 坡度惩罚的逻辑模型。预告量以 1−min(提前秒,6)/6 表示紧迫度，手位以 0/1 表示。用留出的不同排练批比较基础与全模型的对数损失，损失至少降低 0.015 才采用手位特征。新版须低于原纸谱的模型风险且风险不高于 0.45，同时提交三次连续成功试翻凭据。

小样和风险阈值用于本地谱务协作，模型使用匿名合成演示事件，无法替代人工演出彩排。

## 快速启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

- 前端浏览器地址为 `http://127.0.0.1:18445`。
- FastAPI 文档地址为 `http://127.0.0.1:19445/docs`。
- PostgreSQL 本地端口为 `17945`。后端与后台 worker 共用数据库事务和 Redis 健康探测。
- 开发 HTML、CSS、ES modules 后运行 `docker compose up -d --build frontend`。Python 代码修改后运行 `docker compose up -d --build backend worker`。
- `SEED_DEMO` 控制自动填充。可改三项宿主端口、`DEMO_PASSWORD`、`JWT_SECRET`、`POSTGRES_PASSWORD`。持久卷保存业务数据和队列状态。停机并保留数据使用 `docker compose down`。
- 技术栈为 Python 3.11、FastAPI、PostgreSQL 16、Redis 7、Nginx 与原生浏览器 JS。后端业务模块、SQL 迁移都在 `backend/`。界面和交互在 `frontend/`。

| 账号 | 密码 | 典型权限 |
|---|---|---|
| operator@demo.local | Demo2026! | 登记翻页事件及分页试翻方案 |
| reviewer@demo.local | Demo2026! | 冻结训练和验证证据、批准演出用谱 |
| viewer@demo.local | Demo2026! | 查阅记录和经计算的指标 |

共享角色和任务状态枚举分别位于 `backend/core.py` 的 `ROLES`、`JOB_STATES` 和 `frontend/base.js` 的 `roles`、`jobStates`。数据库检查约束与服务状态以相应 SQL 和模块为准。

许可证见 LICENSE。
