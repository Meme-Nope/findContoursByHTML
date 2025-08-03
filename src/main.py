from flask import Flask, request, render_template, send_from_directory
import os
from processor import ImageProcessor
from werkzeug.utils import secure_filename
import time

# 基礎
app = Flask(__name__)
UPLOAD_FOLDER = "app/static/uploads"
RESULT_FOLDER = "app/static/results"
HIST_FOLDER = "app/static/histogram"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(HIST_FOLDER, exist_ok=True)

# 数値をタプルに変換
def parse_k_size(k_size_str: str) -> tuple[int, int]:
    try:
        parts = k_size_str.split(",")
        return (int(parts[0]), int(parts[1]))
    except Exception:
        return (3, 3)

#アプリ起動と同時にhtmlを呼び出し
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# 画像1枚の処理前半
@app.route("/upload_single", methods=["POST"])
def upload_single():
    file = request.files.get("image")
    if not file:
        return "画像が選択されていません", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # パラメータ取得
    k_size = parse_k_size(request.form.get("k_size", "3,3"))
    sigma_x = float(request.form.get("sigma_x", "-1"))
    show_hist = "show_hist" in request.form

    # 処理
    processor = ImageProcessor(input_path, k_size=k_size, sigma_x=sigma_x)
    l_channel = processor._convert_to_l_channel()
    hist_path = os.path.join(HIST_FOLDER, "histogram.png")
    processor._show_histogram(l_channel, hist_path)
    hist_url = "histogram/histogram.png"
   

    return render_template("index.html",
                           hist_image=hist_url,
                           image_filename=filename,
                           k_size_str=request.form.get("k_size", "3,3"),
                           sigma_x_str=request.form.get("sigma_x", "-1"))

# 画像1枚の処理後半
@app.route("/binarize_single", methods=["POST"])
def binarize_single():
    filename = request.form.get("filename")
    input_path = os.path.join(UPLOAD_FOLDER, filename)

    k_size = parse_k_size(request.form.get("k_size", "3,3"))
    sigma_x = float(request.form.get("sigma_x", "-1"))
    method = request.form.get("method", "inRange")

    lower = int(request.form.get("lower", 100)) if method == "inRange" else None
    upper = int(request.form.get("upper", 200)) if method == "inRange" else None

    processor = ImageProcessor(input_path, k_size=k_size, sigma_x=sigma_x)
    processor.remove_background_by_contour(method=method, lower=lower, upper=upper)
    
    save_path = os.path.join(RESULT_FOLDER, filename)
    processor.save(save_path)
    result_url = "results/" + filename

    return render_template("index.html", result_files=[result_url])


#残り時間の送信が課題
# @app.route("/upload_folder", methods=["POST"])
# def upload_folder():
#     files = request.files.getlist("files")
#     if not files:
#         return "フォルダが空です", 400
    
#     # パラメータ取得
#     k_size = parse_k_size(request.form.get("k_size", "3,3"))
#     sigma_x = float(request.form.get("sigma_x", "-1"))
#     show_hist = "show_hist" in request.form

#     #処理対象となるファイルを抽出し、カウント
#     saved_files = []
#     for file in files:
#         filename = secure_filename(file.filename)
#         save_path = os.path.join(UPLOAD_FOLDER, filename)
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)  # サブフォルダも再現
#         file.save(save_path)
#         saved_files.append(filename)
#     valid_exts = (".jpg", ".jpeg", ".png", ".bmp")
#     file_list = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(valid_exts)]
#     target_counts = len(file_list)


#     start = time.time()
#     result_files = []
#     for idx, file in enumerate(file_list, start=1):
#         in_path = os.path.join(UPLOAD_FOLDER, file)

#         try:
#             processor = ImageProcessor(in_path, k_size=k_size, sigma_x=sigma_x, show_hist=show_hist)
#             processor.remove_background_by_contour()
#             save_path = os.path.join(RESULT_FOLDER, file)
#             processor.save(save_path)
#             result_files.append("results/" + file)
#         except Exception as e:
#             print(f"処理失敗: {filename} - {e}")

#     return render_template("index.html", result_files=result_files)

if __name__ == "__main__":
    app.run(debug=True)
