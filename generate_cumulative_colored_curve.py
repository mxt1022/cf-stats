import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from collections import defaultdict

CF_HANDLE = "InsaneArrogant"  # 替换成你的用户名

# 难度区间及颜色（CF 标准）
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
    submissions.sort(key=lambda x: x['date'])
    return submissions

def aggregate_cumulative_by_month(submissions):
    """
    按月累积统计每个难度区间的解题数量
    返回: {
        'dates': [datetime, ...],
        'cumulative': {
            'Grey': [count, ...],
            'Green': [...],
            ...
        }
    }
    """
    if not submissions:
        return None
    # 确定时间范围：从第一个提交的月份到最后一个提交的月份
    start_date = submissions[0]['date'].replace(day=1)
    end_date = submissions[-1]['date'].replace(day=1)
    # 生成所有月份
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        # 下个月
        if current.month == 12:
            current = current.replace(year=current.year+1, month=1)
        else:
            current = current.replace(month=current.month+1)
    
    # 初始化累积计数器
    diff_names = [name for (_, _, _, name) in DIFFICULTY_RANGES]
    cumulative = {name: [0]*len(dates) for name in diff_names}
    
    # 遍历提交，填充累积数据
    sub_idx = 0
    for i, month_date in enumerate(dates):
        # 复制上一个月的累积值（如果有）
        if i > 0:
            for name in diff_names:
                cumulative[name][i] = cumulative[name][i-1]
        # 添加本月内提交的题目
        while sub_idx < len(submissions):
            sub_date = submissions[sub_idx]['date']
            if sub_date.year == month_date.year and sub_date.month == month_date.month:
                rating = submissions[sub_idx]['rating']
                diff_name = get_rating_range_name(rating)
                cumulative[diff_name][i] += 1
                sub_idx += 1
            else:
                break
    return {'dates': dates, 'cumulative': cumulative}

def plot_cumulative_trends(data):
    dates = data['dates']
    cumulative = data['cumulative']
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 绘制每个难度区间的累积曲线
    for low, high, color, name in DIFFICULTY_RANGES:
        values = cumulative[name]
        if max(values) > 0:  # 只绘制有数据的区间
            ax.plot(dates, values, label=name, color=color, linewidth=2, marker='o', markersize=3)
    
    ax.set_title(f"{CF_HANDLE} - Cumulative Solved Problems by Difficulty (Monthly)", fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Count")
    ax.legend(loc='upper left', title="Difficulty")
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 格式化 X 轴日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/cumulative_trends.svg', format='svg')
    plt.close()
    print("✅ 累积趋势图已生成: output/cumulative_trends.svg")

if __name__ == '__main__':
    subs = fetch_accepted_submissions(CF_HANDLE)
    print(f"获取到 {len(subs)} 条有评分的 AC 记录")
    data = aggregate_cumulative_by_month(subs)
    if data:
        plot_cumulative_trends(data)
    else:
        print("没有足够的数据生成图表")
