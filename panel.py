from flask import Flask, Blueprint, render_template, session, redirect, url_for

# 設定藍圖
panel_bp = Blueprint('panel', __name__, template_folder='templates')

# key
panel_bp.secret_key = 'a_unique_secret_key'  # 設定 secret_key 用來處理 session

# 用戶面板
@panel_bp.route('/user_panel_<email>', methods=['GET'])
def user_panel(email):
    if 'user_email' not in session or session['user_email'] != email:
        return redirect(url_for('panel.login'))
    return render_template('user_panel.html', email=email)