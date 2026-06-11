from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import os
import random
import time  # 引入時間模組，用來模擬網路爬蟲的傳輸延遲

main_bp = Blueprint('main', __name__)

def fetch_realtime_clothing_data(brand, gender, clothing_type, min_price, max_price):
    """
    【核心技術：即時網路爬蟲與數據清洗引擎】
    模擬 Requests 與 BeautifulSoup 爬取各大品牌官網並即時動態生成資料
    """
    # 模擬真實爬蟲在網路世界等待回應的傳輸延遲（讓前端的轉圈圈動畫更逼真！）
    time.sleep(1.5) 
    
    # 【已過濾人像】全新純商品平拍、掛拍高品質圖片池 - 新增 type 標籤
    mock_pool = [
        # T-shirt 系列
        {"type": "T-shirt", "title": "高質感重磅純棉微廓形上衣", "price_base": 590, "rating": 4.5, "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500"},
        {"type": "T-shirt", "title": "美式復古學院風印花短袖", "price_base": 490, "rating": 4.3, "img": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500"},
        {"type": "T-shirt", "title": "極簡生活系列 基礎百搭素T", "price_base": 390, "rating": 4.2, "img": "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=500"},
        {"type": "T-shirt", "title": "荷葉邊可愛短袖上衣", "price_base": 620, "rating": 4.4, "img": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500"},
        {"type": "T-shirt", "title": "蕾絲拼接舒適短袖", "price_base": 680, "rating": 4.5, "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500"},
        {"type": "T-shirt", "title": "清新條紋落肩上衣", "price_base": 540, "rating": 4.3, "img": "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=500"},
        
        # Jacket 外套系列
        {"type": "Jacket", "title": "城市極簡機能防風連帽外套", "price_base": 1990, "rating": 4.8, "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500"},
        {"type": "Jacket", "title": "經典街頭率性丹寧牛仔外套", "price_base": 1490, "rating": 4.6, "img": "https://images.unsplash.com/photo-1611312449412-6cefac5dc3e4?w=500"},
        {"type": "Jacket", "title": "英倫風時尚雙排扣翻領大衣", "price_base": 2490, "rating": 4.7, "img": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=500"},
        {"type": "Jacket", "title": "小香風優雅外套", "price_base": 1990, "rating": 4.7, "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500"},
        {"type": "Jacket", "title": "輕盈羽絨保暖外套", "price_base": 1790, "rating": 4.5, "img": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=500"},
        {"type": "Jacket", "title": "皮革機能休閒外套", "price_base": 1850, "rating": 4.4, "img": "https://images.unsplash.com/photo-1611312449412-6cefac5dc3e4?w=500"},
        
        # Jeans 褲裝系列
        {"type": "Jeans", "title": "工裝風多口袋休閒寬褲", "price_base": 990, "rating": 4.6, "img": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500"},
        {"type": "Jeans", "title": "日系純色百搭舒適修身直筒褲", "price_base": 790, "rating": 4.2, "img": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500"},
        {"type": "Jeans", "title": "高腰修身顯瘦復古水洗牛仔褲", "price_base": 1290, "rating": 4.5, "img": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500"},
        {"type": "Jeans", "title": "高腰直筒刷色牛仔褲", "price_base": 1050, "rating": 4.5, "img": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500"},
        {"type": "Jeans", "title": "淺色寬鬆復古牛仔褲", "price_base": 1150, "rating": 4.4, "img": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500"},
        {"type": "Jeans", "title": "彈性修身牛仔九分褲", "price_base": 990, "rating": 4.3, "img": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500"},
        
        # Dress 連身裙系列
        {"type": "Dress", "title": "法式優雅浪漫碎花連身裙", "price_base": 1490, "rating": 4.7, "img": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500"},
        {"type": "Dress", "title": "赫本風極簡純色高腰洋裝", "price_base": 1680, "rating": 4.6, "img": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=500"},
        {"type": "Dress", "title": "浪漫雪紡花瓣洋裝", "price_base": 1790, "rating": 4.6, "img": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500"},
        {"type": "Dress", "title": "優雅蕾絲拼接連身裙", "price_base": 1590, "rating": 4.5, "img": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=500"},
        {"type": "Dress", "title": "波西米亞長袖洋裝", "price_base": 1890, "rating": 4.7, "img": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500"},
        {"type": "Dress", "title": "經典襯衫連身洋裝", "price_base": 1390, "rating": 4.4, "img": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=500"}
    ]
    
    realtime_results = []
    
    # 網路爬蟲數據過濾與格式標準化清洗 - 新增類型篩選
    for item in mock_pool:
        # 【新增】檢查服飾類型是否匹配
        if item["type"] != clothing_type:
            continue
            
        brand_multiplier = {"UNIQLO": 1.0, "GU": 0.8, "ZARA": 1.4, "H&M": 0.9}
        multiplier = brand_multiplier.get(brand, 1.0)
        final_price = int(item["price_base"] * multiplier)
        
        if min_price <= final_price <= max_price:
            brand_code = str(brand)[:2].upper()
            serial_num = random.randint(100, 999)
            item_code = f"CRAWL-{brand_code}-{final_price}-{serial_num}"
            
            realtime_results.append({
                'item_code': item_code,
                'title': f"【即時搜羅】{brand} {gender}{clothing_type} · {item['title']}",
                'price': final_price,
                'rating': item["rating"],
                'brand': brand,
                'image_url': item["img"],
                'is_fallback': False,
                'is_crawler': True
            })
            
    return realtime_results

def load_local_clothing_data(target_brand, target_gender, target_type, min_price, max_price):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, '..', 'data.csv')
    df = pd.read_csv(csv_path)
    df['brand'] = df['brand'].astype(str).str.strip()
    df['gender'] = df['gender'].astype(str).str.strip()
    df['type'] = df['type'].astype(str).str.strip()

    condition = (
        (df['gender'] == target_gender) &
        (df['brand'] == target_brand) &
        (df['type'] == target_type) &
        (df['price'] >= min_price) &
        (df['price'] <= max_price)
    )

    results = []
    for idx, row in df[condition].iterrows():
        brand_code = str(row['brand'])[:2].upper()
        serial_num = random.randint(100, 999)
        item_code = f"LOCAL-{brand_code}-{int(row['price'])}-{serial_num}"

        results.append({
            'item_code': item_code,
            'title': row['title'],
            'price': int(row['price']),
            'rating': float(row['rating']),
            'brand': row['brand'],
            'image_url': row['image_url'],
            'is_fallback': False
        })

    return results

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    
    frontend_gender = data.get('gender')
    target_brand = data.get('brand')
    target_type = data.get('type')
    
    gender_map = {'男裝': 'men', '女裝': 'women'}
    target_gender = gender_map.get(frontend_gender, frontend_gender)

    try:
        min_price = float(data.get('min_price') if data.get('min_price') else 0)
    except:
        min_price = 0.0
        
    try:
        max_price = float(data.get('max_price') if data.get('max_price') else 99999)
    except:
        max_price = 99999.0

    # 1. 優先啟動即時網路爬蟲
    try:
        crawler_data = fetch_realtime_clothing_data(target_brand, frontend_gender, target_type, min_price, max_price)

        if crawler_data:
            try:
                csv_results = load_local_clothing_data(target_brand, target_gender, target_type, min_price, max_price)
                if csv_results:
                    existing_titles = {item['title'] for item in crawler_data}
                    for item in csv_results:
                        if item['title'] not in existing_titles:
                            crawler_data.append(item)
            except Exception as csv_merge_err:
                print(f"本機 CSV 補充失敗: {csv_merge_err}")

            return jsonify({
                'success': True,
                'count': len(crawler_data),
                'data': crawler_data
            })
    except Exception as crawler_err:
        print(f"即時爬蟲模組異常: {crawler_err}")

    # 2. 備援機制：本機 CSV 資料庫 (精準對齊修復區塊)
    # 2. 備援機制：本機 CSV 資料庫 (精準對齊修復區塊)
# 2. 備援機制：本機 CSV 資料庫 (精準對齊修復區塊)
    try:
        # 修正：先找到目前 routes.py 的位置，再往上一層找到最外面的 data.csv
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, '..', 'data.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'message': '找不到備用資料庫'}), 404

        df = pd.read_csv(csv_path)
        df['brand'] = df['brand'].str.strip()
        df['gender'] = df['gender'].str.strip()
        df['type'] = df['type'].str.strip()

        condition = (
            (df['gender'] == target_gender) &
            (df['brand'] == target_brand) &
            (df['type'] == target_type) &
            (df['price'] >= min_price) &
            (df['price'] <= max_price)
        )
        filtered_df = df[condition]
        
        results = []
        for idx, row in filtered_df.iterrows():
            brand_code = str(row['brand'])[:2].upper()
            serial_num = random.randint(100, 999)
            item_code = f"LOCAL-{brand_code}-{int(row['price'])}-{serial_num}"
            
            results.append({
                'item_code': item_code,
                'title': row['title'],
                'price': int(row['price']),
                'rating': float(row['rating']),
                'brand': row['brand'],
                'image_url': row['image_url'],
                'is_fallback': False
            })
            
        # 3. 店長隨機推薦
        if not results:
            brand_fallback = df[df['brand'] == target_brand]
            if not brand_fallback.empty:
                sample_size = min(3, len(brand_fallback))
                fallback_df = brand_fallback.sample(n=sample_size)
                
                for idx, row in fallback_df.iterrows():
                    brand_code = str(row['brand'])[:2].upper()
                    serial_num = random.randint(100, 999)
                    item_code = f"RECOMMEND-{brand_code}-{int(row['price'])}-{serial_num}"
                    
                    results.append({
                        'item_code': item_code,
                        'title': f"【店長推薦】{row['title']}",
                        'price': int(row['price']),
                        'rating': float(row['rating']),
                        'brand': row['brand'],
                        'image_url': row['image_url'],
                        'is_fallback': True
                    })

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
