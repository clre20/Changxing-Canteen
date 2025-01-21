import Cmail
import random
import json

def run_mail_one(email, title, t):
    key = "one"

    to_email = email

    print(to_email)

    # to_email=["smart960710@gmail.com", "11305230@mail2.ccvs.kh.edu.tw", "11305231@mail2.ccvs.kh.edu.tw"]

    # t = random.randint(1,10)        # 产生 1 到 10 的一个整数型随机数

    # title=f"編號:{t}"
    # print({title})

    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    html = read_file(f'{t}.html')
    css = read_file('Cmail/style.css')

    Cmail.email(to_email, title, html, css, key)

def run_mail_all(title, t):
    key = "all"

    with open('user.json', 'r') as file:
        data = json.load(file)

    # 從data中提取所有的email
    to_email = [user_info['email'] for user_info in data.values()]
    print(type(to_email))
    print(to_email)

    # to_email=["smart960710@gmail.com", "11305230@mail2.ccvs.kh.edu.tw", "11305231@mail2.ccvs.kh.edu.tw"]

    # t = random.randint(1,10)        # 产生 1 到 10 的一个整数型随机数

    # title=f"編號:{t}"
    # print({title})

    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    html = read_file(f'{t}.html')
    css = read_file('Cmail/style.css')

    Cmail.email(to_email, title, html, css, key)

# email = "11305231@mail2.ccvs.kh.edu.tw"
#email = "smart960710@gmail.com" #設定收件者
#title = "測試通知" # 設定標題
#t = "Cmail/Cmail_register" # 設定發送的檔案
#t = "Cmail/Cmail_list" # 設定發送的檔案
#t = "Cmail/Cmail_order_food" # 設定發送的檔案
#run_mail(email, title, t)