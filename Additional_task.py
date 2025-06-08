import pyttsx3
import speech_recognition as sr
import json
import random
import requests
import re
import webbrowser


def speak(text, engine):
    engine.say(text)
    engine.runAndWait()

def search_dictionary(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    # Gửi yêu cầu GET tới API
    response = requests.get(url)

    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("No data found.")

def record_volume(engine):
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print('Preparing...')
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('Listening...')
        audio = r.listen(source)
    print('Speech received.')
    try:
        query = r.recognize_google(audio, language='en-US')
        text = query.lower()
        print(f'You said: {text}')
        return text
    except sr.UnknownValueError:
        print('Sorry, I did not understand your speech.')
        speak('Sorry, I did not understand your speech.', engine)
        return None
    except sr.RequestError:
        print('Speech recognition service error.')
        speak('Speech recognition service error.', engine)

def command_recognition(command, dictionary_data, engine):
    if not dictionary_data:  # Check if data is empty
        print('Diction data is missing.')
        speak('Sorry, I cannot retrieve Diction data.', engine)
        return False, dictionary_data  # Trả về dictionary_data chưa thay đổi

    commands_write = {
        'record',
        'save to file',
        'save weather',
        'log',
        'save',
    }
    commands_exit = {
        'goodbye',
        'see you',
        'stop',
        'exit',
        'terminate',
        'farewell',
    }

    for exit_command in commands_exit:
        if exit_command in command:
            print('Goodbye! See you later.')
            speak('Goodbye! See you later.', engine)
            return True, dictionary_data  # Trả về dictionary_data chưa thay đổi
        
    for write_command in commands_write:
        if write_command in command:
            # Lưu dữ liệu vào tệp JSON
            word_to_save = dictionary_data[0]["word"]  # Lấy từ cuối cùng trong lệnh để lưu
            with open(f"{word_to_save}_definition.json", "w", encoding="utf-8") as f:
                json.dump(dictionary_data, f, ensure_ascii=False, indent=4)

            print(f"Data saved to {word_to_save}_definition.json")
            return False, dictionary_data  # Trả về dictionary_data chưa thay đổi

    if 'find' in command:
        words = command.split(' ')
        if len(word) > 1:  # Kiểm tra xem có ít nhất một từ sau 'find'
            word_to_search = words[-1]
            dictionary_data = search_dictionary(word_to_search)  # Cập nhật dữ liệu từ điển
            
            if dictionary_data:  # Kiểm tra dữ liệu có được nhận không
                print("Information received!")
                speak("Information received!", engine)
            else:
                print("No data found.")
                speak("No data found.", engine)
        else:
            print("Please provide a word to search for.")  # Thông báo khi không có từ nào sau 'find'
            speak("Please provide a word to search for.", engine)

    elif command == 'meaning':
        # Truy xuất nghĩa của từ "glass" từ phần 'meanings' trong JSON
        meanings = dictionary_data[0]['meanings']
        for meaning in meanings:
            for definition in meaning['definitions']:
                print(f"Meaning: {definition['definition']}")
                speak(definition['definition'], engine)

    elif command == 'example':
        # Truy xuất ví dụ từ phần 'meanings'
        meanings = dictionary_data[0]['meanings']
        for meaning in meanings:
            for definition in meaning['definitions']:
                # Kiểm tra nếu có khóa 'example' trước khi in
                if 'example' in definition:
                    print(f"Example: {definition['example']}")
                    speak(definition['example'], engine)

    elif command == 'link':
        # Truy xuất liên kết từ phần 'sourceUrls'
        webbrowser.open(dictionary_data[0]['sourceUrls'][0])  # Mở liên kết đầu tiên
    
    else:
        print('Sorry, I did not understand the command.')
        speak('Sorry, I did not understand the command.', engine)
    
    return False, dictionary_data  # Trả về dictionary_data chưa thay đổi


if __name__ == '__main__':

    # Lấy voice
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    while True:
        word = input("Input command search: ")
        if 'find' in word:
            word_t = word.split(" ")[-1]
        dictionary_data = search_dictionary(word_t)
        
        if not dictionary_data:
            print("Failed to get dictionary data.")
            speak("Failed to get dictionary data.", engine)
        else:
            print("Information received!")
            break

    # Input voice command
    while True:
        command = record_volume(engine)
        if command is None:
            continue
        should_exit, dictionary_data = command_recognition(command, dictionary_data, engine)  # Lưu dictionary_data mới
        if should_exit:
            break

    
    