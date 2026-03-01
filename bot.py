import os
import io
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from PIL import Image

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Jika dimensi terpanjang lebih dari ini → kirim sebagai dokumen agar tidak dikompresi
PHOTO_MAX_DIM = 2560
# Max file size Telegram (20 MB)
MAX_FILE_SIZE = 20 * 1024 * 1024

# ─── Helpers ──────────────────────────────────────────────────────────────────

def upscale_image(image_bytes: bytes, scale: int):
    """
    Upscale gambar dengan Lanczos (kualitas terbaik).
    Returns (upscaled_bytes, original_size, new_size)
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    original_size = img.size
    new_size = (img.width * scale, img.height * scale)

    upscaled = img.resize(new_size, Image.LANCZOS).convert("RGB")

    output = io.BytesIO()
    upscaled.save(output, format="JPEG", quality=95, optimize=True)
    output.seek(0)
    return output.getvalue(), original_size, new_size


def build_scale_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("2x  📐", callback_data="scale_2"),
        InlineKeyboardButton("3x  📐", callback_data="scale_3"),
        InlineKeyboardButton("4x  📐", callback_data="scale_4"),
    ]])


# ─── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Halo! Saya bot *Image Upscaler* ✨\n\n"
        "📌 *Cara pakai:*\n"
        "1. Kirim gambar (foto atau file/dokumen)\n"
        "2. Pilih skala: 2x, 3x, atau 4x\n"
        "3. Bot langsung *membalas gambar aslimu* dengan versi HD — siap di-forward! 🎉\n\n"
        "💡 Tips: Kirim sebagai *file/dokumen* agar kualitas asli tidak dikompresi Telegram.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🆘 *Bantuan*\n\n"
        "• Kirim sebagai *foto* → Telegram kompres otomatis (kualitas agak turun)\n"
        "• Kirim sebagai *file/dokumen* → kualitas asli terjaga ✅\n\n"
        "Skala:\n"
        "• *2x* → resolusi naik 2 kali\n"
        "• *3x* → resolusi naik 3 kali\n"
        "• *4x* → resolusi naik 4 kali\n\n"
        "Hasil dikirim sebagai *balasan langsung* ke gambar aslimu agar mudah di-forward.",
        parse_mode="Markdown",
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Terima gambar yang dikirim sebagai foto (compressed)."""
    photo = update.message.photo[-1]  # ambil resolusi terbesar yang tersedia

    # Simpan referensi file DAN pesan asli
    context.user_data["file_id"] = photo.file_id
    context.user_data["original_message_id"] = update.message.message_id
    context.user_data["original_chat_id"] = update.message.chat_id

    await update.message.reply_text(
        "🖼️ Gambar diterima! Pilih skala pembesaran:",
        reply_markup=build_scale_keyboard(),
    )


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Terima gambar yang dikirim sebagai file/dokumen (kualitas asli)."""
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text(
            "❌ Bukan file gambar. Kirim ulang sebagai JPG, PNG, WEBP, dll."
        )
        return

    context.user_data["file_id"] = doc.file_id
    context.user_data["original_message_id"] = update.message.message_id
    context.user_data["original_chat_id"] = update.message.chat_id

    await update.message.reply_text(
        f"📁 Gambar diterima! (`{doc.file_name}`)\nPilih skala pembesaran:",
        parse_mode="Markdown",
        reply_markup=build_scale_keyboard(),
    )


async def handle_scale_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Proses upscale lalu kirim hasilnya sebagai REPLY ke gambar asli."""
    query = update.callback_query
    await query.answer()

    file_id            = context.user_data.get("file_id")
    original_msg_id    = context.user_data.get("original_message_id")
    original_chat_id   = context.user_data.get("original_chat_id")

    if not file_id or not original_msg_id:
        await query.edit_message_text("❌ Tidak ada gambar. Kirim gambar dulu!")
        return

    scale = int(query.data.split("_")[1])
    await query.edit_message_text(f"⏳ Memproses {scale}x... Mohon tunggu.")

    try:
        # Download gambar asli
        file = await context.bot.get_file(file_id)
        file_bytes = bytes(await file.download_as_bytearray())

        # Upscale
        upscaled_bytes, original_size, new_size = upscale_image(file_bytes, scale)

        # Cek ukuran output
        if len(upscaled_bytes) > MAX_FILE_SIZE:
            await query.edit_message_text(
                f"⚠️ Hasil upscale ({len(upscaled_bytes) // (1024*1024)} MB) melebihi batas 20 MB Telegram.\n"
                "Coba gunakan skala lebih kecil."
            )
            return

        caption = (
            f"✅ *Resolusi berhasil dinaikkan!*\n"
            f"📐 Asli   : `{original_size[0]} × {original_size[1]}` px\n"
            f"🔼 Sekarang: `{new_size[0]} × {new_size[1]}` px  (*{scale}x*)"
        )

        if max(new_size) <= PHOTO_MAX_DIM:
            # ── Kirim sebagai FOTO → tampil inline, bisa langsung di-forward ──
            await context.bot.send_photo(
                chat_id=original_chat_id,
                photo=io.BytesIO(upscaled_bytes),
                caption=caption,
                parse_mode="Markdown",
                reply_to_message_id=original_msg_id,   # ← reply ke gambar asli!
            )
        else:
            # ── Resolusi sangat besar → kirim sebagai dokumen agar tidak dikompresi ──
            caption += "\n\n📎 _Dikirim sebagai file agar kualitas HD tidak berkurang._"
            await context.bot.send_document(
                chat_id=original_chat_id,
                document=io.BytesIO(upscaled_bytes),
                filename=f"upscaled_{scale}x_{new_size[0]}x{new_size[1]}.jpg",
                caption=caption,
                parse_mode="Markdown",
                reply_to_message_id=original_msg_id,   # ← reply ke gambar asli!
            )

        # Hapus pesan "memproses" agar chat bersih
        await query.delete_message()

        # Bersihkan data sesi user
        context.user_data.clear()

    except Exception as e:
        logger.error(f"Error saat upscale: {e}")
        await query.edit_message_text(
            f"❌ Gagal memproses gambar.\nError: `{e}`\n\nCoba kirim gambar lain.",
            parse_mode="Markdown",
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception saat menangani update:", exc_info=context.error)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, receive_document))
    app.add_handler(CallbackQueryHandler(handle_scale_callback, pattern=r"^scale_\d+$"))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
