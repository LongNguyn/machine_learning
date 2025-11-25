import os
import cv2
import numpy as np
import pickle
import time
from deepface import DeepFace
from numpy.linalg import norm

# ========================
# Build or update embeddings
# ========================
def build_or_update_embeddings(dataset_folder, embed_file, model_name="ArcFace", detector_backend="retinaface"):
    embeddings = []

    if os.path.exists(embed_file):
        with open(embed_file, "rb") as f:
            embeddings = pickle.load(f)

    existing_identities = set(e["identity"] for e in embeddings)
    print(f"[INFO] Đã có {len(existing_identities)} nhãn trong embeddings")

    for root, dirs, files in os.walk(dataset_folder):
        label = os.path.basename(root)
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                if label in existing_identities:
                    continue
                img_path = os.path.join(root, file)
                try:
                    embedding = DeepFace.represent(
                        img_path=img_path,
                        model_name=model_name,
                        detector_backend=detector_backend,
                        enforce_detection=True
                    )[0]["embedding"]

                    embeddings.append({
                        "identity": label,
                        "embedding": np.array(embedding, dtype=np.float32)
                    })

                    print(f"[INFO] Thêm embedding cho {label} ({file})")

                except Exception as e:
                    print(f"[CẢNH BÁO] Không trích xuất được embedding cho {img_path}: {e}")

    with open(embed_file, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"[INFO] Sau chuẩn hoá: {len(embeddings)} embedding(s).")
    return embeddings


# ========================
# Cosine similarity
# ========================
def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (norm(a) * norm(b))


def find_best_match(face_emb, embeddings, threshold=0.55):
    min_dist = float("inf")
    identity = "Unknown"

    for e in embeddings:
        dist = cosine_distance(face_emb, e["embedding"])
        if dist < min_dist:
            min_dist = dist
            identity = e["identity"]

    confidence = max(0, 1 - min_dist)

    if min_dist > threshold:
        identity = "Unknown"

    return identity, confidence


# ========================
# Vẽ lên frame
# ========================
def draw_face(frame, box, name, confidence):
    x, y, w, h = box
    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    cv2.putText(frame, f"{name} ({confidence*100:.1f}%)", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


# ========================
# Main
# ========================
if __name__ == "__main__":
    DATASET_FOLDER = "dataset"
    EMBED_FILE = "embeddings.pkl"
    MODEL_NAME = "ArcFace"
    DETECTOR = "retinaface"

    embeddings = build_or_update_embeddings(DATASET_FOLDER, EMBED_FILE, MODEL_NAME, DETECTOR)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không mở được webcam!")
        exit()

    print("[INFO] Nhấn phím 'q' để thoát")

    frame_count = 0
    last_results = []  # lưu kết quả ở frame trước

    # Biến tính FPS
    fps = 0
    fps_count = 0
    fps_start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        fps_count += 1

        try:
            if frame_count % 10 == 0:
                last_results = []
                results = DeepFace.extract_faces(frame, detector_backend=DETECTOR, enforce_detection=False)

                for r in results:
                    fa = r["facial_area"]
                    x, y, w, h = fa["x"], fa["y"], fa["w"], fa["h"]

                    emb = DeepFace.represent(
                        frame[y:y+h, x:x+w],
                        model_name=MODEL_NAME,
                        detector_backend="skip",
                        enforce_detection=False
                    )[0]["embedding"]

                    identity, confidence = find_best_match(np.array(emb, dtype=np.float32), embeddings)

                    last_results.append((x, y, w, h, identity, confidence))

            # Vẽ lại kết quả gần nhất
            for (x, y, w, h, identity, confidence) in last_results:
                draw_face(frame, (x, y, w, h), identity, confidence)

        except Exception as e:
            print(f"[LỖI] {e}")

        # ========================
        # Tính FPS trung bình mỗi 30 frame
        # ========================
        if fps_count >= 30:
            end_time = time.time()
            fps = fps_count / (end_time - fps_start_time)
            fps_start_time = end_time
            fps_count = 0

        cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
