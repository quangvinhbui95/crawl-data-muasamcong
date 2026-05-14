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
    # 1. Cấu hình Selenium sạch cho GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # KHÔNG dùng chrome_options.binary_location ở đây nữa

    try:
        # Tự động cài đặt Driver tương thích với Chrome có sẵn trên GitHub
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
        print(f"Đang quét: {url}")
        
        driver.get(url)
        time.sleep(20) # Chờ trang React load API
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tìm tất cả các thẻ div chứa thông tin thầu
        # Selector này bao quát các khung danh sách của Muasamcong
        items = soup.find_all('div', class_=lambda x: x and ('item-thau' in x or 'card-item' in x))
        
        content = ""
        for i, item in enumerate(items[:5]):
            info = item.get_text(separator=' ', strip=True)
            if "Mã TBMT" in info:
                content += f"🔹 **Gói {i+1}:** {info}\n\n"

        if content:
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=f"🚀 **CÓ THẦU BẢNG TRƯỢT MỚI:**\n\n{content}", parse_mode='Markdown')
            print("Đã gửi Telegram thành công!")
        else:
            print("Không tìm thấy dữ liệu. Có thể trang web đổi cấu hình hoặc đang trống thầu.")

    except Exception as e:
        print(f"Lỗi rồi Vinh ơi: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
