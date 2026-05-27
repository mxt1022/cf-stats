import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

CF_HANDLE = "InsaneArrogant"   # 替换成你的用户名

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

def get_color_for_rating(rating):
    for low, high, color, _ in DIFFICULTY_RANGES:
        if low <= rating <= high:
            return color
    return '#000000'

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

def plot_cumulative_colored_curve(submissions):
    if not submissions:
        print("没有带 rating 的 AC 记录")
        return
    
    # 计算累积数量
    cumulative_counts = list(range(1, len(submissions) + 1))
    dates = [s['date'] for s in submissions]
    ratings = [s['rating'] for s in submissions]
    colors = [get_color_for_rating(r) for r in ratings]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 分段绘制折线，每段颜色由该点的题目难度决定
    # 方法：依次连接相邻点，使用前一个点的颜色（或后一个点）
    for i in range(len(dates) - 1):
        ax.plot([dates[i], dates[i+1]], [cumulative_counts[i], cumulative_counts[i+1]],
                color=colors[i], linewidth=2, solid_capstyle='round')
    
    # 添加散点标记（可选）
    ax.scatter(dates, cumulative_counts, c=colors, s=10, zorder=5, edgecolors='none')
    
    # 设置标题和标签
    ax.set_title(f"{CF_HANDLE} - Cumulative AC Problems Colored by Difficulty", fontsize=14)
    ax.set_xlabel("Submission Date")
    ax.set_ylabel("Cumulative Accepted Count")
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 格式化 X 轴日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # 添加图例（使用手动图例）
    from matplotlib.lines import Line2D
    legend_elements = []
    for low, high, color, name in DIFFICULTY_RANGES:
        legend_elements.append(Line2D([0], [0], color=color, lw=2, label=f"{name} ({low}-{high})"))
    ax.legend(handles=legend_elements, loc='upper left', title="Difficulty")
    
    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/cumulative_colored_curve.svg', format='svg')
    plt.close()
    print("✅ 累积彩色曲线图已生成: output/cumulative_colored_curve.svg")

if __name__ == '__main__':
    subs = fetch_accepted_submissions(CF_HANDLE)
    print(f"获取到 {len(subs)} 条有评分的 AC 记录")
    plot_cumulative_colored_curve(subs)
