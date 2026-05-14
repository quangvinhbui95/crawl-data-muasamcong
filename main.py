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
    # Cấu hình Selenium Headless cho Render
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Đường dẫn đến Chrome đã cài qua shell script
    chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # URL tìm kiếm từ khóa "bảng trượt" (ví dụ)
    url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
    
    try:
        driver.get(url)
        time.sleep(10) # Chờ load API
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Logic bóc tách mã TBMT dựa trên cấu trúc ảnh bạn gửi
        # Lưu ý: Cần kiểm tra chính xác Selector khi chạy thực tế
        items = soup.select('.item-thau') # Ví dụ class
        
        message = "📢 Cập nhật thầu mới:\n"
        if not items:
            message += "Không tìm thấy dữ liệu thầu."
        
        for item in items[:5]: # Lấy 5 tin mới nhất
            message += f"----------\n{item.get_text(separator=' ', strip=True)}\n"

        # Gửi Telegram
        bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
        await bot.send_message(chat_id=os.getenv('CHAT_ID'), text=message)

    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())