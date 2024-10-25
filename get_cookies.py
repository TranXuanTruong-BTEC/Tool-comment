from selenium import webdriver
import pickle
import time

# Khởi tạo trình điều khiển Chrome
driver = webdriver.Chrome()

# Truy cập Facebook
driver.get("https://www.facebook.com/")
time.sleep(60)  # Đăng nhập thủ công và đợi 20 giây để bạn hoàn thành

# Lưu cookie vào file
pickle.dump(driver.get_cookies(), open("facebook_cookies.txt", "wb"))

driver.quit()
