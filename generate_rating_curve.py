import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

# 你的 Codeforces 用户名
CF_HANDLE = "InsaneArrogant"

def fetch_rating_history(handle):
    """获取用户的 rating 历史记录（比赛数据）"""
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    resp = requests.get(url)
    data = resp.json()
    if data['status'] != 'OK':
        raise Exception(f"API error: {data.get('comment')}")
    contests = data['result']
    # 按时间排序（API 返回的默认按时间升序）
    dates = [datetime.fromtimestamp(c['ratingUpdateTimeSeconds']) for c in contests]
    ratings = [c['newRating'] for c in contests]
    return dates, ratings

def plot_rating_curve(dates, ratings):
    if not dates:
        print("没有 rating 历史数据")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, ratings, marker='o', linestyle='-', linewidth=2, markersize=4, color='#FF6B6B')
    
    # 标注最高分
    max_rating = max(ratings)
    max_idx = ratings.index(max_rating)
    ax.annotate(f'Peak: {max_rating}', xy=(dates[max_idx], max_rating),
                xytext=(dates[max_idx], max_rating + 50),
                arrowprops=dict(arrowstyle='->', color='gray'),
                fontsize=9, ha='center')
    
    # 标注当前分
    current_rating = ratings[-1]
    ax.annotate(f'Current: {current_rating}', xy=(dates[-1], current_rating),
                xytext=(dates[-1], current_rating - 80),
                arrowprops=dict(arrowstyle='->', color='gray'),
                fontsize=9, ha='center')
    
    # 设置标题和轴标签
    ax.set_title(f'{CF_HANDLE} - Codeforces Rating History', fontsize=14)
    ax.set_xlabel('Contest Date')
    ax.set_ylabel('Rating')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 格式化 x 轴日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # 设置 y 轴范围（留一些边距）
    min_rating = min(ratings)
    ax.set_ylim(max(0, min_rating - 100), max_rating + 150)
    
    plt.tight_layout()
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/rating_curve.svg', format='svg')
    plt.close()
    print("✅ Rating 曲线图已生成: output/rating_curve.svg")

if __name__ == '__main__':
    print(f"正在获取 {CF_HANDLE} 的 rating 历史...")
    dates, ratings = fetch_rating_history(CF_HANDLE)
    print(f"共参与 {len(dates)} 场比赛")
    plot_rating_curve(dates, ratings)
