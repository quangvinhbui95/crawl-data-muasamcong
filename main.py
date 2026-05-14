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
    # 1. Cấu hình Selenium Headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Giả lập User-Agent để tránh bị hệ thống chặn
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # URL tìm kiếm (nên sử dụng tham số tìm kiếm trực tiếp trên URL)
    url = "https://muasamcong.mpi.gov.vn/web/guest/contractor-selection?keyword=bảng%20trượt"
    
    try:
        print(f"Đang truy cập: {url}")
        driver.get(url)
        
        # Chờ đợi trang Render hoàn toàn (Muasamcong dùng React nên load khá chậm)
        time.sleep(20) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Selector mới: Thường các gói thầu nằm trong các div có class 'card-item' hoặc 'item-content'
        # Mình sẽ dùng tìm kiếm linh hoạt hơn để tránh hụt dữ liệu
        items = soup.select('div[class*="item-thau"], div[class*="card-item"]') 
        
        content = ""
        count = 0
        for item in items:
            if count >= 5: break # Lấy tối đa 5 gói thầu mới nhất
            
            text_data = item.get_text(separator=' | ', strip=True)
            if "Mã TBMT" in text_data:
                content += f"📦 **Gói thầu {count+1}:**\n{text_data}\n\n"
                count += 1

        if content:
            # 2. Gửi Telegram (Sử dụng biến môi trường từ GitHub Secrets)
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            
            if token and chat_id:
                bot = Bot(token=token)
                # Gửi thông báo
                header = "🔔 **PHÁT HIỆN GÓI THẦU BẢNG TRƯỢT MỚI** 🔔\n\n"
                await bot.send_message(chat_id=chat_id, text=header + content, parse_mode='Markdown')
                print(f"Đã gửi {count} gói thầu qua Telegram.")
            else:
                print("Lỗi: Thiếu TELEGRAM_TOKEN hoặc CHAT_ID trong Environment Variables.")
        else:
            print("Không tìm thấy dữ liệu thầu. Có thể do Selector sai hoặc trang chưa load kịp.")
            # Debug: In ra một phần HTML nếu không tìm thấy gì
            # print(soup.prettify()[:500])

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
