import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
'''
def email(to_email, title, t, html, css):
    print(f"Cmail.py收到了--{to_email}--{title}--{t}--{html}--{css}")
    # 配置郵件信息
    smtp_server = 'smtp.gmail.com'
    port = 587
    sender_email = '你的信箱'
    password = '密碼'
    receiver_email = to_email  # 使用參數中的收件人電子郵件
    name = "長興食堂"

    # HTML 模板-註冊
    html_template_register = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {css}
        </style>
    </head>
    <body>
        {html}
        <h3>帳號資訊</h3>
        <br>
        電子郵件：{email}
        </div>
    </body>
    </html>
    """
    # HTML 模板-點餐
    html_template_order_food = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {css}
        </style>
    </head>
    <body>
        {html}
        </div>
    </body>
    </html>
    """
    # HTML 模板-註冊
    html_template_list = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            
        </style>
    </head>
    <body>
        3
        {html}
    </body>
    </html>
    """
    # HTML 模板-註冊
    html_template_ERROR = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            
        </style>
    </head>
    <body>
        4
        {html}
    </body>
    </html>
    """
    #print(f"t={t}")
    if t == "Cmail/Cmail_register":
        html_template = html_template_register
    elif t == "Cmail/Cmail_order_food":
        html_template = html_template_order_food
    elif t == "Cmail/Cmail_list":
        html_template = html_template_list
    else:
        html_template = html_template_ERROR
    #print(f"{html_template}")
    # 插入變數到 HTML
    html_content = html_template.format(css=css, html=html)#, email=to_email)
    #print(f"html_content type: {type(html_content)}") # 應該輸出 <class 'str'>
    #print(f"html_content: {html_content}") # 打印 html_content 內容
    # 創建郵件
    msg = MIMEMultipart("alternative")
    msg['From'] = f"{name}"
    msg['To'] = receiver_email
    msg['Subject'] = f"{title}"
    #print(f"msg type: {type(msg)}") # 應該輸出 <class 'email.mime.multipart.MIMEMultipart'>
    # 附加 HTML 內容
    msg.attach(MIMEText(html_content, "html"))
    
    # 發送郵件
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("郵件發送成功！")
    except Exception as e:
        print(f"發送郵件時出錯：{e}")
'''

def email(to_email, title, html, css, key):
    # 配置郵件信息
    sender_name = "長興食堂"  # 顯示名稱
    sender_email = "smart96071031@gmail.com"
    sender_password = "ftah zivh udvv dsjd"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 建立郵件內容
    msg = MIMEMultipart()
    msg['From'] = msg['From'] = f"{sender_name}"  # 顯示名稱與郵箱地址
    if key == "one":
        msg['To'] = to_email
    elif key == "all":
        msg['To'] = ",".join(to_email)
    msg['Subject'] = title
    
    # 讀取文件內容
    html_content = html
    css_content = css

    # 合併 HTML、CSS 和 JavaScript 的內容
    combined_content = f"""
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <style>
            {css_content}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # 添加 HTML 內容
    
    msg.attach(MIMEText(combined_content, 'html'))

    # 發送郵件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print("郵件發送成功！")
    except Exception as e:
        print(f"郵件發送失敗: {e}")
