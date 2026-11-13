# CI 运行记录（mf-ai-platform）

> 这是**可核对的事实记录**，不是截图。截图需要打开 github.com 的网页，本机浏览器打不开该站点（只能访问 api.github.com），
> 因此改用 README 上的官方 CI badge（随每次运行实时更新）+ 本文件记录 run ID / 链接 / 结论。

## 最近一次运行（通过）

| 项 | 值 |
|---|---|
| 工作流 | CI（`.github/workflows/ci.yml`） |
| run ID | `43412980802` |
| 触发 | push 到 `main`（提交 `8a2adb5`） |
| 时间 | 2026-11-13T10:56:16Z |
| 结论 | **success** |
| 链接 | https://github.com/qie0403/mf-ai-platform/actions/runs/43412980802 |
| 矩阵 | Python 3.11 / 3.13 两个 job 均通过 |
| 覆盖 | `python -m pytest -q --cov=modules`，本地同版本 14 passed |

## 第一次运行（失败，已修复）

| 项 | 值 |
|---|---|
| run ID | `43412597482` |
| 时间 | 2026-11-13T10:53:23Z |
| 结论 | failure |
| 链接 | https://github.com/qie0403/mf-ai-platform/actions/runs/43412597482 |
| 真因 | 与 mag 同一个问题：裸 `pytest` 没有把仓库根目录加进 `sys.path`，`import modules` 失败；本地一直用 `venv\Scripts\python.exe -m pytest` 所以没暴露 |
| 修复 | `pytest.ini` 增加 `pythonpath = .`；CI 改用 `python -m pytest`（提交 `8a2adb5`） |

## 本地复现方式

```bash
# 必须用项目自己的 venv（全局 python 缺 PyPDF2）
venv\Scripts\python.exe -m pytest -q
```
