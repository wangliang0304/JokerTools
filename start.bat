@echo off
chcp 65001 >nul
title 头条文章监控系统

echo ========================================
echo 🚀 头条文章监控系统
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "config.json" (
    echo ⚠️ 配置文件不存在
    echo 是否运行配置向导？
    set /p choice="输入 y 运行配置向导，其他键退出: "
    if /i "%choice%"=="y" (
        python setup_config.py
        if errorlevel 1 (
            echo ❌ 配置失败
            pause
            exit /b 1
        )
    ) else (
        echo 请先运行配置向导: python setup_config.py
        pause
        exit /b 1
    )
)

REM 检查依赖
echo 📦 检查依赖...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 显示菜单
:menu
echo.
echo 请选择操作:
echo 1. 启动监控服务
echo 2. 测试系统
echo 3. 查看状态
echo 4. 手动检查
echo 5. 配置向导
echo 6. 退出
echo.
set /p choice="请输入选择 (1-6): "

if "%choice%"=="1" goto start_monitor
if "%choice%"=="2" goto test_system
if "%choice%"=="3" goto show_status
if "%choice%"=="4" goto manual_check
if "%choice%"=="5" goto config_wizard
if "%choice%"=="6" goto exit
echo ❌ 无效选择，请重新输入
goto menu

:start_monitor
echo.
echo 🚀 启动监控服务...
echo 按 Ctrl+C 停止服务
echo.
python main.py start
goto menu

:test_system
echo.
echo 🔧 测试系统...
python main.py test
echo.
pause
goto menu

:show_status
echo.
echo 📊 查看状态...
python main.py status
echo.
pause
goto menu

:manual_check
echo.
echo 🔍 手动检查...
python main.py check
echo.
pause
goto menu

:config_wizard
echo.
echo ⚙️ 运行配置向导...
python setup_config.py
echo.
pause
goto menu

:exit
echo.
echo 👋 再见！
exit /b 0
