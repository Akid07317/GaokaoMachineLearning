# 服务器初始化与部署记录

本文档记录高考志愿预测项目当前服务器的基础配置状态，方便后续对话或协作者接手。

更新时间：2026-05-11  
系统时区：Asia/Shanghai

## 服务器信息

```text
公网 IP: 101.132.168.144
登录用户: don
系统: Ubuntu 24.04.4 LTS
主机名: iZuf6bjykk3xaut9e5lg33Z
项目目录: /srv/new-project
GitHub 仓库: https://github.com/Akid07317/GaokaoMachineLearning.git
```

安全提醒：

- 不要把服务器密码、SSH 私钥、GitHub Token、API Key 写入仓库或聊天记录。
- 当前 GitHub 仓库是公网地址，服务器 IP 写在本文档中会让服务器更容易被扫描；如果以后仓库转为公开展示，应考虑移除 IP 或迁移到私有运维文档。

## 已完成的基础配置

### 系统与目录

```text
磁盘: 40G，初始化时已用约 2.8G
内存: 1.6G
Swap: 2G /swapfile，已写入 /etc/fstab
vm.swappiness: 10
项目目录: /srv/new-project
目录属主: don:don
```

### SSH

有效 SSH 配置：

```text
port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

说明：

- root 登录已禁用。
- SSH 密码登录已禁用，只允许密钥登录。
- `don` 用户在 `sudo` 和 `docker` 组内。
- SSH 配置修改前已备份：

```text
/etc/ssh/sshd_config.bak-20260511165926
```

### 防火墙

UFW 已启用：

```text
Default: deny incoming, allow outgoing, deny routed
Allowed inbound:
- 22/tcp  SSH
- 80/tcp  HTTP
- 443/tcp HTTPS
```

云厂商安全组也需要放行 `22`、`80`、`443`。如果服务器内 UFW 已放行但公网访问失败，优先检查云控制台安全组。

### fail2ban

`fail2ban` 已安装并启用 `sshd` jail：

```text
service: fail2ban
status: active / enabled
maxretry: 5
findtime: 10m
bantime: 1h
```

检查命令：

```bash
sudo fail2ban-client status sshd
```

### Docker

Docker 与 Docker Compose 已安装：

```text
Docker: 29.1.3
Docker Compose: 2.40.3
docker service: active / enabled
```

`don` 用户已经加入 `docker` 组，重新登录后可以免 `sudo` 使用 Docker：

```bash
docker ps
docker compose version
```

### 常用工具

已安装常用开发与运维工具：

```text
git 2.43.0
Python 3.12.3
pip 24.0
pipx 1.4.3
gcc 13.3.0
make 4.3
jq
rsync
tmux
tree
ncdu
zip / unzip
dnsutils
net-tools
traceroute
lsof
htop
vim
nano
```

`pipx ensurepath` 已对 `don` 执行。若 `pipx` 命令路径未生效，重新 SSH 登录即可。

## GitHub 与服务器代码

本地项目已推送到 GitHub：

```text
repo: https://github.com/Akid07317/GaokaoMachineLearning.git
branch: main
initial commit: f25d389 Initial gaokao planner project
```

服务器已克隆到：

```bash
cd /srv/new-project
git status
```

后续在服务器同步最新代码：

```bash
cd /srv/new-project
git pull --ff-only
```

如果服务器上出现本地修改，先查看：

```bash
cd /srv/new-project
git status
git diff
```

不要直接 `git reset --hard`，除非明确确认服务器上的改动都可以丢弃。

## AstrBot QQ 小号机器人部署记录

更新时间：2026-05-11 23:35 Asia/Shanghai

部署目录：

```bash
/home/don/astrbot-qqbot
```

运行方式：

```bash
cd /home/don/astrbot-qqbot
docker compose ps
docker compose logs -f astrbot
docker compose logs -f napcat
docker compose restart
docker compose down
docker compose up -d
```

容器与镜像：

```text
astrbot: swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/soulter/astrbot:v4.22.1
napcat:  m.daocloud.io/docker.io/mlikiowa/napcat-docker:latest
```

端口绑定：

```text
AstrBot WebUI: 127.0.0.1:6185 -> container 6185
NapCat WebUI:  127.0.0.1:6099 -> container 6099
```

说明：

- 两个 WebUI 都只绑定在服务器本机 `127.0.0.1`，不要直接暴露公网。
- 本地访问建议使用 SSH 隧道：

```bash
ssh -L 6185:127.0.0.1:6185 -L 6099:127.0.0.1:6099 don@101.132.168.144
```

- 隧道打开后，本机访问：

```text
AstrBot: http://127.0.0.1:6185
NapCat:  http://127.0.0.1:6099/webui
```

- AstrBot 默认用户名和密码为 `astrbot` / `astrbot`，首次登录后应立即修改。
- NapCat 首次启动会输出 WebUI token 和 QQ 扫码登录二维码。不要把 token、二维码链接、QQ 登录状态文件提交到仓库或聊天记录。
- 2026-05-11 首次部署时，Docker Hub 直连和部分镜像代理拉取 AstrBot 较慢，最终使用华为云 SWR 同步镜像部署 AstrBot v4.22.1。

## 常用检查命令

```bash
ssh don@101.132.168.144
```

```bash
hostname
lsb_release -a
free -h
df -h /
swapon --show
```

```bash
sudo ufw status verbose
sudo systemctl status ssh --no-pager
sudo systemctl status docker --no-pager
sudo systemctl status fail2ban --no-pager
```

```bash
docker --version
docker compose version
docker ps
```

## 后续建议

下一阶段建议做：

1. 绑定域名，并在云控制台安全组确认放行 `80` 和 `443`。
2. 安装 Caddy 或 Nginx，优先推荐 Caddy 自动管理 HTTPS。
3. 为项目补 `docker-compose.yml`、`.env.example` 和部署脚本。
4. 如果后续引入数据库，先写备份脚本，再上线服务。
5. 为 GitHub 仓库配置部署用 SSH key 或只读拉取方式，避免在服务器保存个人访问 Token。

## 禁止写入文档的信息

不要提交以下内容：

```text
服务器登录密码
sudo 密码
SSH 私钥
GitHub Token
数据库密码
API Key
.env 生产配置
真实考生个人信息
```
