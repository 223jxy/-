#!/bin/bash

# 前端部署脚本

set -e

echo "===== 书驿云桥前端部署脚本 ====="

# 检查Node.js版本
echo "检查Node.js版本..."
node -v
npm -v

# 安装依赖
echo "安装依赖..."
npm install --registry=https://registry.npmmirror.com

# 选择构建环境
if [ -z "$BUILD_ENV" ]; then
  BUILD_ENV="production"
fi

echo "构建环境: $BUILD_ENV"

# 构建应用
echo "构建应用..."
npm run build:$BUILD_ENV

# 检查构建结果
if [ ! -d "dist" ]; then
  echo "构建失败，dist目录不存在"
  exit 1
fi

echo "构建成功，dist目录内容："
ls -la dist

# 部署到目标目录
if [ -n "$DEPLOY_DIR" ]; then
  echo "部署到目标目录: $DEPLOY_DIR"
  
  # 创建目标目录
  mkdir -p $DEPLOY_DIR
  
  # 备份旧版本
  if [ -d "$DEPLOY_DIR" ]; then
    BACKUP_DIR="$DEPLOY_DIR_$(date +%Y%m%d_%H%M%S)"
    echo "备份旧版本到: $BACKUP_DIR"
    cp -r $DEPLOY_DIR $BACKUP_DIR
  fi
  
  # 复制构建产物
  echo "复制构建产物到目标目录..."
  cp -r dist/* $DEPLOY_DIR/
  
  # 清理缓存
  echo "清理缓存..."
  find $DEPLOY_DIR -name "*.gz" -o -name "*.br" | xargs rm -f 2>/dev/null || true
  
  echo "部署完成"
else
  echo "未指定部署目录，构建产物保存在 dist 目录"
fi

# 显示部署信息
echo "\n部署信息："
echo "- 构建环境: $BUILD_ENV"
echo "- 构建时间: $(date)"
echo "- 构建产物大小: $(du -sh dist | cut -f1)"

if [ -n "$DEPLOY_DIR" ]; then
  echo "- 部署目录: $DEPLOY_DIR"
  echo "- 部署后大小: $(du -sh $DEPLOY_DIR | cut -f1)"
fi

echo "===== 部署脚本执行完成 ====="