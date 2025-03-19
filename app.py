from flask import Flask, render_template
from weekly import weekly_bp
from loginout import loginout_bp
from panel import panel_bp

app = Flask(__name__)
# key
app.secret_key = 'a_unique_secret_key'  # 設定 secret_key 用來處理 session

# 藍圖註冊
app.register_blueprint(weekly_bp)
app.register_blueprint(loginout_bp)
app.register_blueprint(panel_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20024, debug=True)