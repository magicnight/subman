# MySub Manager - Linux 服务器部署指南

本文档介绍如何将 MySub Manager 部署到 Linux 服务器上。

## 📋 目录

- [前置要求](#前置要求)
- [部署方式](#部署方式)
  - [方式一：使用部署脚本（推荐）](#方式一使用部署脚本推荐)
  - [方式二：使用 Docker](#方式二使用-docker)
  - [方式三：手动部署](#方式三手动部署)
- [配置 Nginx 反向代理](#配置-nginx-反向代理)
- [配置 HTTPS](#配置-https)
- [维护和更新](#维护和更新)
- [故障排查](#故障排查)

## 前置要求

### 系统要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / 其他主流 Linux 发行版
- **Python**: 3.12 或更高版本
- **内存**: 至少 512MB RAM
- **磁盘**: 至少 1GB 可用空间

### 必需软件

- `git` - 用于克隆代码
- `curl` - 用于下载安装脚本
- `sudo` - 用于执行管理命令（可选）

## 部署方式

### 方式一：使用部署脚本（推荐）

这是最简单快捷的部署方式，适合大多数用户。

#### 1. 克隆项目

```bash
# 如果还没有项目代码
git clone https://github.com/magicnight/subman.git
cd subman

# 或者如果已有代码，直接进入项目目录
cd /path/to/subman
```

#### 2. 运行部署脚本

```bash
# 给脚本添加执行权限
chmod +x deploy.sh

# 安装服务（需要 root 权限）
sudo ./deploy.sh --install
```

部署脚本会自动：
- ✅ 检查并安装系统依赖
- ✅ 安装 uv 包管理器（如果未安装）
- ✅ 安装项目依赖
- ✅ 创建必要的目录
- ✅ 创建 systemd 服务文件
- ✅ 启用服务

#### 3. 启动服务

```bash
# 启动服务
sudo systemctl start subman

# 查看服务状态
sudo systemctl status subman

# 设置开机自启
sudo systemctl enable subman
```

#### 4. 验证部署

访问 `http://your_server_ip:8501` 查看应用是否正常运行。

#### 5. 管理服务

```bash
# 使用部署脚本管理
sudo ./deploy.sh --start      # 启动
sudo ./deploy.sh --stop       # 停止
sudo ./deploy.sh --restart    # 重启
sudo ./deploy.sh --status     # 查看状态
sudo ./deploy.sh --logs       # 查看日志

# 或直接使用 systemctl
sudo systemctl start subman
sudo systemctl stop subman
sudo systemctl restart subman
sudo systemctl status subman
sudo journalctl -u subman -f  # 查看日志
```

### 方式二：使用 Docker

适合已经熟悉 Docker 的用户，便于管理和迁移。

#### 1. 安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 构建和启动

```bash
# 进入项目目录
cd /path/to/subman

# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

#### 3. 管理容器

```bash
# 停止
docker-compose stop

# 重启
docker-compose restart

# 停止并删除容器
docker-compose down

# 重新构建
docker-compose up -d --build
```

#### 4. 数据持久化

数据文件会自动挂载到 `./data` 目录，确保数据不会丢失。

### 方式三：手动部署

适合需要完全控制部署过程的用户。

#### 1. 安装依赖

```bash
# 安装 Python 3.12
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

#### 2. 克隆项目

```bash
git clone https://github.com/magicnight/subman.git
cd subman
```

#### 3. 安装项目依赖

```bash
uv sync
```

#### 4. 创建 systemd 服务

复制 `subman.service` 到 `/etc/systemd/system/`，并修改以下内容：

```bash
sudo cp subman.service /etc/systemd/system/subman.service
sudo nano /etc/systemd/system/subman.service
```

需要修改的配置：
- `User`: 运行服务的用户
- `WorkingDirectory`: 项目路径
- `ExecStart`: uv 的完整路径

#### 5. 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable subman
sudo systemctl start subman
```

## 配置 Nginx 反向代理

使用 Nginx 作为反向代理可以提供更好的性能和安全性。

### 1. 安装 Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### 2. 配置 Nginx

```bash
# 复制配置文件
sudo cp nginx.conf.example /etc/nginx/sites-available/subman

# 编辑配置
sudo nano /etc/nginx/sites-available/subman
```

修改配置中的 `server_name` 为你的域名或 IP。

### 3. 启用配置

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/subman /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 4. 验证

访问 `http://your_domain` 或 `http://your_server_ip` 应该能看到应用。

## 配置 HTTPS

使用 Let's Encrypt 免费 SSL 证书。

### 1. 安装 Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. 获取证书

```bash
sudo certbot --nginx -d your_domain.com
```

按照提示完成配置，Certbot 会自动配置 Nginx。

### 3. 自动续期

证书会自动续期，但可以手动测试：

```bash
sudo certbot renew --dry-run
```

## 维护和更新

### 更新代码

```bash
# 使用部署脚本（推荐）
sudo ./deploy.sh --update

# 或手动更新
cd /path/to/subman
git pull origin main
uv sync
sudo systemctl restart subman
```

### 备份数据

```bash
# 备份数据目录
tar -czf subman-backup-$(date +%Y%m%d).tar.gz data/

# 或使用 rsync
rsync -av data/ /backup/location/subman-data/
```

### 查看日志

```bash
# systemd 服务日志
sudo journalctl -u subman -f

# 应用日志
tail -f logs/app.log

# 错误日志
tail -f logs/error.log
```

## 故障排查

### 服务无法启动

1. **检查服务状态**
   ```bash
   sudo systemctl status subman
   ```

2. **查看详细日志**
   ```bash
   sudo journalctl -u subman -n 50
   ```

3. **检查端口占用**
   ```bash
   sudo netstat -tlnp | grep 8501
   ```

4. **检查权限**
   ```bash
   ls -la /path/to/subman
   ```

### 无法访问应用

1. **检查防火墙**
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   sudo ufw allow 8501/tcp
   
   # CentOS/RHEL
   sudo firewall-cmd --list-ports
   sudo firewall-cmd --add-port=8501/tcp --permanent
   sudo firewall-cmd --reload
   ```

2. **检查服务是否运行**
   ```bash
   sudo systemctl status subman
   ```

3. **检查 Nginx 配置**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

### 性能优化

1. **增加系统资源**
   - 如果应用响应慢，考虑增加服务器内存

2. **优化 Streamlit 配置**
   - 编辑 `src/config.py` 调整配置

3. **使用 Nginx 缓存**
   - 在 Nginx 配置中启用静态文件缓存

### 常见问题

**Q: 如何更改端口？**

A: 修改 `subman.service` 中的 `--server.port` 参数，或设置环境变量 `PORT=8502`。

**Q: 如何更改运行用户？**

A: 修改 `subman.service` 中的 `User` 字段，确保该用户有项目目录的访问权限。

**Q: 数据文件在哪里？**

A: 数据文件在 `data/` 目录下，包括 `subscriptions.csv`、`Service.csv` 等。

**Q: 如何迁移到新服务器？**

A: 
1. 在新服务器上克隆项目
2. 复制 `data/` 目录到新服务器
3. 运行部署脚本安装服务

## 安全建议

1. **使用非 root 用户运行服务**
   - 在 systemd 服务文件中设置 `User` 字段

2. **配置防火墙**
   - 只开放必要的端口（80, 443, 22）

3. **使用 HTTPS**
   - 配置 SSL 证书保护数据传输

4. **定期更新**
   - 保持系统和依赖包的最新版本

5. **备份数据**
   - 定期备份 `data/` 目录

## 获取帮助

如果遇到问题，可以：

- 📧 提交 Issue: [GitHub Issues](https://github.com/magicnight/subman/issues)
- 📖 查看文档: [README.md](README.md)
- 💬 查看日志: `sudo journalctl -u subman -f`

---

**祝部署顺利！** 🚀
