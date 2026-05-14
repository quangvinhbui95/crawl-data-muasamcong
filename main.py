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
    # KHÔNG dùng chrome_options.binary_location ở đây nữa để tránh lỗi 'no chrome binary'

    try:
        # Tự động cài đặt Driver tương thích với Chrome có sẵn trên GitHub
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Từ khóa "bảng trượt" đã được mã hóa vào URL
        url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
        print(f"Đang tiến hành quét thầu tại: {url}")
        
        driver.get(url)
        time.sleep(20) # Chờ 20 giây để trang React/Angular load xong API thầu
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tìm tất cả các khối chứa thông tin thầu (Selector linh hoạt)
        items = soup.find_all('div', class_=lambda x: x and ('item-thau' in x or 'card-item' in x))
        
        content = ""
        count = 0
        for item in items:
            if count >= 5: break
            info = item.get_text(separator=' ', strip=True)
            if "Mã TBMT" in info:
                content += f"🔹 **Gói {count+1}:** {info}\n\n"
                count += 1

        if content:
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=f"🚀 **PHÁT HIỆN GÓI THẦU MỚI:**\n\n{content}", parse_mode='Markdown')
            print(f"Đã gửi thành công {count} gói thầu.")
        else:
            print("Kết quả rỗng. Có thể trang web chưa load kịp hoặc không có thầu mới.")

    except Exception as e:
        print(f"Lỗi rồi Vinh ơi: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
