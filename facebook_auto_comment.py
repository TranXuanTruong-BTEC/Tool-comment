import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import pickle
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# Tạo thư mục lưu cookies nếu chưa tồn tại
cookies_dir = "cookies"
if not os.path.exists(cookies_dir):
    os.makedirs(cookies_dir)

def log_message(message):
    """Hàm ghi lại thông điệp vào bảng hiển thị."""
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)

def random_sleep(min_seconds=1, max_seconds=3):
    """Hàm để ngủ ngẫu nhiên giữa các hành động."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def add_facebook_account():
    """Hàm để thêm tài khoản Facebook mới."""
    account_window = tk.Toplevel(root)
    account_window.title("Thêm Tài Khoản Facebook Mới")
    account_window.geometry("300x200")

    ttk.Label(account_window, text="Email/Phone:").pack(pady=5)
    email_entry = ttk.Entry(account_window)
    email_entry.pack(pady=5)

    ttk.Label(account_window, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(account_window, show="*")
    password_entry.pack(pady=5)

    def save_account():
        email = email_entry.get()
        password = password_entry.get()
        if email and password:
            # Kiểm tra xem tài khoản đã tồn tại chưa
            if os.path.exists("facebook_accounts.txt"):
                with open("facebook_accounts.txt", "r") as f:
                    for line in f:
                        if email in line:
                            log_message("Tài khoản đã tồn tại. Vui lòng sử dụng tài khoản khác.")
                            return

            log_message("Đang đăng nhập vào Facebook...")
            driver = webdriver.Chrome()
            driver.get("https://www.facebook.com/")
            random_sleep(2, 4)

            # Nhập thông tin đăng nhập
            email_input = driver.find_element(By.NAME, "email")
            password_input = driver.find_element(By.NAME, "pass")
            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            random_sleep(5, 10)  # Đợi để đăng nhập

            # Theo dõi trạng thái đăng nhập
            while True:
                current_url = driver.current_url
                log_message(f"Đang kiểm tra URL: {current_url}")
                
                if "facebook.com" in current_url:
                    log_message("Đang kiểm tra trạng thái đăng nhập...")
                    try:
                        # Kiểm tra xem có thông báo lỗi không
                        error_message = driver.find_element(By.XPATH, "//div[contains(text(), 'sai')]")
                        log_message("Đăng nhập không thành công. Vui lòng kiểm tra thông tin tài khoản.")
                        driver.quit()
                        return
                    except:
                        # Kiểm tra xem có cần xác thực không
                        if "checkpoint" in current_url or "captcha" in current_url:
                            log_message("Cần xác thực CAPTCHA hoặc xác thực từ thiết bị khác. Vui lòng hoàn tất và nhấn Enter.")
                            input("Nhấn Enter khi bạn đã hoàn tất xác thực...")
                            continue  # Quay lại vòng lặp để kiểm tra lại trạng thái

                        # Kiểm tra xem có yêu cầu mã xác thực không
                        if "login" in current_url and "code" in current_url:
                            verification_code = input("Nhập mã xác thực đã gửi đến điện thoại hoặc email của bạn: ")
                            verification_input = driver.find_element(By.NAME, "approvals_code")
                            verification_input.send_keys(verification_code)
                            verification_input.send_keys(Keys.RETURN)
                            random_sleep(5, 10)  # Đợi để đăng nhập

                            # Kiểm tra lại trạng thái đăng nhập
                            continue  # Quay lại vòng lặp để kiểm tra lại trạng thái

                        # Kiểm tra xem đã vào trang chủ Facebook chưa
                        if current_url == "https://www.facebook.com/":
                            log_message("Đăng nhập thành công!")
                            break  # Thoát vòng lặp khi đăng nhập thành công

                random_sleep(2, 4)  # Đợi một chút trước khi kiểm tra lại

            # Lưu cookies vào tệp riêng biệt cho tài khoản trong thư mục cookies
            cookies = driver.get_cookies()
            cookies_file_path = os.path.join(cookies_dir, f"{email}_cookies.txt")
            with open(cookies_file_path, "wb") as f:
                pickle.dump(cookies, f)

            # Chỉ lưu tài khoản vào tệp sau khi đã lưu cookies thành công
            with open("facebook_accounts.txt", "a") as f:
                f.write(f"{email},{password}\n")

            driver.quit()  # Đóng trình duyệt sau khi hoàn tất

            # Thông báo thành công sau khi lưu cookies
            log_message("Tài khoản đã được thêm thành công!")
            account_window.destroy()
            load_accounts()  # Tải lại danh sách tài khoản
        else:
            log_message("Cảnh báo: Vui lòng nhập đầy đủ thông tin!")

    # Thêm nút "Đăng nhập"
    ttk.Button(account_window, text="Đăng nhập", command=save_account).pack(pady=10)

def load_accounts():
    """Hàm tải danh sách tài khoản Facebook từ tệp."""
    accounts_list.delete(0, tk.END)  # Xóa danh sách hiện tại
    if os.path.exists("facebook_accounts.txt"):
        with open("facebook_accounts.txt", "r") as f:
            for line in f:
                line = line.strip()  # Xóa khoảng trắng ở đầu và cuối
                if line:  # Kiểm tra xem dòng không rỗng
                    parts = line.split(",")
                    if len(parts) >= 2:  # Đảm bảo có đủ phần
                        email = parts[0]
                        accounts_list.insert(tk.END, email)  # Thêm email vào danh sách

def login_with_cookies(account_info):
    """Hàm để đăng nhập vào Facebook bằng cookies."""
    log_message("Khởi tạo trình duyệt...")
    driver = webdriver.Chrome()
    
    log_message("Đang truy cập Facebook...")
    driver.get("https://www.facebook.com/")
    random_sleep(2, 4)

    # Tải cookies từ tệp tương ứng với tài khoản đã chọn
    cookies_file_path = os.path.join(cookies_dir, f"{account_info}_cookies.txt")
    if os.path.exists(cookies_file_path):
        log_message("Đang tải cookies...")
        cookies = pickle.load(open(cookies_file_path, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
            log_message(f"Cookie {cookie['name']} đã được thêm.")

        log_message("Đang tải lại Facebook với cookies...")
        driver.get("https://www.facebook.com/")
        random_sleep(5, 10)

        # Kiểm tra trạng thái đăng nhập
        if "facebook.com" in driver.current_url:
            log_message("Đang kiểm tra trạng thái đăng nhập...")
            try:
                # Kiểm tra xem có thông báo lỗi không
                error_message = driver.find_element(By.XPATH, "//div[contains(text(), 'sai')]")
                log_message("Đăng nhập không thành công. Vui lòng kiểm tra thông tin tài khoản.")
                driver.quit()
                return
            except:
                log_message("Đăng nhập thành công!")

        # Bắt đầu thực hiện các tác vụ khác
        auto_comment(account_info, driver)

    else:
        log_message("Không tìm thấy tệp cookies cho tài khoản này.")
        driver.quit()

def start_tool():
    """Hàm để bắt đầu chạy tool với tài khoản đã chọn."""
    selected_account = accounts_list.curselection()
    if not selected_account:
        log_message("Cảnh báo: Vui lòng chọn một tài khoản Facebook để chạy tool.")
        return

    account_info = accounts_list.get(selected_account)
    log_message(f"Bắt đầu đăng nhập với tài khoản: {account_info}")
    threading.Thread(target=login_with_cookies, args=(account_info,)).start()

def auto_comment(account_info, driver):
    """Hàm tự động bình luận vào tất cả các bài viết tìm thấy.""" 
    commented_links = load_commented_links('commented_links.txt')
    
    # Danh sách bình luận
    comments = [
        "Chào mọi người! Nhận mã giảm giá đặc biệt từ Highlands Coffee tại https://shorten.asia/gPkmnG3e!",
        "Giải Pháp Tài Chính Đơn Giản! Cần tiền nhanh chóng? Truy cập https://vay.fecredit.com.vn/ để tìm hiểu thêm!",
        "Mời bạn tham gia chương trình khuyến mãi hấp dẫn tại đây  https://shorten.asia/gPkmnG3e!!",
        "Đừng bỏ lỡ cơ hội nhận ưu đãi đặc biệt này https://vay.fecredit.com.vn/!"
    ]
    
    try:
        while True:
            log_message("Đang tìm bài viết...")
            scroll_down(driver, times=5)
            post_links = get_post_links(driver)
 
            if not post_links:
                log_message("Không tìm thấy bài viết.")
                return
 
            comment_count = 0
            max_comments = random.randint(5, 15)
 
            for link in post_links:
                if link in commented_links:
                    log_message(f"Đã bình luận trên: {link}. Bỏ qua...")
                    continue
 
                log_message(f"Đang truy cập bài viết: {link}")
                driver.get(link)
                random_sleep(2, 4)
 
                try:
                    comment_box = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
                    )
                    log_message("Ô bình luận đã sẵn sàng.")
                    comment_box.click()
                    random_sleep(1, 3)
                    
                    # Chọn ngẫu nhiên bình luận từ danh sách
                    valid_comment = random.choice(comments)
                    log_message(f"Chuẩn bị bình luận: {valid_comment}")
                    comment_box.send_keys(valid_comment)
                    comment_box.send_keys(Keys.RETURN)
                    log_message(f"Bình luận thành công trên: {link}")
 
                    commented_links.add(link)
                    save_commented_link('commented_links.txt', link)
 
                    comment_count += 1
                    log_message(f"Tổng số bình luận: {comment_count}")
                    random_sleep(5, 10)
 
                    if comment_count >= max_comments:
                        log_message("Đã đạt số bình luận tối đa.")
                        break
 
                except Exception as e:
                    log_message(f"Lỗi khi bình luận trên {link}: {e}")
                    continue
 
            break_time = random.randint(240, 360)
            log_message(f"Đang nghỉ trong {break_time // 60} phút...")
            time.sleep(break_time)
 
    finally:
        driver.quit()
        log_message("Bot đã dừng.")

def scroll_down(driver, times=3):
    """Hàm cuộn trang xuống để tải thêm nội dung."""
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        log_message("Đang cuộn trang...")
        random_sleep(2, 4)

def get_post_links(driver):
    """Hàm lấy liên kết các bài viết từ trang tìm kiếm."""
    posts = driver.find_elements(By.XPATH, "//div[contains(@role, 'article')]")
    links = []
    for post in posts:
        try:
            link = post.find_element(By.XPATH, ".//a[contains(@href, '/')]").get_attribute("href")
            links.append(link)
            log_message(f"Tìm thấy liên kết bài viết: {link}")
        except Exception as e:
            log_message(f"Lỗi khi lấy liên kết bài viết: {e}")
            continue
    log_message(f"Tổng số liên kết bài viết tìm thấy: {len(links)}")
    return links

def load_commented_links(filename):
    """Hàm tải các liên kết đã bình luận từ tệp."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            log_message(f"Đang tải liên kết đã bình luận từ {filename}...")
            return set(file.read().splitlines())
    log_message(f"Không tìm thấy liên kết đã bình luận. Bắt đầu mới.")
    return set()

