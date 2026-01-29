# 部署指南

本文档介绍如何配置自动部署到远程 Linux 服务器。

## GitHub Actions 自动部署

### 配置步骤

#### 1. 生成 SSH 密钥对

在本地机器上生成 SSH 密钥对（如果没有的话）：

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

#### 2. 配置服务器

将公钥添加到服务器的 `authorized_keys`：

```bash
# 复制公钥内容
cat ~/.ssh/github_actions_deploy.pub

# SSH 登录服务器，将公钥添加到 authorized_keys
ssh user@your-server
mkdir -p ~/.ssh
echo "公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 3. 配置 GitHub Secrets

在 GitHub 仓库中设置以下 Secrets（Settings → Secrets and variables → Actions → New repository secret）：

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `SERVER_HOST` | 服务器地址 | `192.168.1.100` 或 `example.com` |
| `SERVER_USER` | SSH 用户名 | `root` 或 `ubuntu` |
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | 整个私钥文件内容 |
| `SSH_PORT` | SSH 端口（可选） | `22`（默认） |
| `SERVER_PATH` | 服务器上项目路径 | `/opt/telegram-bot` |

**添加 SSH_PRIVATE_KEY 的步骤：**

```bash
# 查看私钥内容
cat ~/.ssh/github_actions_deploy
```

复制输出内容（包括 `-----BEGIN` 和 `-----END` 行），粘贴到 GitHub Secret 中。

#### 4. 服务器首次设置

SSH 登录服务器，执行以下初始化：

```bash
# 安装 uv (如果没有)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆代码仓库
cd /opt
git clone <your-repo-url> telegram-bot
cd telegram-bot

# 配置环境变量
cp .env.example .env
nano .env  # 填入实际的配置值

# 安装依赖
uv sync

# 启动服务
nohup uv run python -m bot > bot.log 2>&1 &
```

## 手动部署

你也可以在服务器上手动执行部署：

```bash
cd /opt/telegram-bot
./scripts/deploy.sh
```

## 查看日志

```bash
# 查看实时日志
tail -f bot.log

# 查看最近的日志
tail -n 50 bot.log
```

## 管理服务

```bash
# 查看进程
ps aux | grep "python -m bot"

# 停止服务
pkill -f "python -m bot"

# 重启服务
pkill -f "python -m bot" && sleep 2 && nohup uv run python -m bot > bot.log 2>&1 &
```

## 故障排查

### GitHub Actions 失败

1. 检查 Secrets 是否配置正确
2. 确认服务器 SSH 端口开放
3. 查看服务器 `~/.ssh/authorized_keys` 是否包含公钥

### Bot 无法启动

1. 检查 `.env` 文件配置是否正确
2. 查看 `bot.log` 日志文件
3. 确认依赖已安装：`uv sync`
