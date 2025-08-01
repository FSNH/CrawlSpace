#!/bin/bash

# Script to start Django development server, cron service, and add Django crontab tasks

# Exit on any error
set -e

# Define project directory and log file
#PROJECT_DIR="/mnt/data/pythongit/CrawlSpace版本迭代/CrawlSpace"
#LOG_FILE="/mnt/data/pythongit/CrawlSpace版本迭代/CrawlSpace/logs/crontab.log"
PROJECT_DIR="$(dirname "$(realpath "$0")")"
LOG_FILE="$PROJECT_DIR/logs/start.log"
DJANGO_PORT=8000  # Default port for Django server
PID_FILE="/tmp/django_runserver.pid"  # File to store Django server PID
STATIC_ROOT="${STATIC_ROOT:-$PROJECT_DIR/static}"  # Default to project/staticfiles

# Superuser credentials (set these in your environment or modify here)
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin01"}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"admin01"}


# 日志记录函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 启动服务函数
start_services() {
    # 检查日志文件是否可写
    if ! touch "$LOG_FILE" 2>/dev/null; then
        echo "错误：无法写入日志文件 $LOG_FILE，请检查权限"
        exit 1
    fi

    # 检查是否安装 cron
    if ! command -v cron &> /dev/null; then
        log_message "错误：未安装 cron，正在安装..."
        if sudo apt-get update && sudo apt-get install -y cron 2>>"$LOG_FILE"; then
            log_message "cron 安装成功"
        else
            log_message "错误：安装 cron 失败"
            exit 1
        fi
    fi

    # 启动 cron 服务
    log_message "启动 cron 服务..."
    if sudo service cron start 2>>"$LOG_FILE"; then
        log_message "cron 服务启动成功"
    else
        log_message "错误：启动 cron 服务失败"
        exit 1
    fi

    # 验证 cron 服务状态
    if service cron status | grep -q "active (running)"; then
        log_message "cron 服务正在运行"
    else
        log_message "错误：cron 服务未运行"
        exit 1
    fi

    # 进入项目目录
    cd "$PROJECT_DIR" || {
        log_message "错误：无法进入项目目录 $PROJECT_DIR"
        exit 1
    }

    # 运行 Django 迁移
    log_message "运行 Django makemigrations..."
    if python manage.py makemigrations 2>>"$LOG_FILE"; then
        log_message "Django makemigrations 完成"
    else
        log_message "错误：运行 makemigrations 失败"
        exit 1
    fi

    log_message "运行 Django migrate..."
    if python manage.py migrate 2>>"$LOG_FILE"; then
        log_message "Django migrate 完成"
    else
        log_message "错误：运行 migrate 失败"
        exit 1
    fi

    # 验证超级用户凭证
    if [ -z "$DJANGO_SUPERUSER_USERNAME" ] || [ -z "$DJANGO_SUPERUSER_EMAIL" ] || [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
        log_message "错误：超级用户凭证未完整设置（用户名、邮箱或密码缺失）"
        exit 1
    fi

    # 检查超级用户是否存在，不存在则创建
    log_message "检查超级用户 '$DJANGO_SUPERUSER_USERNAME'..."
    if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())" 2>>"$LOG_FILE" | grep -q "True"; then
        log_message "超级用户 '$DJANGO_SUPERUSER_USERNAME' 已存在，验证权限和密码..."
        # 验证权限
        if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); print(u.is_superuser and u.is_staff)" 2>>"$LOG_FILE" | grep -q "True"; then
            log_message "超级用户 '$DJANGO_SUPERUSER_USERNAME' 已具有 superuser 和 staff 权限"
        else
            log_message "修复超级用户 '$DJANGO_SUPERUSER_USERNAME' 的权限..."
            if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); u.is_superuser = True; u.is_staff = True; u.save()" 2>>"$LOG_FILE"; then
                log_message "超级用户权限修复成功"
            else
                log_message "错误：修复超级用户权限失败"
                exit 1
            fi
        fi
        # 验证密码
        if python manage.py shell -c "from django.contrib.auth import authenticate; user = authenticate(username='$DJANGO_SUPERUSER_USERNAME', password='$DJANGO_SUPERUSER_PASSWORD'); print('Login successful' if user else 'Login failed')" 2>>"$LOG_FILE" | grep -q "Login successful"; then
            log_message "超级用户 '$DJANGO_SUPERUSER_USERNAME' 密码验证成功"
        else
            log_message "错误：超级用户 '$DJANGO_SUPERUSER_USERNAME' 密码验证失败，尝试重置..."
            if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); u.set_password('$DJANGO_SUPERUSER_PASSWORD'); u.save()" 2>>"$LOG_FILE"; then
                log_message "超级用户密码重置成功"
            else
                log_message "错误：重置超级用户密码失败，请检查日志 $LOG_FILE"
                exit 1
            fi
        fi
    else
        log_message "创建 Django 超级用户..."
        # 使用 Python 脚本创建超级用户，确保密码可靠设置
        if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username='$DJANGO_SUPERUSER_USERNAME', email='$DJANGO_SUPERUSER_EMAIL', password='$DJANGO_SUPERUSER_PASSWORD')" 2>>"$LOG_FILE"; then
            log_message "Django 超级用户 '$DJANGO_SUPERUSER_USERNAME' 创建成功"
            # 确保权限正确
            if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); u.is_superuser = True; u.is_staff = True; u.save()" 2>>"$LOG_FILE"; then
                log_message "超级用户权限设置成功"
            else
                log_message "错误：设置超级用户权限失败"
                exit 1
            fi
        else
            log_message "错误：创建 Django 超级用户失败，请检查日志 $LOG_FILE"
            exit 1
        fi
    fi

    # 确保 STATIC_ROOT 存在且可写
    log_message "检查 STATIC_ROOT 目录 ($STATIC_ROOT)..."
    if [ ! -d "$STATIC_ROOT" ]; then
        log_message "创建 STATIC_ROOT 目录于 $STATIC_ROOT..."
        if mkdir -p "$STATIC_ROOT" 2>>"$LOG_FILE"; then
            log_message "STATIC_ROOT 目录创建成功"
        else
            log_message "错误：无法创建 STATIC_ROOT 目录"
            exit 1
        fi
    fi
    if [ ! -w "$STATIC_ROOT" ]; then
        log_message "尝试为 STATIC_ROOT 设置写权限..."
        if chmod u+rw "$STATIC_ROOT" 2>>"$LOG_FILE"; then
            log_message "STATIC_ROOT 权限设置成功"
        else
            log_message "警告：无法为 STATIC_ROOT 设置权限，尝试使用 sudo 运行 collectstatic..."
            if sudo python manage.py collectstatic --noinput 2>>"$LOG_FILE"; then
                log_message "使用 sudo 成功收集静态文件"
            else
                log_message "错误：即使使用 sudo 也无法收集静态文件"
                exit 1
            fi
        fi
    fi

    # 收集静态文件
    log_message "收集静态文件到 $STATIC_ROOT..."
    if python manage.py collectstatic --noinput 2>>"$LOG_FILE"; then
        log_message "静态文件收集成功"
    else
        log_message "错误：收集静态文件失败，请检查日志 $LOG_FILE"
        exit 1
    fi

    # 在后台启动 Django 开发服务器并保存 PID
    log_message "启动 Django 开发服务器，端口 $DJANGO_PORT..."
    if python manage.py runserver 0.0.0.0:$DJANGO_PORT > "$LOG_FILE" 2>&1 & then
        DJANGO_PID=$!
        if echo $DJANGO_PID > "$PID_FILE"; then
            log_message "Django 开发服务器启动成功，PID 为 $DJANGO_PID"
        else
            log_message "错误：无法写入 PID 文件 $PID_FILE"
            exit 1
        fi
    else
        log_message "错误：启动 Django 开发服务器失败"
        exit 1
    fi

    # 添加 Django 定时任务
    log_message "添加 Django 定时任务..."
    if python manage.py crontab add 2>>"$LOG_FILE"; then
        log_message "Django 定时任务添加成功"
    else
        log_message "错误：添加 Django 定时任务失败"
        exit 1
    fi

    # 显示当前定时任务
    log_message "当前定时任务："
    python manage.py crontab show >> "$LOG_FILE" 2>&1

    log_message "启动脚本执行成功"
    echo "Django 服务器和 cron 设置完成。请检查 $LOG_FILE 获取详情。"
}

