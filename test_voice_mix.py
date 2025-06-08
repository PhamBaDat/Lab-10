import pyttsx3
import speech_recognition as sr

text = 'Hello, im David Rebecca'
tts = pyttsx3.init()
rate = tts.getProperty('rate')  # Tốc độ phát âm
tts.setProperty('rate', rate-40)

volume = tts.getProperty('volume')  # Âm lượng giọng nói
tts.setProperty('volume', volume+0.9)

voices = tts.getProperty('voices')
for voice in voices:
    print(f"Voice: {voice.name}")

# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

# Đặt giọng nói mặc định
tts.setProperty('voice', 'en')

# Thử cài đặt giọng nói yêu thích
for voice in voices:
    if voice.name == 'Microsoft David Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

tts.say(text)
tts.runAndWait()