import telebot
import requests
import os
import time
import logging

# Logging sozlamalari
logging.basicConfig(filename='quran_bot.log', level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot tokenini kiriting
BOT_TOKEN = '6809565231:AAF33NNKAxoegb55OtI82TFZQbxlhYZMtRw'
bot = telebot.TeleBot(BOT_TOKEN)

# Start buyrug'i uchun handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = f"Assalomu alaykum, {user_name}!\n\nQur'oni Karim oyatlarini ko'rish uchun quyidagi formatda xabar yuboring:\n\nSura raqami:Oyat raqami\nMasalan: 2:255"
    bot.reply_to(message, welcome_text)

# Oyat so'rovi uchun handler
@bot.message_handler(func=lambda message: ':' in message.text)
def send_ayah(message):
    try:
        # Sura va oyat raqamlarini ajratib olish
        sura, ayah = map(int, message.text.split(':'))
        
        # Arabcha matnni olish
        arabic_url = f"https://api.alquran.cloud/v1/ayah/{sura}:{ayah}/ar.asad"
        arabic_response = requests.get(arabic_url)
        arabic_data = arabic_response.json()
        
        # O'zbekcha tarjimani olish
        uzbek_url = f"https://api.alquran.cloud/v1/ayah/{sura}:{ayah}/uz.sodik"
        uzbek_response = requests.get(uzbek_url)
        
        if arabic_response.status_code == 200:
            arabic_text = arabic_data['data']['text']
            
            # O'zbekcha tarjimani tekshirish
            try:
                uzbek_data = uzbek_response.json()
                uzbek_text = uzbek_data['data']['text']
            except:
                uzbek_text = "Tarjima yuklanmadi. Qayta urinib ko'ring."
        else:
            arabic_text = "Oyat matni yuklanmadi"
            uzbek_text = "Tarjima yuklanmadi"
        
        # Everyayah.com API manzili (rasm uchun)
        image_url = f"https://everyayah.com/data/images_png/{sura}_{ayah}.png"
        print(f"Yuklanayotgan rasm manzili: {image_url}")
        
        # Rasmni yuklab olish
        response = requests.get(image_url)
        
        if response.status_code == 200:
            # Rasmni saqlash
            image_path = f"ayah_{sura}_{ayah}.png"
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Avval rasmni yuborish
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            
            # Keyin matnlarni alohida xabar qilib yuborish
            text_message = f"🔹 {arabic_text}\n\n🔸 {uzbek_text}"
            bot.send_message(message.chat.id, text_message)
            
            # Rasmni o'chirish
            os.remove(image_path)
        else:
            bot.reply_to(message, "Bunday oyat topilmadi. Iltimos sura va oyat raqamlarini tekshiring.")
            
    except ValueError:
        bot.reply_to(message, "Noto'g'ri format. Iltimos raqamlarni to'g'ri kiriting. Masalan: 2:255")
    except Exception as e:
        print(f"Xatolik: {str(e)}")
        bot.reply_to(message, "Iltimos to'g'ri formatda kiriting. Masalan: 2:255")

# Botni ishga tushirish (serverda ishlashi uchun yangilangan)
def main_loop():
    while True:
        try:
            logger.info("Bot ishga tushdi")
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"Bot xatosi: {str(e)}")
            time.sleep(15)

if __name__ == "__main__":
    main_loop()
