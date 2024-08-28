import os
import sys
from io import BytesIO
from telegram_app.utils.preprocess_image import get_model


import numpy as np
from aiogram import F
from aiogram import Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from common.messages import NEXT
from common.messages import TAKE_IMAGE
from common.messages import WELCOME
from keyboards import choice_model
from PIL import Image
from states.main_state import MainState
from tensorflow.keras.preprocessing.image import img_to_array


user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=await choice_model())


@user_private_router.callback_query(F.data.startswith("model_"))
async def process_model_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    model_type = callback_query.data
    model_type = model_type.replace("model_", "")
    print(model_type)
    await state.update_data(model_type=model_type)
    await callback_query.answer()
    await callback_query.message.answer(TAKE_IMAGE)
    await state.update_data(model_type=model_type)
    await state.set_state(MainState.image.state)


@user_private_router.message(MainState.image)
async def handle_image(message: types.Message, state: FSMContext):
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        file_data = await message.bot.download_file(file_path)
        img_bytes = file_data.getvalue()
        img = Image.open(BytesIO(img_bytes))
        data = await state.get_data()
        confidence_threshold = data.get("confidence_threshold", 0.63)
        model_t = data.get("model_type")
        model = get_model(model_t)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = img.resize((32, 32))
        img_array = img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)
        confidence = prediction[0][predicted_class]
        class_labels = os.getenv("MODEL_CLASSES", "").split(",")
        if confidence >= confidence_threshold:
            result_text = (
                f"На картинці зображено {class_labels[predicted_class]}"
                f" із вірогідністю у {confidence * 100:.2f}%"
            )
        else:
            result_text = (
                f"Поточне зображення не підходить для класифікації. Впевненість моделі становить:"
                f" {confidence * 100:.2f}%. Завантажте, будь ласка, інше зображення."
            )

        await message.answer(f"{result_text}\n")
        await state.clear()
        await message.answer(text=NEXT, reply_markup=await choice_model())
    else:
        await message.answer(TAKE_IMAGE)
