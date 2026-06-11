import whisper
from moviepy.editor import TextClip
from moviepy.config import change_settings
import os
import gc

# Путь к ImageMagick
MAGICK_PATH = r""
change_settings({"IMAGEMAGICK_BINARY": MAGICK_PATH})

print(" Загрузка модели Whisper...")
model = whisper.load_model("base") 

def create_karaoke_clips(audio_path, font_path):
    print(f" Whisper начинает слушать: {audio_path}...")
    
    # ОТЛАДКА ШРИФТА 
    # Мы выводим в консоль то, что пришло из Factory.
    print(f"\n [SUBTITLES.PY] Получен шрифт: '{font_path}'")
    
    if not os.path.exists(audio_path):
        print(f" ОШИБКА: Аудиофайл не найден: {audio_path}")
        return []

    try:
        result = model.transcribe(audio_path, word_timestamps=True, fp16=False)
    except Exception as e:
        print(f" Ошибка внутри Whisper: {e}")
        return []
    
    clips = []
    print(" Распознавание завершено. Группировка фраз...")

    all_words = []
    for segment in result["segments"]:
        for word_info in segment["words"]:
            all_words.append(word_info)

    MAX_WORDS_IN_GROUP = 3   
    MAX_CHARS_IN_GROUP = 25  
    
    current_group = []      
    group_start_time = 0.0  
    
    clip_counter = 0

    for i, word_info in enumerate(all_words):
        word = word_info["word"].strip()
        start = float(word_info["start"])
        end = float(word_info["end"])

        if not current_group:
            group_start_time = start

        current_group.append(word)
        
        is_limit_reached = len(current_group) >= MAX_WORDS_IN_GROUP
        is_too_long = sum(len(w) for w in current_group) > MAX_CHARS_IN_GROUP
        is_last_word = (i == len(all_words) - 1)

        if is_limit_reached or is_too_long or is_last_word:
            full_text = " ".join(current_group)
            
            duration = end - group_start_time
            if duration < 0.5: duration = 0.5 

            # print(f" Рендер: '{full_text}'") # Можно раскомментить если нужно

            try:
                #  СОЗДАНИЕ КЛИПА 
                # Мы просто используем font_path как есть. 
                # Factory.py уже позаботился о собачках (@) и слэшах.
                
                txt = TextClip(
                    full_text, 
                    fontsize=80,          
                    color="white", 
                    font=font_path,       # <--- ИСПОЛЬЗУЕМ НАПРЯМУЮ     # Чтобы текст читался на любом фоне
                    method='caption',     
                    align='center',
                    size=(1000, None)
                ) 
                
                txt = txt.set_position(('center', 'center')).set_start(group_start_time).set_duration(duration)
                clips.append(txt)
                
                clip_counter += 1
                if clip_counter % 10 == 0: 
                    gc.collect()

            except Exception as e:
                print(f" Сбой на фразе '{full_text}': {e}")
            
            current_group = []

    print(f" Успешно создано {len(clips)} групповых субтитров")
    return clips
