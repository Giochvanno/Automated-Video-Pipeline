import g4f
import time
import random


# БАЗОВАЯ УТИЛИТА СВЯЗИ

def ask_gpt(prompt):
    models_chain = [g4f.models.gpt_4, g4f.models.default]
    for model in models_chain:
        try:
            response = g4f.ChatCompletion.create(
                model=model, messages=[{"role": "user", "content": prompt}], timeout=25 
            )
            if response and len(str(response)) > 10 and "Error" not in str(response)[:20]:
                return str(response)
        except:
            time.sleep(1)
            continue
    return None



# АВТО-ЛОР (САМООБУЧАЮЩИЙСЯ СЦЕНАРИСТ)

def get_ai_quotes(topic, mode="lore", count=4):
    print(f" Brain: Изучаю лор и пишу сценарий ({count} фактов) про '{topic}'...")

    # ИИ сам вспоминает, что это за тварь, и пишет факты/правила.
    # Если он не знает, он придумает логичные правила для этого названия.
    if mode == "alarm":
        prompt = (
            f"You are the Emergency Alert System. Write exactly {count} terrifying survival rules for the horror entity known as '{topic}'. "
            "If it's from a known creepypasta, game, or analog horror, use its actual lore. "
            "Style: Mandatory Protocol / Analog Horror Instruction. "
            "Format: Numbered list. "
            "CONSTRAINT: Maximum 6-8 words per rule. Do NOT use the phrase 'Emergency Broadcast'."
        )
    else:
        prompt = (
            f"You are a horror lore expert. Write exactly {count} creepy facts about the entity '{topic}'. "
            "If it's from a known fiction (like Vita Carnis, SCP, etc.), use canonical lore. "
            "Style: Found footage documentary. "
            "Format: Numbered list. "
            "CONSTRAINT: Maximum 8-10 words per fact."
        )

    response = ask_gpt(prompt)
    print("   Сценарий готов!")
    
    clean_quotes = []
    if response:
        for line in response.split('\n'):
            # Добавил # и убираем звездочки
            cleaned = line.lstrip("0123456789.-) *#").strip().replace("**", "").replace("*", "")
            if "emergency broadcast" in cleaned.lower(): continue
            # Убираем строки, если это заголовки вроде "Fact 1:"
            if "fact" in cleaned.lower() and ":" in cleaned:
                cleaned = cleaned.split(":")[-1].strip()
            if len(cleaned) > 5: clean_quotes.append(cleaned)
    
    if len(clean_quotes) < count:
        return ["Do not look at it.", "Lock all entrances.", "It mimics familiar voices.", "You are not alone."][:count]
        
    return clean_quotes[:count]



#  АВТО-РЕСЕРЧЕР ВИЗУАЛА (ВМЕСТО СЛОВАРЕЙ)

def get_dynamic_visual_lore(topic):
    """Заставляет ИИ вспомнить внешность монстра перед тем, как рисовать."""
    print(f"  Ищу внешность '{topic}' в базе данных...")
    prompt = (
        f"Identify the horror entity known as '{topic}'. "
        "Describe its exact physical appearance (body, face, skin texture) for a concept artist. "
        "If it is a known internet urban legend, analog horror, or creepypasta character, use its CANON appearance. "
        "OUTPUT REQUIREMENT: ONLY provide a 2-3 sentence physical description. Do not include introductory text."
    )
    lore = ask_gpt(prompt)
    if lore:
        print(f"    Внешность найдена: {lore[:50]}...")
        return lore
    else:
        return f"A terrifying, distorted, hyper-realistic horror entity known as {topic}."



#  РЕЖИССЁР (СБОРКА ТЗ ДЛЯ FLUX)

def get_director_instruction(script_line, topic):
    # 1. Получаем внешность монстра динамически!
    monster_visual = get_dynamic_visual_lore(topic)

    # 2. Формируем ТЗ для художника
    prompt = (
        f"You are a Visual Director for a horror film using the FLUX AI engine.\n"
        f"TOPIC: {topic}\n"
        f"SCENE: \"{script_line}\"\n\n"
        
        "GOAL: Create a photo-realistic, terrifying TEXT prompt.\n"
        " CRITICAL RULE: DO NOT generate an actual image. DO NOT return markdown links or URLs. RETURN ONLY RAW TEXT. \n\n"

        " INSTRUCTIONS FOR FLUX:\n"
        f"1. **MANDATORY ENTITY DESCRIPTION:**\n"
        f"   - Use this exact appearance: {monster_visual}\n"
        "   - Do NOT make it a normal human or animal. Keep it monstrous.\n\n"

        "2. **LIGHTING & ATMOSPHERE:**\n"
        "   - Use 'Harsh camera flash' or 'grainy VHS texture'.\n"
        "   - Lighting should be realistic/bad (flashlight beam, security cam).\n\n"

        "3. **COMPOSITION:**\n"
        "   - Low angle shot, security camera view, or terrifying close-up.\n"
        "   - The entity should often be peeking, stalking, or standing in the distance.\n\n"

        "OUTPUT: Provide ONLY the raw prompt string in English. No introductory text, no links, no brackets."
    )
    
    visual_instruction = ask_gpt(prompt)
    
    #  ЗАЩИТА ОТ БАГОВ: Если ИИ всё равно выдал ссылку (http) или пустоту, включаем резерв
    if not visual_instruction or "http" in visual_instruction or len(visual_instruction) < 10:
        fallback = f"{monster_visual}, harsh flashlight, dark setting, vhs style"
        print(f" Director (Fallback used): ...{fallback[:30]}...")
        return fallback
        
    #  ЧИСТКА: Убираем любые остатки маркдауна (скобки, кавычки)
    clean_prompt = visual_instruction.replace('"', '').replace("'", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    if ":" in clean_prompt[:20]: clean_prompt = clean_prompt.split(":")[-1].strip()

    print(f" Director: ...{clean_prompt[:30]}...")
    return clean_prompt


#  ТЕСТОВЫЙ ПОЛИГОН (ЗАПУСК БЕЗ РЕНДЕРА)

if __name__ == "__main__":
    print("\n" + "="*40)
    print(" ЗАПУСК ИЗОЛИРОВАННОГО ТЕСТА BRAIN 2.0 ")
    print("="*40)
    
    # Можешь вписать сюда любого монстра
    test_topic = input("\nВведи имя монстра (например, Siren Head или The Rake): ").strip()
    if not test_topic:
        test_topic = "Siren Head"

    print("\n---  ЭТАП 1: ГЕНЕРАЦИЯ СЦЕНАРИЯ ---")
    quotes = get_ai_quotes(test_topic, mode="lore", count=3)
    for i, q in enumerate(quotes, 1):
        print(f"Факт {i}: {q}")

    print("\n---  ЭТАП 2: ПОИСК ВНЕШНОСТИ (ЛОР) ---")
    visual_desc = get_dynamic_visual_lore(test_topic)
    print(f"Описание для художника: \n{visual_desc}")

    print("\n---  ЭТАП 3: ФОРМИРОВАНИЕ ПРОМПТА FLUX ---")
    test_line = quotes[0] if quotes else "It is watching you."
    director_prompt = get_director_instruction(test_line, test_topic)
    print(f"Итоговый промпт:\n{director_prompt}")
    print("\n" + "="*40 + "\n")
