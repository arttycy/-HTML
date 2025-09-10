import requests
import json
import time
import os
from bs4 import BeautifulSoup

# --- 配置 ---
BASE_URL = "https://www.shenpowang.com"
INDEX_URL = "https://www.shenpowang.com/taluopai/jieshi/"
OUTPUT_FOLDER = "tarot_knowledge_base"  # 我们将把78个txt文件保存在这个文件夹里

# 设置请求头，模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_all_card_links():
    """从主页面获取所有塔罗牌详情页的链接和标题"""
    print("步骤 1/3: 开始获取所有卡牌链接...")
    try:
        response = requests.get(INDEX_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cards = []
        # 使用我们确定的正确选择器 '.taluo_jieshi a'
        for a_tag in soup.select('.taluo_jieshi a'):
            if a_tag.has_attr('href') and a_tag.has_attr('title'):
                card_info = {
                    "url": BASE_URL + a_tag['href'],
                    "title": a_tag['title'].replace("解释", "").replace("解读", "") # 清理标题
                }
                cards.append(card_info)
        
        print(f"成功找到 {len(cards)} 个卡牌链接。")
        return cards
    except requests.exceptions.RequestException as e:
        print(f"获取主页面失败: {e}")
        return []

def scrape_and_clean_details(card_info):
    """从单个卡牌详情页抓取并清洗核心内容"""
    card_url = card_info['url']
    try:
        print(f"抓取: {card_info['title']}")
        response = requests.get(card_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 精确定位包含所有核心内容的 div 容器
        content_div = soup.select_one('.show_cnt')
        
        if not content_div:
            return "未能找到核心内容容器 (.show_cnt)"

        # 提取该容器内的所有文本，并进行清洗
        all_text = content_div.get_text(separator='\n', strip=True)
        
        # 根据你提供的起止点，我们可以进一步精确截取
        # 但通常提取整个 .show_cnt 已经足够干净，因为它不包含侧边栏和页脚
        # 如果需要更精确，可以像下面这样做：
        start_marker = card_info['title']
        end_marker = "相关阅读" # 我们知道内容在此之前结束

        # 简单的截取逻辑
        start_index = all_text.find(start_marker)
        if start_index != -1:
             # 从标题之后开始截取，避免包含标题本身
            all_text = all_text[start_index + len(start_marker):]

        return all_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"抓取详情页失败: {card_url}, 错误: {e}")
        return None

def main():
    """主函数：执行爬取、清洗并生成78个TXT文件"""
    # 确保输出文件夹存在
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"已创建输出文件夹: {OUTPUT_FOLDER}")

    all_cards = get_all_card_links()
    
    if not all_cards:
        print("未能获取到任何卡牌链接，程序退出。")
        return

    print(f"\n步骤 2/3: 开始循环抓取 {len(all_cards)} 个页面的详细内容...")
    
    saved_count = 0
    for card in all_cards:
        cleaned_content = scrape_and_clean_details(card)
        
        if cleaned_content:
            # 清理文件名中不合法字符
            safe_filename = card['title'].replace('（', '(').replace('）',')').replace('/', '_') + ".txt"
            filepath = os.path.join(OUTPUT_FOLDER, safe_filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                saved_count += 1
            except IOError as e:
                print(f"保存文件失败: {filepath}, 错误: {e}")

        # 做一个有礼貌的爬虫，每次请求后暂停
        time.sleep(0.5) # 暂停 0.5 秒

    print(f"\n步骤 3/3: 任务完成！")
    print(f"成功处理并保存了 {saved_count} 个TXT文件到 '{OUTPUT_FOLDER}' 文件夹中。")

if __name__ == '__main__':
    main()