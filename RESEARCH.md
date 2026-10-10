# GitHub 类似插件调查

查阅日期：2026-10-10。通过 GitHub 公共仓库搜索（`astrbot choice`、`astrbot choose`、`astrbot 决策`、`astrbot 选择`）及项目 README／源码，找到以下相关项目。

| 项目 | 已有功能 | 与本次需求的区别 |
| --- | --- | --- |
| [darklinden/astrbot-plugin-choice](https://github.com/darklinden/astrbot-plugin-choice) | `choice`／`帮我选` 命令，空格分隔多个选项，至少两个，随机选取。 | 没有 `1d`＋`还是` 语法；所查源码没有重复选项检测及当前人格异常回复。 |
| [QCZXDTC/astrbot_plugin_binary_choice](https://github.com/QCZXDTC/astrbot_plugin_binary_choice) | 群聊自动监听“还是／或者／or”，先让 LLM 判断并提取两个选项，再随机回复；支持冷却。 | 正常问题也需要 LLM；限定二选一和群聊，未包含本次指定的前缀及重复／空项的人格回怼路由。 |
| [zsmkmojang-a11y/astrbot_plugin_decision](https://github.com/zsmkmojang-a11y/astrbot_plugin_decision) | README 描述支持“还是”多选项、等权选择、回复模板及当前模型生成原因；提供 `/抉择` 和唤醒后的自然问句。 | 支持特殊答案概率和模板；README 未描述 `1d` 前缀或无效题面采用当前人格训斥用户的功能。此项目仅核对 README。 |

本次调查没有找到同时满足指定语法、有效题面只返回选项、重复／空项通过当前人格回怼的完整实现。因此在新目录独立实现这些行为，参考了上述项目的功能思路，没有复制其代码、模板、图片或其他资源，也没有沿用它们的仓库地址作为本插件发布地址。

## 核对版本

- `astrbot-plugin-choice`：固定提交 [`fbd1eb94e6f02057ac7620428a9bd348cd430bdc`](https://github.com/darklinden/astrbot-plugin-choice/commit/fbd1eb94e6f02057ac7620428a9bd348cd430bdc)，作者 darklinden。
- `astrbot_plugin_binary_choice`：固定提交 [`ae005083062d7cd83e80b6f73bfb90dbf6e5d813`](https://github.com/QCZXDTC/astrbot_plugin_binary_choice/commit/ae005083062d7cd83e80b6f73bfb90dbf6e5d813)，插件元信息作者孤清辰。
- `astrbot_plugin_decision`：读取 GitHub Contents API 返回的 README，文件 blob SHA 为 `3cff68073d5704acbc47375d88136d225aad67e6`。

## AstrBot 接口核对

- [官方 LLM、对话及人格文档](https://docs.astrbot.app/dev/star/guides/ai.html)：当前聊天模型查询与对话管理。
- [AstrMessageEvent 接口](https://docs.astrbot.app/dev/star/resources/astr_message_event.html)：`request_llm` 的 `conversation` 参数使用该对话的人格和设置；传入非空 `contexts` 会覆盖对话，因此本插件不传独立上下文。
- [官方事件实现](https://github.com/AstrBotDevs/AstrBot/blob/fb49dfa54bb248e263f1db14cfc553b2cb0655c3/astrbot/core/platform/astr_message_event.py)：LLM 请求构建及事件停止语义。
- [官方处理流程](https://github.com/AstrBotDevs/AstrBot/blob/fb49dfa54bb248e263f1db14cfc553b2cb0655c3/astrbot/core/pipeline/process_stage/stage.py)：插件 yield 的请求交给当前 Agent 管线处理。
- [官方主 Agent 构建](https://github.com/AstrBotDevs/AstrBot/blob/fb49dfa54bb248e263f1db14cfc553b2cb0655c3/astrbot/core/astr_main_agent.py)：从绑定对话解析当前人格并追加人格提示词。
- [v4.5.7 会话 LLM 管理器](https://github.com/AstrBotDevs/AstrBot/blob/v4.5.7/astrbot/core/star/session_llm_manager.py)：核对 `should_process_llm_request` 接口存在，以遵循当前会话的 LLM 开关。

官方 master 源码快照提交为 `fb49dfa54bb248e263f1db14cfc553b2cb0655c3`，包版本为 `4.29.0-beta.1`。源码核对和模拟测试均不等同于 AstrBot、聊天平台及模型的真实联调。
