import requests
import time

#  НАСТРОЙКИ (ТВОИ ДАННЫЕ) 
API_KEY = ""
VOICE_ID = ""  # Голос: Clyde

def generate_voice_elevenlabs(text, filename):
    """
    Генерирует голос через ElevenLabs и сохраняет в filename.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    # НАСТРОЙКИ ХАРАКТЕРА ГОЛОСА (CLYDE)
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {
            # Stability 0.40: Голос будет "шершавым", с легкой дрожью и хрипотцой. 
            # Если поставить выше (0.7), он станет слишком гладким.
            "stability": 0.70,       
            
            # Similarity 0.85: Заставляем его держать басы и характер Клайда.
            "similarity_boost": 0.85, 
            
            # Style 0.5: Добавляем немного драматизма (но не истерики).
            "style": 0.00,            
            
            "use_speaker_boost": True
        }
    }
    try:
        print(f" ElevenLabs: Озвучиваю '{text[:30]}...' (Clyde)")
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f" Аудио сохранено: {filename}")
            return True
        else:
            print(f" ОШИБКА ElevenLabs: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f" Критическая ошибка звука: {e}")
        return False

# Тестовый запуск (если запустить этот файл отдельно)
if __name__ == "__main__":
    generate_voice_elevenlabs("Subject 89 is demonstrating mimicry capabilities.", "test_clyde.mp3")