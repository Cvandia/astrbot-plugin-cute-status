<div align="center">

# 🐾 astrbot-plugin-cute-status

_⭐ 基于 AstrBot 的可爱服务器状态卡片插件 ⭐_

<a href="https://www.python.org/downloads/">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python 3.10+" />
</a>
<a href="https://github.com/AstrBotDevs/AstrBot">
  <img src="https://img.shields.io/badge/AstrBot-4.5.0+-purple" alt="AstrBot 4.5.0+" />
</a>
<img src="https://img.shields.io/badge/render-Pillow-pink" alt="Pillow" />
<a href="https://github.com/Cvandia/astrbot-plugin-cute-status/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" />
</a>

**中文简体**

</div>

---

AstrBot 服务器状态插件，以插画和爪印进度环展示 CPU、内存、Swap、磁盘、系统信息、插件数量及运行时长。

## 📦 安装

需要 **AstrBot 4.5.0+、Python 3.10+**，Python 版本同时需满足所用 AstrBot 的要求。

在 WebUI「插件」→「从链接安装」中输入以下地址，安装后重载插件：

```text
https://github.com/Cvandia/astrbot-plugin-cute-status
```

## 🎮 指令

| 命令 | 示例 | 默认权限 |
| --- | --- | --- |
| status | `/status` | 所有人 |
| 状态 | `/状态` | 所有人 |
| 运行状态 | `/运行状态` | 所有人 |

前缀遵循 AstrBot 设置，上表以 `/` 为例。开启 `to_me` 后，群聊需发送 `@机器人 /状态`，私聊无需 @。
`only_admin` 指 AstrBot 配置中的管理员。

## 🖼️ 效果预览

<img src="docs/preview.png" width="480" alt="Cute Status 状态卡片示例（固定数据）" />

## ⚙️ 配置

在 WebUI 的插件配置面板修改，保存后重载插件。

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `nickname` | string | `AstrBot` | 卡片昵称，最多 64 字符，显示超宽时截断 |
| `only_admin` | bool | `false` | 仅允许 AstrBot 管理员查询 |
| `to_me` | bool | `false` | 群聊必须 @机器人，不支持 @ 的平台保持关闭 |
| `cooldown` | float | `10.0` | 各会话共享的查询冷却秒数，0–3600，0 关闭 |
| `disk_path` | string | `/` | 查询此路径所在文件系统，Windows 可设置 `C:\` |
| `font_path` | string | 空字符串 | 自定义字体路径，留空使用内置字体 |

路径建议使用绝对路径；相对路径以 AstrBot 进程工作目录为基准。
运行时长为 AstrBot 进程存活时间，重载插件不会重置。

> 💡 容器内显示当前环境可见的系统信息，不保证等于容器配额。绘图失败时返回文字状态；
> 图片展示取决于平台适配器，特殊符号或 Emoji 可通过自定义字体补充字形。

## 🧪 开发

在 Git 克隆的仓库目录执行：

```bash
python -m pip install -r requirements-dev.txt
python -m pre_commit install
python -m pre_commit run --all-files
python -m unittest discover -s tests -v
```

每个本地克隆安装一次提交钩子即可；自动修正后检查修改并重新 `git add`。
GitHub Actions 同步执行代码检查和测试，开发依赖不影响插件安装。

## 💝 特别鸣谢

- [Kawaii Status](https://github.com/KomoriDev/nonebot-plugin-kawaii-status)：原始功能、插画、字体与布局。
- [AstrBot](https://github.com/AstrBotDevs/AstrBot)：机器人框架。
- [Pillow](https://github.com/python-pillow/Pillow) · [psutil](https://github.com/giampaolo/psutil)：绘图与系统状态采集。

### 👥 贡献者

<a href="https://github.com/Cvandia/astrbot-plugin-cute-status/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Cvandia/astrbot-plugin-cute-status&amp;max=100" alt="contributors" />
</a>

## 🛠️ 支持

[帮助文档](https://docs.astrbot.app/) · [问题反馈](https://github.com/Cvandia/astrbot-plugin-cute-status/issues) · [更新日志](CHANGELOG.md)

代码使用 [MIT](LICENSE)；插画与字体来源见 [资源说明](assets/README.md)。
