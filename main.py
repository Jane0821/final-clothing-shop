from flask import Flask
import os

app = Flask(__name__)

# 註冊藍圖 (Blueprint) 或直接導入路由
from app.routes import main_bp
app.register_blueprint(main_bp)

if __name__ == '__main__':
    # 讓程式自動讀取 Render 分配的 Port，如果讀不到（例如在本機環境）就預設用 5002
    port = int(os.environ.get("PORT", 5002))
    # 雲端部署必須將 host 設定為 '0.0.0.0'
    app.run(host='0.0.0.0', port=port, debug=False)