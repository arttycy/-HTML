import requests
import time
import os
from bs4 import BeautifulSoup

# --- 配置 ---
BASE_URL = "https://www.shenpowang.com"
OUTPUT_FOLDER = "tarot_knowledge_base"  # 文件夹名保持一致

# 设置请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# scrape_and_clean_details 函数保持不变，因为它是我们的测试核心
def scrape_and_clean_details(card_info):
    """从单个卡牌详情页抓取并清洗核心内容"""
    card_url = card_info['url']
    try:
        print(f"正在抓取测试页面: {card_info['title']}")
        response = requests.get(card_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = soup.select_one('.show_cnt')
        
        if not content_div:
            return "未能找到核心内容容器 (.show_cnt)"

        all_text = content_div.get_text(separator='\n', strip=True)
        
        # 我们可以进一步优化清洗逻辑
        # 找到内容的真实起点，通常是标题之后的一段描述
        start_marker = "也是起点" # 这是一个只在“愚人”牌解释中出现的独特句子
        start_index = all_text.find(start_marker)
        
        if start_index != -1:
            # 从标记词之前的一小段开始截取，以包含开头
            # 这个数字-10需要根据实际情况微调
            final_text = all_text[start_index-10:]
        else:
            final_text = all_text # 如果找不到标记，就返回全部内容

        return final_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"抓取详情页失败: {card_url}, 错误: {e}")
        return None

def main_test():
    """专门用于测试单个页面的主函数"""
    print("--- 开始单页抓取测试 ---")

    # 我们手动指定“愚人”这张牌的链接和标题
    test_card = {
      "url": "https://www.shenpowang.com/taluopai/jieshi/d23044.html",
      "title": "塔罗牌愚人（The Fool）"
    }
    
    # 确保输出文件夹存在
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"已创建输出文件夹: {OUTPUT_FOLDER}")
    
    # 调用抓取函数
    cleaned_content = scrape_and_clean_details(test_card)

    if cleaned_content:
        # 清理文件名中不合法字符
        safe_filename = "_test_output_" + test_card['title'].replace('（', '(').replace('）',')').replace('/', '_') + ".txt"
        filepath = os.path.join(OUTPUT_FOLDER, safe_filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"\n测试成功！已将抓取内容保存到文件: {filepath}")
        except IOError as e:
            print(f"保存文件失败: {filepath}, 错误: {e}")
    else:
        print("\n测试失败，未能抓取到任何内容。")


if __name__ == '__main__':
    main_test() # 注意：我们现在调用的是测试函数 main_test()