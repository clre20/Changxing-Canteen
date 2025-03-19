from flask import Flask, Blueprint, render_template, session, redirect, url_for, request, flash
import json, os

# 設定藍圖
loginout_bp = Blueprint('loginout', __name__, template_folder='templates')

# key
loginout_bp.secret_key = 'a_unique_secret_key'  # 設定 secret_key 用來處理 session

# 用戶資料
user_data = 'user.json'

# 讀取用戶資料
def load_users():
    if os.path.exists(user_data):
        with open(user_data, 'r') as f:
            return json.load(f)
    return {}

# 儲存用戶資料
def save_users(users):
    with open(user_data, 'w') as f:
        json.dump(users, f, indent=4)


# 根路由：如果用戶已經登入，重定向到panel
@loginout_bp.route('/')
def index():
    email = session.get('user_email')
    if email:
        return redirect(url_for('panel.user_panel', email=email))
    return redirect(url_for('loginout.login'))

# 登入頁面
@loginout_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 載入用戶資料
        users = load_users()
        
        if email in users and users[email]['password'] == password:
            session['user_email'] = email
            return redirect(url_for('panel.user_panel', email=email))
        else:
            flash('無效的電子郵件或密碼！')
            return redirect(url_for('loginout.login'))
    
    return render_template('login.html')

# 登出
@loginout_bp.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('loginout.login'))

# 註冊頁面
@loginout_bp.route('/register', methods=['GET', 'POST'])
def register():    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = load_users()
        
        if email in users:
            flash('該電子郵件已經註冊！')
        else:
            users[email] = {'email': email, 'password': password, 'tag': 'user'}
            save_users(users)
            flash('註冊成功！請登入')
            return redirect(url_for('loginout.login'))
    
    return render_template('register.html')

# 忘記密碼頁面
@loginout_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # 載入用戶資料
        users = load_users()
        
        if email in users:
            # 設置密碼為 <email>_password
            new_password = f"{email}_password"
            users[email]['password'] = new_password
            save_users(users)
            
            # 提示用戶密碼已恢復並可重新登入
            flash(f'您的密碼已恢復為 {new_password}，請重新登入！')
            return redirect(url_for('loginout.login'))
        else:
            flash('該電子郵件尚未註冊！')
            return redirect(url_for('loginout.forgot_password'))
    
    return render_template('forgot_password.html')

# 修改密碼頁面
@loginout_bp.route('/change_password_<email>', methods=['GET', 'POST'])
def change_password(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('loginout.login'))
    
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        # 載入用戶資料
        users = load_users()
        
        # 檢查舊密碼是否正確
        if email in users and users[email]['password'] == old_password:
            # 更新密碼
            users[email]['password'] = new_password
            save_users(users)
            flash('密碼已成功更改！')
            return redirect(url_for('loginout.user_panel', email=email))
        else:
            flash('舊密碼不正確！')
    
    return render_template('change_password.html', email=email)

# 用戶帳號
@loginout_bp.route('/account_number_<email>', methods=['GET'])
def account_number(email):
    return render_template('account_number.html', email=email)

# 查看帳號頁面
@loginout_bp.route('/info_<email>', methods=['GET'])
def info(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('loginout.login'))
    # 載入用戶資料
    users = load_users()
    if email in users:
        user_info = users[email]
        return render_template('info.html', user_info=user_info)
    else:
        flash('用戶資料未找到！')
        return redirect(url_for('panel.user_panel', email=email))