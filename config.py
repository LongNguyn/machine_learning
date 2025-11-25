import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# PostgreSQL Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'face_recognition'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'admin123')
}

# Application Configuration
APP_CONFIG = {
    'dataset_folder': os.getenv('DATASET_FOLDER', 'dataset'),
    'embedding_file': os.getenv('EMBEDDING_FILE', 'embeddings.pkl'),
    'model_name': os.getenv('MODEL_NAME', 'ArcFace'),
    'detector_backend': os.getenv('DETECTOR_BACKEND', 'retinaface'),
    'min_images_per_person': int(os.getenv('MIN_IMAGES', '5')),
    'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.55')),
    'image_quality_threshold': float(os.getenv('QUALITY_THRESHOLD', '0.7'))
}

# Tạo thư mục dataset nếu chưa tồn tại
os.makedirs(APP_CONFIG['dataset_folder'], exist_ok=True)