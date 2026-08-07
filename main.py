import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import sqlite3
from datetime import datetime, timezone, timedelta

# Konfigurasi Token dan Admin ID
TOKEN = "8804489343:AAfHt90a45H0u6mTx38p3eSe-x0uCzT2Th4"
ADMIN_ID = 8714195568

bot = telebot.TeleBot(TOKEN)

# Menentukan Zona Waktu WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

# Inisialisasi Database SQLite
def init_db():
    conn = sqlite3.connect('database_transaksi.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            nominal INTEGER,
            tanggal TEXT,
            waktu_lengkap TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Fungsi untuk mencatat transaksi dengan waktu WIB yang akurat
def catat_transaksi(user_id, username, nominal):
    conn = sqlite3.connect('database_transaksi.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Mengambil waktu sekarang berdasarkan zona waktu WIB (UTC+7)
    waktu_sekarang = datetime.now(WIB)
    tanggal_hari_ini = waktu_sekarang.strftime('%Y-%m-%d')
    waktu_lengkap = waktu_sekarang.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("INSERT INTO transaksi (user_id, username, nominal, tanggal, waktu_lengkap) VALUES (?, ?, ?, ?, ?)",
                   (user_id, username, nominal, tanggal_hari_ini, waktu_lengkap))
    conn.commit()
    conn.close()

# Daftar ID Grup atau Channel Telegram Anda
ALL_GROUP_IDS = [
    -1003721629607,
    -1003646177202,
    -1003727409464,
    -1003713991635,
    -1003839151133,
    -1003561794613,
    -1003634689467,
    -1003853297361
]

# Fungsi Watermark Foto
def apply_watermark(input_path, output_path, watermark_text):
    original_image = Image.open(input_path).convert("RGBA")
    txt_layer = Image.new("RGBA", original_image.size, (255, 255, 255, 0))
    
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    draw = ImageDraw.Draw(txt_layer)
    width, height = original_image.size
    text_position = (width - 150, height - 30) 
    draw.text(text_position, watermark_text, fill=(255, 255, 255, 180), font=font)
    
    watermarked = Image.alpha_composite(original_image, txt_layer)
    watermarked.convert("RGB").save(output_path, "JPEG")

# Handler Tombol Konfirmasi Admin (Approve / Reject)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Anda bukan admin!", show_alert=True)
        return

    data = call.data
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])
        nominal_transaksi = 50000 
        username_pembeli = f"User_{user_id}"
        
        # Catat ke database dengan waktu WIB
        catat_transaksi(user_id, username_pembeli, nominal_transaksi)
        
        bot.answer_callback_query(call.id, "Pembayaran disetujui dan tercatat!")
        bot.send_message(user_id, "✅ Pembayaran Anda telah dikonfirmasi oleh Admin! Silakan nikmati aksesnya.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"{call.message.caption}\n\nstatus: ✅ DISETUJUI")
        
    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Pembayaran ditolak.")
        bot.send_message(user_id, "❌ Mohon maaf, bukti pembayaran Anda ditolak oleh Admin. Silakan hubungi admin.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"{call.message.caption}\n\nstatus: ❌ DITOLAK")

# Fitur Laporan Keuangan Khusus Admin (/laporan)
@bot.message_handler(commands=['laporan'])
def laporan_keuangan(message):
    if message.chat.id != ADMIN_ID or message.chat.type != 'private':
        return

    conn = sqlite3.connect('database_transaksi.db', check_same_thread=False)
    cursor = conn.cursor()

    waktu_sekarang = datetime.now(WIB)
    hari_ini = waktu_sekarang.strftime('%Y-%m-%d')
    cursor.execute("SELECT SUM(nominal), COUNT(*) FROM transaksi WHERE tanggal = ?", (hari_ini,))
    res_hari = cursor.fetchone()
    total_hari = res_hari[0] or 0
    count_hari = res_hari[1] or 0

    bulan_ini = waktu_sekarang.strftime('%Y-%m')
    cursor.execute("SELECT SUM(nominal), COUNT(*) FROM transaksi WHERE tanggal LIKE ?", (f"{bulan_ini}%",))
    res_bulan = cursor.fetchone()
    total_bulan = res_bulan[0] or 0
    count_bulan = res_bulan[1] or 0

    conn.close()

    teks_laporan = (
        f"📊 **LAPORAN KEUANGAN BOT** 📊\n\n"
        f"📅 **Hari Ini ({hari_ini}):**\n"
        f"- Total Transaksi: {count_hari} pembeli\n"
        f"- Pendapatan: Rp {total_hari:,}\n\n"
        f"📆 **Bulan Ini ({bulan_ini}):**\n"
        f"- Total Transaksi: {count_bulan} pembeli\n"
        f"- Pendapatan: Rp {total_bulan:,}"
    )
    
    bot.reply_to(message, teks_laporan, parse_mode="Markdown")

# Handler Foto (Watermark & Bukti Bayar)
@bot.message_handler(content_types=['photo'])
def handle_all_photos(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    if user_id == ADMIN_ID and message.chat.type == 'private':
        bot.reply_to(message, "⏳ Sedang memproses watermark pada foto...")
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            input_file = "input_temp.jpg"
            output_file = "output_watermarked.jpg"
            
            with open(input_file, 'wb') as f:
                f.write(downloaded_file)
                
            apply_watermark(input_file, output_file, "@WarungDosa")
            
            with open(output_file, 'rb') as photo_result:
                bot.send_photo(
                    ADMIN_ID, 
                    photo_result, 
                    caption="✅ Berhasil! Foto sudah diberi watermark otomatis."
                )
                
            os.remove(input_file)
            os.remove(output_file)
        except Exception as e:
            bot.reply_to(message, f"❌ Terjadi kesalahan saat watermark: {e}")
        return

    if message.chat.type == 'private':
        markup = InlineKeyboardMarkup()
        btn_approve = InlineKeyboardButton("✅ Setujui & Catat Transaksi", callback_data=f"approve_{user_id}")
        btn_reject = InlineKeyboardButton("❌ Tolak", callback_data=f"reject_{user_id}")
        markup.add(btn_approve, btn_reject)
        
        photo_id = message.photo[-1].file_id
        
        bot.send_photo(
            ADMIN_ID, 
            photo_id, 
            caption=f"🔔 **Bukti Pembayaran Paket VIP!**\nDari: @{username} (ID: `{user_id}`)\nStatus: Menunggu Konfirmasi",
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        bot.reply_to(message, "Bukti pembayaran terkirim ke Admin. Mohon tunggu verifikasi ya!")
        return

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.reply_to(message, "Halo! Selamat datang di bot layanan WarungDosa. Silakan kirimkan bukti pembayaran Anda di sini.")

print("Bot sedang berjalan...")
bot.infinity_polling()
