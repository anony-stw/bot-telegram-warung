import telebot
import time
import threading
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8804489343:AAFht9Da4jH0u6mTx38p3eSE-xOuCzT2Th4"
ADMIN_ID = 8714195568

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

bot = telebot.TeleBot(TOKEN)

# Kamus untuk menyimpan message_id foto QRIS pembeli
qris_message_tracker = {}

# Fungsi untuk membuat menu tombol permanen di bawah
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛒 Beli Paket VIP 8 Grup (Rp 50.000)"))
    markup.add(KeyboardButton("⭐ Testimoni"), KeyboardButton("❓ Bantuan / FAQ"))
    markup.add(KeyboardButton("📞 Hubungi Admin"))
    return markup

# 1. Saat user mengetik /start atau menyapa bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(
        message, 
        "Halo! Selamat Datang di bot VIP Warung Dosa.\n\n"
        "🔥 **Paket Hemat:** Dapatkan akses ke **8 Grup VIP ** hanya dengan **Rp 50.000**!\n\n"
        "Silakan gunakan tombol menu di bawah untuk mulai:", 
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

# 2. Menangani tombol menu permanen: "Beli Paket"
@bot.message_handler(func=lambda message: message.text == "🛒 Beli Paket VIP 8 Grup (Rp 50.000)")
def handle_buy_menu(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 Tampilkan QRIS Pembayaran", callback_data="show_qris"))
    
    bot.send_message(
        chat_id,
        "🟢Anda memilih **Paket VIP 8 Grup Sekaligus (Rp 50.000)**.\n\nKlik tombol di bawah untuk menampilkan QR Code pembayaran:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 3. Menangani tombol menu permanen: "⭐ Testimoni / Ulasan"
@bot.message_handler(func=lambda message: message.text == "⭐ Testimoni")
def handle_testimoni(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Buka Channel Testimoni", url="https://t.me/testiwarungdosaa"))
    
    bot.send_message(
        chat_id,
        "⭐ **Testimoni Member VIP WarungDosa**\n\n"
        "Ingin melihat bukti screenshot pembayaran dan kepuasan member lain yang sudah bergabung?\n\n"
        "Silakan klik tombol di bawah untuk melihat kumpulan testimoni lengkap kami:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 4. Menangani tombol menu permanen: "Bantuan / FAQ"
@bot.message_handler(func=lambda message: message.text == "❓ Bantuan / FAQ")
def handle_faq(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(
        message,
        "💡 **Panduan & FAQ:**\n\n"
        "1. Klik tombol **'🛒 Beli Paket VIP 8 Grup'** di bawah.\n"
        "2. Klik tombol QRIS yang muncul, lalu scan dan bayar tepat **Rp 50.000**.\n"
        "3. **Kirim screenshot bukti transfer** ke chat ini.\n"
        "4. Admin akan memverifikasi, dan link khusus sekali pakai akan dikirim otomatis!\n\n"
        "⚠️ *Catatan: Foto QRIS akan otomatis terhapus setelah pembayaran Anda disetujui admin.*"
    )

# 5. Menangani tombol menu permanen: "Hubungi Admin"
@bot.message_handler(func=lambda message: message.text == "📞 Hubungi Admin")
def handle_contact_admin(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Chat Admin Sekarang", url="https://t.me/Arauxss"))
    
    bot.send_message(
        chat_id,
        "💬 Silakan hubungi Admin kami jika Anda mengalami kendala seputar pembayaran atau akses grup:",
        reply_markup=markup
    )

# 6. Ketika tombol "Tampilkan QRIS" diklik
@bot.callback_query_handler(func=lambda call: call.data == "show_qris")
def process_show_qris(call):
    chat_id = call.message.chat.id
    bot.send_chat_action(chat_id, 'upload_photo')
    
    caption_text = (
        "paket hemat : price 50RB💵\n"
        "   💦Grup Hijab\n"
        "   💦Grup Random\n"
        "   💦Grup Ome Tv\n"
        "   💦Grup Stw\n"
        "   💦Grup Ngintip\n"
        "   💦Grup JJ Tiktok\n"
        "   💦Grup Backup\n"
        "   💦Grup Boc*l (students)\n\n"
        "SETELAH JOIN TIDAK DIKENAKAN BIAYA LAGI!!!\n\n"
        "Silakan transfer tepat Rp 50.000 lalu kirim screenshot bukti transfer ke chat ini."
    )
    
    try:
        photo_file = open('qris.jpg', 'rb')
    except Exception:
        bot.send_message(chat_id, "Gagal memuat gambar QRIS. Pastikan file 'qris.jpg' ada di folder yang sama.")
        bot.answer_callback_query(call.id, "Gagal memuat QRIS!")
        return

    try:
        sent_photo = bot.send_photo(
            chat_id, 
            photo_file, 
            caption=caption_text
        )
        qris_message_tracker[chat_id] = sent_photo.message_id
    except Exception as e:
        bot.send_message(chat_id, f"Terjadi kesalahan: {e}")
        
    bot.answer_callback_query(call.id, "QRIS berhasil dimuat!")

# 7. Menangkap foto bukti transfer dari pembeli (Hanya berfungsi di Chat Pribadi / DM)
@bot.message_handler(content_types=['photo'])
def handle_payment_proof(message):
    # Pastikan foto dikirim di chat pribadi (DM bot), BUKAN di dalam grup/channel
    if message.chat.type != 'private':
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    if user_id == ADMIN_ID:
        bot.reply_to(message, "Itu adalah foto dari Anda (Admin).")
        return

    markup = InlineKeyboardMarkup()
    btn_approve = InlineKeyboardButton("✅ Setujui & Buat Link Unik", callback_data=f"approve_{user_id}")
    btn_reject = InlineKeyboardButton("❌ Tolak", callback_data=f"reject_{user_id}")
    markup.add(btn_approve, btn_reject)
    
    photo_id = message.photo[-1].file_id
    
    bot.send_photo(
        ADMIN_ID, 
        photo_id, 
        caption=f"🔔 **Bukti Pembayaran Paket VIP 8 Grup Baru!**\nDari: @{username} (ID: `{user_id}`)\nStatus: Menunggu Konfirmasi",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    bot.reply_to(message, "Bukti pembayaran terkirim ke Admin. Mohon tunggu verifikasi ya!")

# 8. Aksi Admin ketika menekan tombol Setujui / Tolak
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_action(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Akses ditolak!", show_alert=True)
        return
        
    parts = call.data.split("_")
    action = parts[0]
    target_user_id = int(parts[1])
    
    if action == "approve":
        try:
            generated_links = []
            for group_id in ALL_GROUP_IDS:
                invite = bot.create_chat_invite_link(chat_id=group_id, member_limit=1)
                generated_links.append(invite.invite_link)
            
            links_text = "\n".join([f"- {link}" for link in generated_links])
            
            # Kirim link grup ke pembeli
            bot.send_message(
                target_user_id,
                f"Pembayaran Diverifikasi✅\n\nTerima kasih. Berikut adalah link akses eksklusif sekali pakai Anda:\n\n{links_text}\n\n⚠️Catatan: Link ini hanya bisa digunakan sekali dan akan kedaluwarsa setelah diklik."
            )
            
            # Hapus QRIS di chat pembeli
            if target_user_id in qris_message_tracker:
                try:
                    bot.delete_message(chat_id=target_user_id, message_id=qris_message_tracker[target_user_id])
                    del qris_message_tracker[target_user_id]
                except:
                    pass
            
            # [JIKA DI-ACC] Foto bukti transfer TIDAK DIHAPUS, hanya statusnya yang diubah
            try:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=call.message.caption + "\n\n✅ **STATUS: DISETUJUI (LINK TERKIRIM)**",
                    parse_mode="Markdown",
                    reply_markup=None
                )
            except:
                pass
                
            bot.answer_callback_query(call.id, "Berhasil! Link dikirim & bukti disimpan.")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Gagal membuat link: {e}", show_alert=True)
            
    elif action == "reject":
        try:
            bot.send_message(target_user_id, "❌ Maaf, bukti pembayaran Anda ditolak atau tidak valid.")
            
            # [JIKA DITOLAK] Foto bukti transfer di chat admin akan DIHAPUS OTOMATIS
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            except:
                pass
                
            bot.answer_callback_query(call.id, "Pembayaran ditolak & bukti dihapus.")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Gagal: {e}", show_alert=True)

print("Bot lengkap sedang berjalan...")
bot.infinity_polling()
