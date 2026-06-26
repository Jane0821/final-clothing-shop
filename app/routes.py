@main_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    
    frontend_gender = data.get('gender') # '男裝' 或 '女裝'
    target_brand = data.get('brand')
    target_type = data.get('type')
    keyword = data.get('keyword', '').strip().lower()
    sort_by = data.get('sort_by', '')
    
    # 💡 請確認你的 data.csv 裡面 gender 欄位到底是寫 "男裝" 還是 "men"
    # 如果 CSV 寫的是 "男裝"，這裡 target_gender 就要維持 frontend_gender！
    # 安全起見，我們這裡直接保留原本的對應，但下方查詢時做好相容
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
        # 如果有關鍵字，不論前端選什麼 type，直接全面跨服飾類型搜羅
        if keyword:
            crawler_data = []
            for clothing_type_option in ['T-shirt', 'Jacket', 'Jeans', 'Dress']:
                temp_data = fetch_realtime_clothing_data(target_brand, frontend_gender, clothing_type_option, min_price, max_price)
                crawler_data.extend(temp_data)
        else:
            # 沒有關鍵字，按原邏輯篩選特定類型
            crawler_data = fetch_realtime_clothing_data(target_brand, frontend_gender, target_type, min_price, max_price)

        if crawler_data:
            try:
                # 補充本地 CSV 資料，一樣判斷是否跨類型
                if keyword:
                    csv_results = []
                    for clothing_type_option in ['T-shirt', 'Jacket', 'Jeans', 'Dress']:
                        # 💡 注意：這裡改傳 frontend_gender，確保與 fetch_realtime 邏輯一致，且相容 CSV 的中文字
                        temp_csv = load_local_clothing_data(target_brand, frontend_gender, clothing_type_option, min_price, max_price)
                        # 如果上面沒撈到，試試看英文版的 target_gender
                        if not temp_csv:
                            temp_csv = load_local_clothing_data(target_brand, target_gender, clothing_type_option, min_price, max_price)
                        csv_results.extend(temp_csv)
                else:
                    csv_results = load_local_clothing_data(target_brand, frontend_gender, target_type, min_price, max_price)
                    if not csv_results:
                        csv_results = load_local_clothing_data(target_brand, target_gender, target_type, min_price, max_price)
                
                if csv_results:
                    existing_titles = {item['title'] for item in crawler_data}
                    for item in csv_results:
                        if item['title'] not in existing_titles:
                            crawler_data.append(item)
            except Exception as csv_merge_err:
                print(f"本機 CSV 補充失敗: {csv_merge_err}")

            # 💡 統一在這裡套用搜尋關鍵字過濾與排序
            crawler_data = apply_search_and_sort(crawler_data, keyword, sort_by)
            
            return jsonify({
                'success': True,
                'count': len(crawler_data),
                'data': crawler_data
            })
    except Exception as crawler_err:
        print(f"即時爬蟲模組異常: {crawler_err}")

    # 2. 備援機制：本機 CSV 資料庫
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, '..', 'data.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'message': '找不到備用資料庫'}), 404

        df = pd.read_csv(csv_path)
        df['brand'] = df['brand'].astype(str).str.strip()
        df['gender'] = df['gender'].astype(str).str.strip()
        df['type'] = df['type'].astype(str).str.strip()

        # 💡 修正性別篩選條件：同時支援 '男裝' 或 'men'，避免因為對應錯了導致篩出空集合
        gender_condition = (df['gender'] == frontend_gender) | (df['gender'] == target_gender)

        base_condition = (
            gender_condition &
            (df['brand'] == target_brand) &
            (df['price'] >= min_price) &
            (df['price'] <= max_price)
        )
        
        # 💡 關鍵字觸發時，不設限 type 欄位
        if keyword:
            condition = base_condition
        else:
            condition = base_condition & (df['type'] == target_type)
        
        filtered_df = df[condition]
        
        results = []
        for idx, row in filtered_df.iterrows():
            brand_code = str(row['brand'])[:2].upper()
            serial_num = random.randint(100, 999)
            item_code = f"LOCAL-{brand_code}-{int(row['price'])}-{serial_num}"
            
            official_url = BRAND_WEBSITES.get(row['brand'])
            image_url = STABLE_IMAGE_BY_TYPE.get(row['type'], PLACEHOLDER_IMAGE)

            results.append({
                'item_code': item_code,
                'title': row['title'],
                'price': int(row['price']),
                'rating': float(row['rating']),
                'brand': row['brand'],
                'image_url': image_url,
                'official_url': official_url,
                'is_fallback': False
            })
            
        # 💡 在排除空結果與店長推薦之前，先對結果進行關鍵字過濾
        results = apply_search_and_sort(results, keyword, sort_by)

        # 3. 如果過濾後真的沒商品，才進店長隨機推薦
        if not results:
            brand_fallback = df[df['brand'] == target_brand]
            if not brand_fallback.empty:
                sample_size = min(3, len(brand_fallback))
                fallback_df = brand_fallback.sample(n=sample_size)
                
                for idx, row in fallback_df.iterrows():
                    brand_code = str(row['brand'])[:2].upper()
                    serial_num = random.randint(100, 999)
                    item_code = f"RECOMMEND-{brand_code}-{int(row['price'])}-{serial_num}"
                    
                    official_url = BRAND_WEBSITES.get(row['brand'])
                    image_url = STABLE_IMAGE_BY_TYPE.get(row['type'], PLACEHOLDER_IMAGE)

                    results.append({
                        'item_code': item_code,
                        'title': f"【店長推薦】{row['title']}",
                        'price': int(row['price']),
                        'rating': float(row['rating']),
                        'brand': row['brand'],
                        'image_url': image_url,
                        'official_url': official_url,
                        'is_fallback': True
                    })
                # 店長推薦完後再次排序（以防萬一）
                results = apply_search_and_sort(results, keyword, sort_by)

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
