# 快速部署指南

## 🚀 一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/magicnight/subman.git
cd subman

# 2. 运行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh --install

# 3. 启动服务
sudo systemctl start subman

# 4. 访问应用
# 浏览器打开: http://your_server_ip:8501
```

## 🐳 Docker 部署

```bash
# 1. 进入项目目录
cd subman

# 2. 启动容器
docker-compose up -d

# 3. 访问应用
# 浏览器打开: http://your_server_ip:8501
```

## 📝 常用命令

### 使用部署脚本

```bash
sudo ./deploy.sh --start      # 启动
sudo ./deploy.sh --stop       # 停止
sudo ./deploy.sh --restart    # 重启
sudo ./deploy.sh --status     # 状态
sudo ./deploy.sh --logs       # 日志
sudo ./deploy.sh --update     # 更新
```

### 使用 systemctl

```bash
sudo systemctl start subman
sudo systemctl stop subman
sudo systemctl restart subman
sudo systemctl status subman
sudo journalctl -u subman -f
```

### 使用 Docker

```bash
docker-compose up -d          # 启动
docker-compose stop           # 停止
docker-compose restart        # 重启
docker-compose logs -f        # 日志
docker-compose ps             # 状态
```

## 🔧 配置说明

### 修改端口

**systemd 方式:**
编辑 `/etc/systemd/system/subman.service`，修改 `--server.port=8501`

**Docker 方式:**
编辑 `docker-compose.yml`，修改 `ports` 部分

### 配置域名和 HTTPS

参考 [DEPLOYMENT.md](DEPLOYMENT.md) 中的 "配置 Nginx 反向代理" 和 "配置 HTTPS" 章节。

## 📚 详细文档

- [完整部署文档](DEPLOYMENT.md) - 详细的部署说明和故障排查
- [项目 README](README.md) - 项目介绍和使用说明

## ⚠️ 注意事项

1. **数据备份**: 定期备份 `data/` 目录
2. **防火墙**: 确保开放 8501 端口（或配置的端口）
3. **权限**: 确保运行用户有项目目录的读写权限

## 🆘 遇到问题？

查看日志：
```bash
# systemd
sudo journalctl -u subman -f

# Docker
docker-compose logs -f
```

详细故障排查请参考 [DEPLOYMENT.md](DEPLOYMENT.md#故障排查)
