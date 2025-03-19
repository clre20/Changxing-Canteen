from flask import Flask, Blueprint, render_template, request, redirect, url_for
from datetime import date, timedelta
import json, os

weekly_bp = Blueprint('weekly', __name__, template_folder='templates')

# 設定 secret_key 用來處理 session
weekly_bp.secret_key = 'a_unique_secret_key'

@weekly_bp.route("/list")
def list():
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    today = date.today()
    # 以星期一作為一週的起點
    current_monday = today - timedelta(days=today.weekday())
    start_of_week = current_monday + timedelta(weeks=offset)

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    days = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        formatted_date = day_date.strftime("%m/%d")
        full_date = day_date.strftime("%Y%m%d")  # 完整日期格式：年月日
        days.append({"date": formatted_date, "weekday": weekdays[i], "date_full": full_date})
    
    # 讀取 meals.json 來取得餐點資料
    meals_path = os.path.join(weekly_bp.root_path, 'meals.json')
    with open(meals_path, 'r', encoding='utf-8') as f:
        meals = json.load(f)

    # 讀取 meals_ok.json，改用字典結構，直接以日期為 key
    meals_ok_path = os.path.join(weekly_bp.root_path, 'meals_ok.json')
    try:
        with open(meals_ok_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        meals_ok = data
    except Exception:
        meals_ok = {}

    return render_template("calendar.html", days=days, offset=offset, meals=meals, meals_ok=meals_ok)

@weekly_bp.route("/save_meals", methods=["POST"])
def save_meals():
    selected_items = request.form.getlist("selected")  # 使用者選取的餐點
    selected_date = request.form.get("selectedDate")   # 所屬日期 (YYYYMMDD)

    # 讀取 meals.json 來取得餐點資料
    meals_path = os.path.join(weekly_bp.root_path, 'meals.json')
    with open(meals_path, 'r', encoding='utf-8') as f:
        meals = json.load(f)

    # 建立當前選擇的結構
    new_selections = {}
    for item in selected_items:
        parts = item.split("|")  # 格式 "group_key|i"
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

    # 讀取現有的 meals_ok.json (以字典方式儲存)
    meals_ok_path = os.path.join(weekly_bp.root_path, 'meals_ok.json')
    try:
        with open(meals_ok_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    # 若該日期已存在，則進行合併
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
