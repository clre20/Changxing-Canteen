from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
import run_Cmail

app = Flask(__name__)
app.secret_key = 'a_unique_secret_key'  # 設定 secret_key 用來處理 session

# 用戶資料儲存在 JSON 檔案中
USER_DATA_FILE = 'user.json'

# 讀取 JSON 文件
def load_meals():
    with open('meals.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 讀取 meals_list.json 文件
def load_meals_list():
    try:
        with open('meals_list.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 保存更新後的 meals_list.json 文件
def save_meals_list(meals_data):
    with open('meals_list.json', 'w', encoding='utf-8') as file:
        json.dump(meals_data, file, ensure_ascii=False, indent=4)

# 讀取 list_ok.json 文件
def load_list_ok():
    try:
        with open('list_ok.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 保存 list_ok.json 文件
def save_list_ok(data):
    with open('list_ok.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 獲取特定用戶的tag 
def get_user_tag(email):
    users = load_users()
    user = users.get(email)
    if user:
        return user.get('tag')
    return None

# 讀取用戶資料
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# 儲存用戶資料
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


# 根路由：如果用戶已經登入，重定向到對應的個人面板
@app.route('/')
def index():
    email = session.get('user_email')
    if email:
        return redirect(url_for('user_panel', email=email))
    return redirect(url_for('login'))

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 載入用戶資料
        users = load_users()
        
        if email in users and users[email]['password'] == password:
            session['user_email'] = email
            return redirect(url_for('user_panel', email=email))
        else:
            flash('無效的電子郵件或密碼！')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# 用戶面板
@app.route('/user_panel_<email>', methods=['GET'])
def user_panel(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('login'))
    return render_template('user_panel.html', email=email)

# 登出
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login'))

# 註冊頁面
@app.route('/register', methods=['GET', 'POST'])
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
            
            # 發送信件通知-設定
            title = "註冊成功通知"
            t = "Cmail/Cmail_register"
            # 發送信件通知
            run_Cmail.run_mail_one(email, title, t)
            return redirect(url_for('login'))
    
    return render_template('register.html')

# 忘記密碼頁面
@app.route('/forgot_password', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))
        else:
            flash('該電子郵件尚未註冊！')
            return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')

# 修改密碼頁面
@app.route('/change_password_<email>', methods=['GET', 'POST'])
def change_password(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('login'))
    
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
            return redirect(url_for('user_panel', email=email))
        else:
            flash('舊密碼不正確！')
    
    return render_template('change_password.html', email=email)

# 查看帳號頁面
@app.route('/view_account_<email>', methods=['GET'])
def view_account(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('login'))
    
    # 載入用戶資料
    users = load_users()
    
    if email in users:
        user_info = users[email]
        return render_template('view_account.html', user_info=user_info)
    else:
        flash('用戶資料未找到！')
        return redirect(url_for('user_panel', email=email))

# 點餐頁面
@app.route('/order_food_<email>')
def order_food(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('login'))
    # 載入用戶資料
    users = load_users()
    
    if email in users:
        user_info = users[email]
        meals_data = load_meals()  # 從 meals.json 讀取數據
        return render_template('order_food.html', user_info=user_info, meals=meals_data)
    else:
        flash('用戶資料未找到！')
        return redirect(url_for('user_panel', email=email))

# 儲存點餐選擇頁面
@app.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.get_json()
    selected = data.get('selected', [])

    meals_data = load_meals_list()
    meals_info = load_meals()

    # 更新選擇的項目，保留原有資料
    for item in selected:
        try:
            meal_id, content_id = item.split('-')
            content_key = f"content{content_id}"
            image_key = f"image{content_id}"
            if meal_id in meals_info:
                if meal_id not in meals_data:
                    meals_data[meal_id] = {}
                content_value = meals_info[meal_id].get(content_key, "")
                image_value = meals_info[meal_id].get(image_key, "")
                meals_data[meal_id][content_key] = content_value
                meals_data[meal_id][image_key] = image_value
        except ValueError:
            flash('點餐失敗！')
            continue

    save_meals_list(meals_data)
    # 發送信件通知-設定
    title = "點餐通知"
    t = "Cmail/Cmail_order_food"
    # 發送信件通知
    run_Cmail.run_mail_all(title, t)
    flash('點餐成功！')
    return jsonify({"message": "選擇已儲存", "updated_meals": meals_data}), 200

# 希望餐點和大廚嚴選查看
@app.route('/list_<email>')
def list(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('user_panel'))

    meals_list = load_meals_list()  # 載入 meals_list.json
    list_ok = load_list_ok()  # 載入 list_ok.json
    
    tag = get_user_tag(email)
    
    return render_template('list.html', email=email, meals_list=meals_list, list_ok=list_ok, tag=tag)

# 新增項目至新的 JSON 文件，並從 meals_list.json 中刪除
@app.route('/ok_item/<key>/<item_key>', methods=['POST'])
def ok_item(key, item_key):
    meals_data = load_meals_list()
    list_ok_data = {}

    # 嘗試讀取 list_ok.json 文件，如果存在則載入
    if os.path.exists('list_ok.json'):
        with open('list_ok.json', 'r', encoding='utf-8') as file:
            list_ok_data = json.load(file)

    if key in meals_data and item_key in meals_data[key]:
        if key not in list_ok_data:
            list_ok_data[key] = {}
        content_key = item_key.replace('image', 'content')
        list_ok_data[key][item_key] = meals_data[key][item_key]
        list_ok_data[key][content_key] = meals_data[key][content_key]

        # 保存 list_ok.json 文件
        with open('list_ok.json', 'w', encoding='utf-8') as file:
            json.dump(list_ok_data, file, ensure_ascii=False, indent=4)

        # 從 meals_list.json 中刪除對應的項目
        del meals_data[key][item_key]
        if content_key in meals_data[key]:
            del meals_data[key][content_key]

        save_meals_list(meals_data)

        return jsonify({"message": "Item added to list_ok.json and deleted from meals_list.json"}), 200
    return jsonify({"message": "Item not found"}), 404

# 從 list_ok.json 中刪除項目並重新加入 meals_list.json
@app.route('/remove_ok_item/<key>/<item_key>', methods=['DELETE'])
def remove_ok_item(key, item_key):
    list_ok_data = load_list_ok()  # 使用 load_list_ok 函數讀取 list_ok.json
    meals_data = load_meals_list()  # 使用 load_meals_list 函數讀取 meals_list.json

    if key in list_ok_data and item_key in list_ok_data[key]:
        if key not in meals_data:
            meals_data[key] = {}
        content_key = item_key.replace('image', 'content')
        meals_data[key][item_key] = list_ok_data[key][item_key]
        meals_data[key][content_key] = list_ok_data[key][content_key]

        # 保存 meals_list.json 文件
        save_meals_list(meals_data)  # 使用 save_meals_list 函數保存 meals_list.json

        # 從 list_ok.json 中刪除對應的項目
        del list_ok_data[key][item_key]
        if content_key in list_ok_data[key]:
            del list_ok_data[key][content_key]

        save_list_ok(list_ok_data)  # 使用 save_list_ok 函數保存 list_ok.json

        return jsonify({"message": "Item removed from list_ok.json and added to meals_list.json"}), 200
    return jsonify({"message": "Item not found"}), 404

# 大廚確認餐點
@app.route('/confirm_<email>')
def confirm(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('user_panel'))    
    tag = get_user_tag(email)
    return render_template('confirm.html', email=email, tag=tag)

# 大廚確認餐點後清除希望餐點
@app.route('/clear_meals_list', methods=['POST'])
def clear_meals_list():
    try:
        # 清空 meals_list.json 文件的內容
        save_meals_list({})
        email = request.args.get('email')  # 獲取用戶的 email
        # 發送信件通知-設定
        title = "大廚嚴選通知"
        t = "Cmail/Cmail_list"
        # 發送信件通知
        run_Cmail.run_mail_all(title, t)
        flash('確認成功，已清空希望餐點！')
        return jsonify({'message': 'meals_list.json 已成功清空', 'redirect': url_for('user_panel', email=email)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23444, debug=True)
