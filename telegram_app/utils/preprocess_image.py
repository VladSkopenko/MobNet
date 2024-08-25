import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from dotenv import load_dotenv
from tensorflow.keras.preprocessing.image import img_to_array
from telegram_app.utils.get_models import get_vgg16_model, get_mobnet_model, get_lenet_model, get_alexnet_model
from telegram_app.utils.py_logger import get_logger



load_dotenv()
logger = get_logger(__name__)

def preprocess_image(img):
    """Перевірка на RGB та створення масиву зображення."""
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((32, 32))
    img_array = img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def get_model(model_type):
    """Отримання моделі на основі вибраного типу."""
    if model_type == "vgg16":
        return get_vgg16_model()
    elif model_type == "mobnet":
        return get_mobnet_model()
    elif model_type == "lenet":
        return get_lenet_model()
    elif model_type == "alexnet":
        return get_alexnet_model()
    else:
        logger.error("Invalid model type selected")
        return get_vgg16_model()

def validate_confidence_threshold(threshold):
    """Перевірка значення порогу довіри."""
    try:
        threshold = float(threshold)
        if threshold < 0 or threshold > 1:
            raise ValueError("Confidence threshold must be between 0 and 1.")
        return threshold
    except ValueError as e:
        logger.error(f"Invalid confidence threshold value: {e}")
        threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.70))
        return threshold

def apply_filters(img, model, confidence_threshold):
    """Застосування фільтрів та перевірка впевненості."""
    filters = [
        ("Контраст", ImageEnhance.Contrast(img).enhance(4)),
        ("Різкість", ImageEnhance.Sharpness(img).enhance(4)),
        ("Колір", ImageEnhance.Color(img).enhance(4)),
        ("Деталізація", img.filter(ImageFilter.DETAIL)),
        ("Додаткова різкість", img.filter(ImageFilter.SHARPEN)),
        ("Згладжування", img.filter(ImageFilter.SMOOTH)),
        ("Розмиття", img.filter(ImageFilter.GaussianBlur(1))),
        ("Накладання фонового кольору", img.convert('L').point(lambda x: x // 16 * 16))
    ]

    for filter_name, filtered_img in filters:
        img_array = preprocess_image(filtered_img)
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)
        confidence = prediction[0][predicted_class]

        if confidence >= confidence_threshold:
            return f"Точність прогнозу була нижче заданого порогу, тому застосували фільтр '{filter_name}'. Результат : {os.getenv('MODEL_CLASSES', '').split(',')[predicted_class]} із вірогідністю {confidence * 100:.2f}%"

    return f"Поточне зображення не підходить для класифікації. Впевненість моделі становить: {confidence * 100:.2f}%. Завантажте, будь ласка, інше зображення."

def make_prediction(model, img_array, confidence_threshold):
    """Прогнозування на основі моделі та повернення результату."""
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    confidence = prediction[0][predicted_class]

    class_labels = os.getenv("MODEL_CLASSES", "").split(",")

    if confidence >= confidence_threshold:
        result_text = f"Результат : {os.getenv('MODEL_CLASSES', '').split(',')[predicted_class]} із вірогідністю у {confidence * 100:.2f}%"
    else:
        img = Image.fromarray((img_array[0] * 255).astype('uint8'))
        result_text = apply_filters(img, model, confidence_threshold)

    return result_text, confidence












