Mở cmd chạy pip install -r requirement.txt

tạo file .env:
DB_HOST=localhost
DB_PORT=5431
DB_NAME=face_recognition
DB_USER=
DB_PASSWORD=

# Giữ nguyên phần này

DATASET_FOLDER=dataset
EMBEDDING_FILE=embeddings.pkl
MODEL_NAME=ArcFace
DETECTOR_BACKEND=retinaface
MIN_IMAGES=5
CONFIDENCE_THRESHOLD=0.55
QUALITY_THRESHOLD=0.7

Tạo db xong điền thông tin vào .env

xong chạy python init_database.py

chạy xong thì chạy python gui_app.py là xong

Nên lấy điện thoại là web cam để hiệu quả hơn
