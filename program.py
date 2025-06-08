import pyttsx3
import speech_recognition as sr
import json
import random
import requests
import re

END = "\x1b[0m"
CLEAR = "[033[H"

RED = "\033[91m"
WHITE = "\033[97m"
BLACK = "\033[90m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

def Weather_Report():
    url_weather = f'https://wttr.in/Saint-Petersburg?format=2'
    data = []

    response = requests.get(url_weather)
    weather_data = response.text

    wind_direction_mapping = {
        "↖": "Северо-запад",  # Tây Bắc
        "↗": "Северо-восток",  # Đông Bắc
        "↑": "Север",           # Bắc
        "↓": "Юг",              # Nam
        "↘": "Юго-восток",       # Đông Nam
        "↙": "Юго-запад",       # Tây Nam
        "←": "Запад",           # Tây
        "→": "Восток",          # Đông
    }
    
    match = re.match(r"([🌦⛅️☀️☁️🌤️⛅️🌥️🌦️🌧️🌨️🌩️🌪️🌫️🌬️🌈❄️🌨️🌩️⛈️]+)\s+🌡️([+-]?\d+°C)\s+🌬️([↖↗↑↓↘↙←→↘↖]+)(\d+km/h)", weather_data)

    if response.status_code == 200:
        if match:
            for i in range(1, 5):
                data.append(match.group(i))

            # Thay thế mũi tên trong hướng gió bằng hướng theo Đông, Tây, Nam, Bắc
            wind_direction = data[2]
            if wind_direction in wind_direction_mapping:
                data[2] = wind_direction_mapping[wind_direction]
        else:
            print("Погодные данные не найдены.")
            return [] 
        
        print(f'{BLUE}Отчёт о погоде в Санкт-Петербурге:{END}')
        print(f' - Описание: {data[0]}')
        print(f' - Температура: {data[1]}')
        print(f' - Направление ветра: {data[2]}')
        print(f' - Скорость ветра: {data[3]}')
    else:
        print("Не удалось получить данные.")
        return []  # Trả về danh sách rỗng nếu không nhận được phản hồi từ API
    
    return data

def speak(text, engine):
    engine.say(text)
    engine.runAndWait()

def record_volume():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print('Подготовка...')
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('Слушаю...')
        audio = r.listen(source)
    print('Речь получена.')
    try:
        query = r.recognize_google(audio, language='ru-RU')
        text = query.lower()
        print(f'Вы сказали: {text}')
        return text
    except sr.UnknownValueError:
        print('Извините, я не понял вашу речь.')
        speak('Извините, я не понял вашу речь.', engine)
        return None
    except sr.RequestError:
        print('Ошибка сервиса распознавания речи.')
        speak('Ошибка сервиса распознавания речи.', engine)

def command_recognition(command, data):
    if not data:  # Kiểm tra nếu data trống
        print('Данные о погоде отсутствуют.')
        speak('Извините, я не могу получить данные о погоде.', engine)
        return False

    commands = {
        'показать погоду': 0,
        'погода': 0,
        'описание': 0,
        'какая погода': 0,
        'показать температуру': 1,
        'температура': 1,
        'направление ветра': 2,
        'направление': 2,
        'скорость ветра': 3,
        'скорость': 3,
    }
    commands_exit = {
        'пока',
        'увидимся',
        'стоп',
        'выход',
        'остановить',
        'до свидания',
    }
    commands_write = {
        'записать',
        'сохранить в файл',
        'сохранить погоду',
        'логировать',
        'сохранить',
    }

    for exit_command in commands_exit:
        if exit_command in command:
            print('До свидания! Увидимся позже.')
            speak('До свидания! Увидимся позже.', engine)
            return True
        
    for write_command in commands_write:
        if write_command in command:
            with open("weather_log.txt", "a", encoding="utf-8") as f:
                f.write("Отчёт о погоде:\n")
                f.write(f" - Описание: {data[0]}\n")
                f.write(f" - Температура: {data[1]}\n")
                f.write(f" - Направление ветра: {data[2]}\n")
                f.write(f" - Скорость ветра: {data[3]}\n\n")
            print("Информация о погоде сохранена в файл.")
            speak("Информация о погоде сохранена в файл.", engine)
            return False
        
    temp_value = int(data[1].replace("°C", ""))
    wind_speed_value = int(data[3].replace("km/h", ""))

    if temp_value < 5 or wind_speed_value > 15:
        warning = "Внимание! Погода неблагоприятная. Лучше остаться дома."
        print(warning)
        speak("Не рекомендуется выходить при таких погодных условиях.", engine)

    if command in commands:
        speak(data[commands[command]], engine)
    else:
        print('Извините, я не понял команду.')
        speak('Извините, я не понял команду.', engine)

if __name__ == '__main__':
    # Lấy voice
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Microsoft Irina Desktop - Russian" in voice.name:
            engine.setProperty('voice', voice.id)
            break

    weather_data = Weather_Report()

    while True:
        command = record_volume()
        if command is None:
            continue
        should_exit = command_recognition(command, weather_data)
        if should_exit:
            break
