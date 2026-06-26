@main_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    
    frontend_gender = data.get('gender') # '男裝' 或 '女裝'
    target_brand = data.get('brand')
    target_type = data.get('type')
    keyword = data.get('keyword', '').strip().lower()
    sort_by = data.get('sort_by', '')
    
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

    # 定義系統支援的所有品牌與類型列表，用於跨領域搜尋
    ALL_BRANDS = ["UNIQLO", "GU", "ZARA", "H&M"]
    ALL_TYPES = ['T-shirt', 'Jacket', 'Jeans', 'Dress']

    # 1. 優先啟動即時網路爬蟲
    try:
        # 💡 【核心改動】如果有關鍵字，同時打破「品牌」與「類型」的限制，全盤搜羅！
        if keyword:
            crawler_data = []
            for brand_option in ALL_BRANDS:
                for clothing_type_option in ALL_TYPES:
                    temp_data = fetch_realtime_clothing_data(brand_option, frontend_gender, clothing_type_option, min_price, max_price)
                    crawler_data.extend(temp_data)
        else:
            # 沒有關鍵字，維持原本精準的品牌與類型篩選
            crawler_data = fetch_realtime_clothing_data(target_brand, frontend_gender, target_type, min_price, max_price)

        if crawler_data:
            try:
                # 補充本地 CSV 資料，同樣在有關鍵字時跨品牌與類型
                if keyword:
                    csv_results = []
                    for brand_option in ALL_BRANDS:
                        for clothing_type_option in ALL_TYPES:
                            temp_csv = load_local_clothing_data(brand_option, frontend_gender, clothing_type_option, min_price, max_price)
                            if not temp_csv:
                                temp_csv = load_local_clothing_data(brand_option, target_gender, clothing_type_option, min_price, max_price)
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

            # 統一套用關鍵字過濾（因為上面撈出了所有品牌的資料，這裡會幫你留下符合關鍵字的）
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

        # 性別與價格是基本過濾條件
        gender_condition = (df['gender'] == frontend_gender) | (df['gender'] == target_gender)
        base_condition = (
            gender_condition &
            (df['price'] >= min_price) &
            (df['price'] <= max_price)
        )
        
        # 💡 【核心改動】在備援機制中，如果有關鍵字，連 df['brand'] == target_brand 的條件也拔掉！
        if keyword:
            condition = base_condition  # 不限制品牌，也不限制類型
        else:
            condition = base_condition & (df['brand'] == target_brand) & (df['type'] == target_type)
        
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
            
        # 先進行跨品牌的關鍵字過濾與排序
        results = apply_search_and_sort(results, keyword, sort_by)

        # 3. 店長隨機推薦（當什麼都沒搜到時）
        if not results:
            # 既然是跨品牌搜空了，推薦就從全資料庫裡抽
            sample_size = min(3, len(df))
            if sample_size > 0:
                fallback_df = df.sample(n=sample_size)
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
                results = apply_search_and_sort(results, keyword, sort_by)

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500