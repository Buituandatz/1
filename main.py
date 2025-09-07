import asyncio
import logging
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token bot của bạn
BOT_TOKEN = "7374832893:AAExmqLWkOtuz0zXMNcueqtCWfzk8mT8P2k"

# Múi giờ Việt Nam
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Dictionary để lưu trữ các task đang chạy
active_tasks = {}

def get_vietnam_time():
    """Lấy thời gian hiện tại ở Việt Nam"""
    return datetime.now(VIETNAM_TZ)

def format_time(dt):
    """Định dạng thời gian"""
    return dt.strftime("%d/%m/%Y %H:%M:%S")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Kiểm tra nếu đã có task chạy
    if chat_id in active_tasks:
        await update.message.reply_text("⏰ Bot đã bắt đầu gửi thời gian rồi!")
        return
    
    await update.message.reply_text(
        f"👋 Xin chào {user.first_name}!\n"
        f"🕐 Bắt đầu gửi thời gian Việt Nam mỗi giây...\n"
        f"❌ Gõ /stop để dừng"
    )
    
    # Tạo task mới
    task = asyncio.create_task(send_time_continuously(chat_id, context))
    active_tasks[chat_id] = task

async def send_time_continuously(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Gửi thời gian liên tục mỗi giây"""
    try:
        while chat_id in active_tasks:
            current_time = get_vietnam_time()
            formatted_time = format_time(current_time)
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🕐 {formatted_time} (GMT+7)"
                )
            except Exception as e:
                logger.error(f"Lỗi gửi tin nhắn: {e}")
                break
            
            # Chờ 1 giây
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info(f"Task cho chat {chat_id} đã bị hủy")
    except Exception as e:
        logger.error(f"Lỗi trong task: {e}")
    finally:
        # Dọn dẹp khi task kết thúc
        if chat_id in active_tasks:
            del active_tasks[chat_id]

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /stop"""
    chat_id = update.effective_chat.id
    
    if chat_id in active_tasks:
        task = active_tasks[chat_id]
        task.cancel()
        del active_tasks[chat_id]
        await update.message.reply_text("✅ Đã dừng gửi thời gian!")
    else:
        await update.message.reply_text("❌ Không có bộ đếm thời gian nào đang chạy!")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /time"""
    current_time = get_vietnam_time()
    formatted_time = format_time(current_time)
    await update.message.reply_text(f"🕐 Thời gian Việt Nam: {formatted_time} (GMT+7)")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lỗi"""
    logger.error(f"Lỗi: {context.error}")

def main():
    """Hàm chính"""
    # Khởi tạo application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("time", time_command))
    
    # Thêm error handler
    application.add_error_handler(error_handler)
    
    # Chạy bot
    print("🤖 Bot đang chạy...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