def save_commented_link(filename, link):
    """Hàm lưu liên kết đã bình luận vào tệp."""
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(link + '\n')
    log_message(f"Đã lưu liên kết bình luận: {link}")

def exit_program():
    """Hàm để thoát chương trình."""
    log_message("Đang thoát chương trình...")
    root.quit()

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Tool Comment Facebook 2024")
root.geometry("600x600")  # Kích thước cửa sổ
root.configure(bg="#1e1e1e")  # Màu nền tối

# Tạo tiêu đề
title_label = tk.Label(root, text="Tool Comment Facebook 2024", font=("Courier", 20), fg="#00ff00", bg="#1e1e1e")
title_label.pack(pady=10)

# Tạo nút "Thêm tài khoản FB mới"
add_account_button = tk.Button(root, text="Thêm tài khoản FB mới", command=add_facebook_account, bg="#00ff00", fg="#1e1e1e", font=("Courier", 12))
add_account_button.pack(pady=10)

# Tạo danh sách tài khoản Facebook
accounts_list = tk.Listbox(root, width=50, height=10, font=("Courier", 12), bg="#2e2e2e", fg="#00ff00")
accounts_list.pack(pady=10)

# Tạo nút "Chọn tài khoản và chạy tool"
start_tool_button = tk.Button(root, text="Chọn tài khoản và chạy tool", command=start_tool, bg="#00ff00", fg="#1e1e1e", font=("Courier", 12))
start_tool_button.pack(pady=10)

# Tạo nút "Thoát"
exit_button = tk.Button(root, text="Thoát", command=exit_program, bg="#ff0000", fg="#ffffff", font=("Courier", 12))
exit_button.pack(pady=10)

# Tạo bảng hiển thị các thao tác
log_text = scrolledtext.ScrolledText(root, width=70, height=20, font=("Courier", 10), bg="#2e2e2e", fg="#00ff00")
log_text.pack(pady=20)

# Tải danh sách tài khoản khi khởi động
load_accounts()

# Chạy ứng dụng
root.mainloop()
