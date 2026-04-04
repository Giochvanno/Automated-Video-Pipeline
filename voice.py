import requests

# ТВОИ ДАННЫЕ (Clyde - Deep & Raspy)
# Ты на тарифе Starter, поэтому это работает без ограничений.
API_KEY = ""
VOICE_ID = "" 

def create_voice(text, filename):
    """
    Генерирует голос через ElevenLabs (Clyde).
    Эта функция заменяет старого Кристофера.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    # Настройки для хоррора (Холодный, глубокий голос)
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.50,       # 50% стабильности (живой голос)
            "similarity_boost": 0.85, # Держим бас Клайда
            "style": 0.0,            # Без лишней театральности
            "use_speaker_boost": True
        }
    }

    try:
        # print(f" ElevenLabs: Озвучиваю...") # Раскомментируй, если нужен лог
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f" ОШИБКА ЗВУКА: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f" Критическая ошибка voice.py: {e}")
        return False

# Тест (если запустишь файл отдельно)
if __name__ == "__main__":
    create_voice("Subject 678. Anomaly confirmed.", "test_clyde.mp3")
    print("Проверь файл test_clyde.mp3")