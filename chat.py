import logging
from datetime import time, datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

# --- 配置区域 ---
TELEGRAM_TOKEN = "8289726720:AAF80E347FfSSqqfiPS51eD87wyHmUswxHY"  # 替换为 BotFather 给你的 Token
PROJECT_ID = "project-bcc94d2a-1684-4f9a-8aa"      # 替换为你的 Google Cloud 项目 ID
LOCATION = "us-central1"                # 或者 asia-east1 等区域

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 存储需要接收睡眠提醒的用户配置
# 结构：{chat_id: {"time": time对象}}
sleep_reminder_users = {}

# 默认提醒时间
DEFAULT_REMINDER_TIME = "23:30"


def parse_time(time_str: str) -> time:
    """
    解析用户输入的时间字符串
    支持格式：HH:MM (24小时制)
    """
    time_str = time_str.strip()
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("时间格式应为 HH:MM")
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("时间超出有效范围")
        return time(hour=hour, minute=minute, tzinfo=BEIJING_TZ)
    except ValueError as e:
        raise ValueError(f"时间格式错误: {e}")

# --- 初始化 Vertex AI ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
# 加载模型 (推荐使用 gemini-1.5-flash，速度快且便宜，适合聊天)
model = GenerativeModel("gemini-2.5-flash")

# --- 内存管理 (简单的内存) ---
# 用字典存储每个用户的聊天历史： {user_id: chat_session_object}
user_chats = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """重置聊天历史"""
    user_id = update.effective_user.id
    # 当用户输入 /start 时，重置聊天历史
    user_chats[user_id] = model.start_chat(history=[])
    await update.message.reply_text("你好！我是你的 AI 助手。我们开始聊天吧！\n\n可用命令：\n/start - 清空记忆重新开始\n/help - 查看所有命令\n/sleep_on [HH:MM] - 开启睡眠提醒（可自定义时间）\n/sleep_off - 关闭睡眠提醒\n/sleep_status - 查看睡眠提醒状态")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示帮助信息"""
    help_text = """🤖 AI 助手命令列表：

📝 聊天命令：
/start - 清空对话记忆，重新开始
/help - 显示此帮助信息

💤 睡眠提醒命令：
/sleep_on [HH:MM] - 开启提醒，可指定时间（默认 23:30）
/sleep_off - 关闭睡眠提醒
/sleep_status - 查看当前提醒设置

💡 直接发送文字即可与 AI 聊天！"""
    await update.message.reply_text(help_text)

async def sleep_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开启睡眠提醒，可选指定时间"""
    chat_id = update.effective_chat.id

    # 获取用户输入的时间（如果有）
    if context.args and len(context.args) > 0:
        time_str = context.args[0]
    else:
        time_str = DEFAULT_REMINDER_TIME

    # 解析时间
    try:
        reminder_time = parse_time(time_str)
        time_display = time_str
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {str(e)}\n\n正确格式示例: 23:30, 22:10, 9:00")
        return

    # 检查是否已存在相同时间的任务
    job_name = f"sleep_reminder_{chat_id}"
    existing_jobs = context.job_queue.get_jobs_by_name(job_name)

    # 如果已存在，先删除旧任务
    for job in existing_jobs:
        job.schedule_removal()

    # 创建新任务
    context.job_queue.run_daily(
        send_sleep_reminder,
        time=reminder_time,
        name=job_name,
        data={"chat_id": chat_id, "time_str": time_display}
    )

    # 更新存储
    sleep_reminder_users[chat_id] = {"time": reminder_time}

    await update.message.reply_text(
        f"✅ 睡眠提醒已开启！\n"
        f"提醒时间：每天 {time_display}（北京时间）\n\n"
        f"💡 提示：\n"
        f"- /sleep_off 关闭提醒\n"
        f"- /sleep_on HH:MM 修改时间\n"
        f"- /sleep_status 查看设置"
    )

async def sleep_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """关闭睡眠提醒"""
    chat_id = update.effective_chat.id

    if chat_id not in sleep_reminder_users:
        await update.message.reply_text("⚠️ 你还没有开启睡眠提醒。")
        return

    # 删除该用户的任务
    job_name = f"sleep_reminder_{chat_id}"
    jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in jobs:
        job.schedule_removal()

    # 从存储中移除
    del sleep_reminder_users[chat_id]

    await update.message.reply_text("❌ 睡眠提醒已关闭。")

async def send_sleep_reminder(context: ContextTypes.DEFAULT_TYPE):
    """定时任务：发送睡眠提醒给特定用户"""
    chat_id = context.job.data.get("chat_id")
    time_str = context.job.data.get("time_str")

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🌙 晚安！现在是北京时间 {time_str}，该睡觉啦！\n\n早睡早起身体好，明天又是元气满满的一天！💤"
        )
    except Exception as e:
        logging.error(f"发送睡眠提醒给 {chat_id} 失败: {e}")
        # 发送失败，移除任务和数据
        context.job.schedule_removal()
        if chat_id in sleep_reminder_users:
            del sleep_reminder_users[chat_id]

async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看睡眠提醒状态"""
    chat_id = update.effective_chat.id

    if chat_id not in sleep_reminder_users:
        await update.message.reply_text(
            f"💤 睡眠提醒状态：未开启\n\n"
            f"使用 /sleep_on 开启提醒\n"
            f"默认时间：{DEFAULT_REMINDER_TIME}"
        )
        return

    user_data = sleep_reminder_users[chat_id]
    reminder_time = user_data["time"]
    time_str = f"{reminder_time.hour:02d}:{reminder_time.minute:02d}"

    # 获取下次执行时间
    job_name = f"sleep_reminder_{chat_id}"
    jobs = context.job_queue.get_jobs_by_name(job_name)
    next_run = "未知"
    if jobs:
        next_run = jobs[0].next_t.strftime("%Y-%m-%d %H:%M:%S")

    await update.message.reply_text(
        f"💤 睡眠提醒状态：已开启\n\n"
        f"📅 提醒时间：每天 {time_str}\n"
        f"⏰ 下次提醒：{next_run}\n\n"
        f"管理命令：\n"
        f"/sleep_on HH:MM - 修改时间\n"
        f"/sleep_off - 关闭提醒"
    )

async def chat_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # 1. 并在用户输入时显示 "typing..." 状态 (提升体验)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # 2. 获取或创建该用户的聊天会话
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    chat = user_chats[user_id]

    try:
        # 3. 发送给 Vertex AI 并获取流式响应 (stream=True 可以让回复更快)
        response_stream = chat.send_message(user_text, stream=True)
        
        # 4. 拼接流式回复 (简单起见，这里等待全部生成完再发，进阶做法是实时更新消息)
        full_response = ""
        for chunk in response_stream:
            full_response += chunk.text

        # 5. 回复用户
        # Telegram Markdown 转义有时比较麻烦，纯文本最稳妥，或者用 parse_mode='Markdown'
        await update.message.reply_text(full_response)

    except Exception as e:
        error_msg = f"出错了: {str(e)}"
        print(error_msg) # 打印在终端方便调试
        await update.message.reply_text("抱歉，我的大脑短路了，请稍后再试。")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 指令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("sleep_on", sleep_on))
    app.add_handler(CommandHandler("sleep_off", sleep_off))
    app.add_handler(CommandHandler("sleep_status", sleep_status))
    
    # 消息处理器：过滤掉指令，只处理纯文本
    # TEXT & (~COMMAND) 意思是：是文本 且 不是指令
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_logic))

    print("AI 机器人已启动...")
    print("睡眠提醒功能：用户可自定义提醒时间")
    app.run_polling()