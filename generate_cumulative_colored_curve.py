import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from collections import defaultdict
import calendar

CF_HANDLE = "InsaneArrogant"  # 替换为你的用户名

# 难度区间及对应颜色（CF 标准）
DIFFICULTY_RANGES = [
    (0, 1199, '#CCCCCC', 'Grey'),
    (1200, 1599, '#77FF77', 'Green'),
    (1600, 1999, '#77DDFF', 'Cyan'),
    (2000, 2399, '#AAAAFF', 'Blue'),
    (2400, 2999, '#FF88FF', 'Violet'),
    (3000, 3499, '#FFCC88', 'Orange'),
    (3500, 4000, '#FF7777', 'Red')
]

def get_rating_range_name(rating):
    for low, high, _, name in DIFFICULTY_RANGES:
        if low <= rating <= high:
            return name
    return 'Unknown'

def fetch_accepted_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    resp = requests.get(url)
    data = resp.json()
    if data['status'] != 'OK':
        raise Exception(f"API error: {data.get('comment')}")
    submissions = []
    for sub in data['result']:
        if sub.get('verdict') == 'OK':
            problem = sub['problem']
            rating = problem.get('rating')
            if rating is not None:
                submissions.append({
                    'date': datetime.fromtimestamp(sub['creationTimeSeconds']),
                    'rating': rating
                })
    return submissions

def aggregate_by_month(submissions):
    # { (year, month): { difficulty_name: count } }
    monthly = defaultdict(lambda: defaultdict(int))
    for sub in submissions:
        year = sub['date'].year
        month = sub['date'].month
        rating = sub['rating']
        diff_name = get_rating_range_name(rating)
        monthly[(year, month)][diff_name] += 1
    return monthly

def plot_stacked_bar(monthly_data):
    if not monthly_data:
        print("没有数据")
        return
    
    # 排序月份
    sorted_months = sorted(monthly_data.keys())
    # 生成月份标签
    month_labels = [f"{y}-{m:02d}" for y, m in sorted_months]
    
    # 准备每个难度区间的数据列表
    diff_names = [name for (_, _, _, name) in DIFFICULTY_RANGES]
    diff_colors = [color for (_, _, color, _) in DIFFICULTY_RANGES]
    data_by_diff = {name: [] for name in diff_names}
    for ym in sorted_months:
        for name in diff_names:
            data_by_diff[name].append(monthly_data[ym].get(name, 0))
    
    # 绘制堆叠柱状图
    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = [0] * len(sorted_months)
    for name, color in zip(diff_names, diff_colors):
        values = data_by_diff[name]
        if max(values) > 0:
            ax.bar(month_labels, values, bottom=bottom, label=name, color=color, edgecolor='white', linewidth=0.5)
            bottom = [bottom[i] + values[i] for i in range(len(values))]
    
    ax.set_title(f"{CF_HANDLE} - Monthly Solved Problems by Difficulty", fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Solved Problems")
    ax.legend(loc='upper left', title="Difficulty")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/stacked_bar.svg', format='svg')
    plt.close()
    print("✅ 堆叠柱状图已生成: output/stacked_bar.svg")

if __name__ == '__main__':
    subs = fetch_accepted_submissions(CF_HANDLE)
    print(f"获取到 {len(subs)} 条有评分的 AC 记录")
    monthly = aggregate_by_month(subs)
    print(f"涉及 {len(monthly)} 个月份")
    plot_stacked_bar(monthly)
