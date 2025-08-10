from flask import Flask, request, render_template, send_from_directory
import os
from processor import ImageProcessor
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import uuid

# 基礎
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
RESULT_FOLDER = os.path.join(BASE_DIR, "static", "results")
HIST_FOLDER = os.path.join(BASE_DIR, "static", "histogram")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(HIST_FOLDER, exist_ok=True)

# 数値をタプルに変換
def parse_k_size(k_size_str: str) -> tuple[int, int]:
    try:
        s = (k_size_str or '').strip()
        if ',' in s:
            a, b = s.split(',', 1)
            kx, ky = int(a), int(b)
        else:
            kx = ky = int(s)
    except Exception:
        kx = ky = 3

    # ガード：3未満→3、偶数→+1
    kx = max(3, kx); ky = max(3, ky)
    if kx % 2 == 0: kx += 1
    if ky % 2 == 0: ky += 1
    return (kx, ky)

#アプリ起動と同時にhtmlを呼び出し
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html",k_size_str="3", sigma_x_str="0")

# 画像1枚の処理前半
@app.route("/upload_single", methods=["POST"])
def upload_single():
    file = request.files.get("image")
    if not file:
        return "画像が選択されていません", 400
    
    # 安全なファイル名を生成（日本語・記号対策済み）
    base = os.path.splitext(secure_filename(file.filename))[0]
    if not base.isascii() or base == "":
        base = uuid.uuid4().hex
    filename = f"{base}.jpg"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # パラメータ取得
    k_val = int(request.form.get('k_size'))
    k_size = parse_k_size(str(k_val))
    sigma_x = float(request.form.get("sigma_x",0))
    if sigma_x < 0: sigma_x = 0.0

    # 処理
    processor = ImageProcessor(input_path, k_size=k_size, sigma_x=sigma_x)
    s_channel = processor._convert_to_s_channel()
    hist_name = f"hist_{base}.png"
    hist_path = os.path.join(HIST_FOLDER, hist_name)
    processor._show_histogram(s_channel, hist_path)
    hist_url = f"histogram/{hist_name}"

    return render_template("index.html",
                            hist_image=hist_url,
                            timestamp=datetime.now().timestamp(),
                            image_filename=filename,
                            k_size_str=str(k_size[0]),
                            sigma_x_str=str(sigma_x)
    )


# 画像1枚の処理後半
@app.route("/binarize_single", methods=["POST"])
def binarize_single():
    filename = request.form.get("filename")
    if not filename:
        return "ファイル名がありません", 400
    input_path = os.path.join(UPLOAD_FOLDER, filename)

    k_size = parse_k_size(request.form.get("k_size", "3"))
    sigma_x = float(request.form.get("sigma_x", "0"))
    if sigma_x < 0: sigma_x = 0.0

    method = request.form.get("method", "")
    lower = int(request.form.get("lower", 100)) if method == "inRange" else None
    upper = int(request.form.get("upper", 200)) if method == "inRange" else None

    processor = ImageProcessor(input_path, k_size=k_size, sigma_x=sigma_x)
    processor.remove_background_by_contour(method=method, lower=lower, upper=upper)
    
    save_path = os.path.join(RESULT_FOLDER, filename)
    processor.save(save_path)
    result_url = "results/" + filename

    return render_template(
        "index.html",
        result_files=[result_url],
        k_size_str=str(k_size[0]),
        sigma_x_str=str(sigma_x),
        image_filename=filename
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
