import requests
import json
import time
from bs4 import BeautifulSoup

# --- 配置 ---
BASE_URL = "https://www.shenpowang.com"
INDEX_URL = "https://www.shenpowang.com/taluopai/jieshi/"
# 设置请求头，模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_all_card_links():
    """第一步：从主页面获取所有塔罗牌详情页的链接"""
    print("开始获取所有卡牌链接...")
    try:
        response = requests.get(INDEX_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = []
        # ▼▼▼ 确认这里的选择器是正确的 ▼▼▼
        for a_tag in soup.select('.taluo_jieshi a'):
            if a_tag.has_attr('href'):
                # 拼接成完整的 URL
                full_url = BASE_URL + a_tag['href']
                links.append(full_url)
        
        print(f"成功找到 {len(links)} 个卡牌链接。")
        return links
    except requests.exceptions.RequestException as e:
        print(f"获取主页面失败: {e}")
        return []

def scrape_card_details(card_url):
    """第二步：从单个卡牌详情页抓取信息"""
    try:
        print(f"正在抓取: {card_url}")
        response = requests.get(card_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 注意：这些 CSS 选择器也需要根据实际页面结构进行分析和可能的微调
        card_data = {}
        
        # 提取牌名 (例如 "0号牌 愚人 The Fool")
        title_tag = soup.select_one('.arc_title h1')
        card_data['title'] = title_tag.text.strip() if title_tag else "未知标题"
        
        # 提取所有的解读文本内容
        # 这里我们将所有 class="content" 的 div 下的 p 标签内容合并
        content_paragraphs = soup.select('.content p')
        full_text = "\n".join([p.text.strip() for p in content_paragraphs])
        card_data['interpretation'] = full_text
        
        card_data['source_url'] = card_url
        
        return card_data
    except requests.exceptions.RequestException as e:
        print(f"抓取详情页失败: {card_url}, 错误: {e}")
        return None

def main():
    """主函数：执行整个爬取和保存流程"""
    card_links = get_all_card_links()
    
    if not card_links:
        print("未能获取到任何卡牌链接，程序退出。")
        return

    all_tarot_data = []
    for link in card_links:
        details = scrape_card_details(link)
        if details:
            all_tarot_data.append(details)
        
        # 做一个有礼貌的爬虫，每次请求后暂停一小段时间
        time.sleep(1) # 暂停1秒

    # 第三步：将所有数据保存到 JSON 文件
    output_filename = 'tarot_knowledge_base.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 确保中文字符能正确写入
        # indent=2 让 JSON 文件格式更美观，易于阅读
        json.dump(all_tarot_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n任务完成！所有数据已成功保存到 {output_filename}")
    print(f"共保存了 {len(all_tarot_data)} 张卡牌的信息。")


if __name__ == '__main__':
    main()