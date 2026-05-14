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
    # 1. Cấu hình Selenium chuẩn cho GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        # Tự động tìm Chrome có sẵn trên GitHub
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
        print(f"Đang mở trang: {url}")
        
        driver.get(url)
        time.sleep(20) # Đợi trang load dữ liệu
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tìm các gói thầu
        items = soup.select('div[class*="item-thau"], div[class*="card-item"]')
        
        content = ""
        for i, item in enumerate(items[:5]):
            info = item.get_text(separator=' ', strip=True)
            if "Mã TBMT" in info:
                content += f"🔹 {info}\n\n"

        if content:
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=f"🚀 **THẦU MỚI:**\n\n{content}", parse_mode='Markdown')
            print("Gửi Telegram OK!")
        else:
            print("Kết quả trống.")

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    asyncio.run(main())