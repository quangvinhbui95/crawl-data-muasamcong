import os
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from telegram import Bot

async def main():
    # 1. Cấu hình Selenium cho GitHub Actions (Bỏ binary_location của Render)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # GitHub Actions tự động tìm Chrome, không cần chỉ định đường dẫn thủ công
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
    
    try:
        print(f"🚀 Đang quét dữ liệu từ: {url}")
        driver.get(url)
        
        # Chờ trang Muasamcong render (React)
        time.sleep(20) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tìm các khối thông tin gói thầu
        items = soup.select('div[class*="item-thau"], div[class*="card-item"]') 
        
        content = ""
        count = 0
        for item in items:
            if count >= 5: break 
            text_data = item.get_text(separator=' ', strip=True)
            if "Mã TBMT" in text_data:
                content += f"----------\n📦 **Gói thầu {count+1}:**\n{text_data}\n\n"
                count += 1

        if content:
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            
            if token and chat_id:
                bot = Bot(token=token)
                header = "🔔 **PHÁT HIỆN GÓI THẦU BẢNG TRƯỢT MỚI**\n\n"
                await bot.send_message(chat_id=chat_id, text=header + content, parse_mode='Markdown')
                print(f"✅ Đã gửi {count} gói thầu qua Telegram.")
            else:
                print("❌ Lỗi: Thiếu Token hoặc Chat ID trong Secrets.")
        else:
            print("⚠️ Không tìm thấy dữ liệu. Có thể trang web đổi cấu trúc hoặc đang trống thầu.")

    except Exception as e:
        print(f"❌ Lỗi thực thi: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
