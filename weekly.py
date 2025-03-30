from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify, session
from datetime import date, timedelta
import json, os

weekly_bp = Blueprint('weekly', __name__, template_folder='templates')

# 設定 secret_key 用來處理 session
weekly_bp.secret_key = 'a_unique_secret_key'

# 用戶資料檔案路徑
USER_DATA_FILE = 'user.json'

# 讀取用戶資料的函數
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@weekly_bp.route("/list")
def list():
    # 檢查是否已登錄
    if 'user_email' not in session:
        return redirect(url_for('loginout.login'))

    # 根據 session 中的 user_email 獲取用戶 tag
    user_email = session['user_email']
    users = load_users()
    user_tag = users.get(user_email, {}).get('tag', 'user')  # 預設為 "user" 如果找不到

    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    start_of_week = current_monday + timedelta(weeks=offset)

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    days = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        formatted_date = day_date.strftime("%m/%d")
        full_date = day_date.strftime("%Y%m%d")
        days.append({"date": formatted_date, "weekday": weekdays[i], "date_full": full_date})
    
    # 讀取 meals.json
    meals_path = os.path.join(weekly_bp.root_path, 'meals.json')
    with open(meals_path, 'r', encoding='utf-8') as f:
        meals = json.load(f)

    # 讀取 meals_ok.json
    meals_ok_path = os.path.join(weekly_bp.root_path, 'meals_ok.json')
    try:
        with open(meals_ok_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        meals_ok = data
    except Exception:
        meals_ok = {}
    
    # 確保 meals_ok 中包含所有日期的初始值
    for day in days:
        if day["date_full"] not in meals_ok:
            meals_ok[day["date_full"]] = {"selections": {}, "confirmed": False}

    return render_template("calendar.html", days=days, offset=offset, meals=meals, meals_ok=meals_ok, user_tag=user_tag)

@weekly_bp.route("/save_meals", methods=["POST"])
def save_meals():
    selected_items = request.form.getlist("selected")
    selected_date = request.form.get("selectedDate")

    meals_path = os.path.join(weekly_bp.root_path, 'meals.json')
    with open(meals_path, 'r', encoding='utf-8') as f:
        meals = json.load(f)

    new_selections = {}
    for item in selected_items:
        parts = item.split("|")
        if len(parts) != 2:
            continue
        group_key, index = parts
        if group_key not in meals:
            continue
        group = meals[group_key]
        content_key = "content" + index
        image_key = "image" + index
        if content_key in group and image_key in group:
            if group_key not in new_selections:
                new_selections[group_key] = {
                    "title": group["title"],
                    "selections": []
                }
            new_selections[group_key]["selections"].append({
                "content": group[content_key],
                "image": group[image_key]
            })

    meals_ok_path = os.path.join(weekly_bp.root_path, 'meals_ok.json')
    try:
        with open(meals_ok_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    if selected_date in data:
        for group_key, new_group in new_selections.items():
            if group_key in data[selected_date]["selections"]:
                existing_items = {item["content"] for item in data[selected_date]["selections"][group_key]["selections"]}
                for item in new_group["selections"]:
                    if item["content"] not in existing_items:
                        data[selected_date]["selections"][group_key]["selections"].append(item)
            else:
                data[selected_date]["selections"][group_key] = new_group
    else:
        data[selected_date] = {"selections": new_selections}

    with open(meals_ok_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return redirect(url_for("weekly.list"))

MEALS_OK_FILE = 'meals_ok.json'
def load_meals():
    with open(MEALS_OK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_meals(data):
    with open(MEALS_OK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@weekly_bp.route('/delete_meal', methods=['POST'])
def delete_meal():
    data = request.get_json()
    date = data.get('date')
    group = data.get('group')
    index = data.get('index')
    meals = load_meals()
    try:
        meals[date]['selections'][group]['selections'].pop(index)
        save_meals(meals)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@weekly_bp.route('/confirm_day', methods=['POST'])
def confirm_day():
    data = request.get_json()
    date = data.get('date')
    meals = load_meals()
    try:
        if date in meals:
            meals[date]['confirmed'] = True
        else:
            meals[date] = {"selections": {}, "confirmed": True}
        save_meals(meals)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))