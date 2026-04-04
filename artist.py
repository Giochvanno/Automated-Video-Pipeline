import os
import time
import requests
import random

# Replicate TOKEN
REPLICATE_API_TOKEN = "" 
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

try:
    import replicate
except ImportError:
    print(" Не установлен модуль replicate! Напиши: pip install replicate")
    exit()

def generate_horror_image(prompt, output_path, max_retries=3):
    print(f" Artist (FLUX.1 Schnell): Рисую '{prompt[:30]}...'")

    # НАСТРОЙКИ СТИЛЯ (ВШИТЫЕ)
    # Мы добавляем это к КАЖДОМУ промпту, чтобы видео выглядело цельно.
    style_suffix = (
        ". STYLE: 1990s analog horror footage, VHS glitch texture, magnetic tape noise, "
        "low resolution, grainy trail cam photo, harsh flash photography. "
        "ATMOSPHERE: Pitch black darkness, eerie, uncanny valley, terrifying realism."
    )

    full_prompt = prompt + style_suffix

    for attempt in range(max_retries):
        try:
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": full_prompt,
                    "aspect_ratio": "9:16",   # Вертикальный формат
                    "go_fast": True,          # Оптимизация скорости
                    "megapixels": "1",        # Хватает для видео
                    "num_inference_steps": 4, # Очень быстро
                    "output_format": "jpg",
                    "disable_safety_checker": True # РАЗРЕШАЕМ МОНСТРОВ
                }
            )
            
            if output:
                image_url = str(output[0])
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    with open(output_path, 'wb') as file:
                        file.write(response.content)
                    print(f" Готово: {output_path}")
                    time.sleep(2) 
                    return True
                else:
                    print(" Ошибка скачивания.")
            
        except Exception as e:
            print(f" Ошибка Replicate: {e}")
            time.sleep(3)
            
    return False

if __name__ == "__main__":
    # Тест
    generate_horror_image("A bipedal creature standing in a swamp", "test_artist_final.jpg")