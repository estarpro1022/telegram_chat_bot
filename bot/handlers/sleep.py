"""睡眠提醒命令处理器"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.reminder import send_sleep_reminder, sleep_reminder_users, parse_time
from bot.config import Config


async def sleep_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开启睡眠提醒，可选指定时间"""
    chat_id = update.effective_chat.id

    # 获取用户输入的时间（如果有）
    if context.args and len(context.args) > 0:
        time_str = context.args[0]
    else:
        time_str = Config.DEFAULT_REMINDER_TIME

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
        f"- /sleepoff 关闭提醒\n"
        f"- /sleepon HH:MM 修改时间\n"
        f"- /sleepstatus 查看设置"
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


async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看睡眠提醒状态"""
    chat_id = update.effective_chat.id

    if chat_id not in sleep_reminder_users:
        await update.message.reply_text(
            f"💤 睡眠提醒状态：未开启\n\n"
            f"使用 /sleepon 开启提醒\n"
            f"默认时间：{Config.DEFAULT_REMINDER_TIME}"
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
        f"/sleepon HH:MM - 修改时间\n"
        f"/sleepoff - 关闭提醒"
    )