# 停止服务函数
stop_services() {
    # 停止 Django 开发服务器
    if [ -f "$PID_FILE" ]; then
        DJANGO_PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$DJANGO_PID" ] && ps -p "$DJANGO_PID" > /dev/null 2>&1; then
            log_message "停止 Django 开发服务器，PID 为 $DJANGO_PID..."
            if kill -15 "$DJANGO_PID" 2>>"$LOG_FILE"; then
                log_message "Django 开发服务器停止成功"
                rm -f "$PID_FILE" 2>/dev/null || log_message "警告：无法删除 PID 文件 $PID_FILE"
            else
                log_message "错误：停止 Django 开发服务器失败，PID $DJANGO_PID 可能无效"
            fi
        else
            log_message "警告：PID $DJANGO_PID 不存在或 PID 文件无效，尝试查找 Django 进程..."
            rm -f "$PID_FILE" 2>/dev/null
        fi
    else
        log_message "警告：未找到 Django 服务器的 PID 文件，尝试查找进程..."
    fi

    # 查找并终止任何剩余的 Django 进程
    DJANGO_PID=$(ps aux | grep "[p]ython manage.py runserver 0.0.0.0:$DJANGO_PORT" | awk '{print $2}' | head -1)
    if [ -n "$DJANGO_PID" ]; then
        log_message "找到 Django 进程，PID 为 $DJANGO_PID，尝试停止..."
        if kill -15 "$DJANGO_PID" 2>>"$LOG_FILE"; then
            log_message "Django 进程停止成功，PID 为 $DJANGO_PID"
        else
            log_message "错误：无法停止 Django 进程，PID 为 $DJANGO_PID"
        fi
    else
        log_message "信息：未找到运行中的 Django 进程"
    fi

    # 停止 cron 服务
    log_message "停止 cron 服务..."
    if sudo service cron stop 2>>"$LOG_FILE"; then
        log_message "cron 服务停止成功"
    else
        log_message "错误：停止 cron 服务失败，请检查权限或服务状态"
    fi

    # 删除 Django 定时任务
    log_message "删除 Django 定时任务..."
    cd "$PROJECT_DIR" || {
        log_message "错误：无法进入项目目录 $PROJECT_DIR"
        exit 1
    }
    if python manage.py crontab remove 2>>"$LOG_FILE"; then
        log_message "Django 定时任务删除成功"
    else
        log_message "错误：删除 Django 定时任务失败"
    fi

    log_message "停止脚本执行完成"
    echo "Django 服务器和 cron 服务停止完成。请检查 $LOG_FILE 获取详情。"
}

# 检查启动/停止参数
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    *)
        echo "用法: $0 {start|stop}"
        exit 1
        ;;
esac