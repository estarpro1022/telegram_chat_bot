import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- 0. 配置日志 (可选，但推荐，方便看报错) ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Step 2: 定义逻辑函数 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 拿到用户发来的名字
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"你好, {user_name}！我配置好了。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("我能帮你做什么？")

if __name__ == '__main__':
    # --- Step 1: 实例化 ---
    # 记得把 TOKEN 换成你自己的
    app = ApplicationBuilder().token("8289726720:AAF80E347FfSSqqfiPS51eD87wyHmUswxHY").build()
    
    # --- Step 3: 绑定路由 (顺序很重要！) ---
    # 只要匹配到 /start，就进 start 函数，不再往下走
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # --- Step 4: 启动 ---
    print("机器人启动中...")
    app.run_polling()