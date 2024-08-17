from flask import Flask, request, jsonify, send_file
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from PIL import Image
import io
import traceback
import logging

app = Flask(__name__)

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

# 加載預訓練的 MobileNetV2 模型
model = MobileNetV2(weights='imagenet')

# 擴展貓科動物列表
cat_breeds = [
    'tabby', 'tiger_cat', 'persian_cat', 'siamese_cat', 'egyptian_cat'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def predict_image(image_data):
    try:
        # 打開圖像並轉換為RGB模式
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        img = img.resize((224, 224))
        
        # 轉換為numpy數組
        x = np.array(img)
        
        # 添加批次維度
        x = np.expand_dims(x, axis=0)
        
        # 預處理輸入
        x = preprocess_input(x)
        
        with tf.device('/CPU:0'):  # 強制使用 CPU，避免 GPU 相關錯誤
            preds = model.predict(x)
        
        return decode_predictions(preds, top=5)[0]
    except Exception as e:
        logging.error(f"Error in predict_image: {str(e)}")
        logging.error(traceback.format_exc())
        return None 

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            try:
                image_data = file.read()
                predictions = predict_image(image_data)
                
                if predictions is None:
                    return jsonify({'error': 'Error processing image'}), 500

                is_cat = any(breed in pred[1].lower() for pred in predictions for breed in cat_breeds)
                results = {
                    'is_cat': is_cat,
                    'predictions': [{'class': pred[1], 'probability': float(pred[2])} for pred in predictions]
                }
                return jsonify(results)
            except Exception as e:
                logging.error(f"Error processing file: {str(e)}")
                logging.error(traceback.format_exc())
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        logging.error(f"Unexpected error in upload_file: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/')
def index():
    return send_file('templates/index.html')

@app.route('/imagenet_classes.txt')
def imagenet_classes():
    return send_file('imagenet_classes.txt')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
