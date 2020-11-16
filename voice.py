# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 19:57:06 2020

@author: Anna Galsanova
"""
       
import io
import requests
from langdetect import detect
from pydub import AudioSegment

def json_extract(obj, key):
    arr = []
    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
 
    values = extract(obj, arr, key)
    return values

text = ""

file = input('Enter file name (without format): ')
file_new = file + ".txt"
try:
    file_in = open(file_new, "r", encoding="utf-8") 
    for line in file_in:
        text +=line
    print("Your text:\n", text)
except:
    print("File error")

key = "be5f4c47488e4d349dbb06b527492c7c"
auth_url = "https://francecentral.api.cognitive.microsoft.com/sts/v1.0/issueToken" 
lang_url = "https://francecentral.tts.speech.microsoft.com/cognitiveservices/voices/list"
auth_headers = { "Ocp-Apim-Subscription-Key": key, "Content-Length": "0", 
                "Content-type": "application/x-www-form-urlencoded" }

auth_response = requests.post(auth_url, headers=auth_headers)
token = auth_response.text

print("Bearer token:\n", token)

lang_headers= { "Authorization": "Bearer " + token }

lang_response = requests.get(lang_url, headers=lang_headers)
json_langs = lang_response.json()

print("Recognized language: ", detect(text))

lang_of_text = detect(text)
for voice in json_langs:
    locale = json_extract(voice,'Locale')
    string_l = ''.join(locale)
    if (string_l.find(lang_of_text) != -1):
        index = json_langs.index(voice)
        
print("Chosen dictor:\n", json_langs[index])

lang_voice = json_langs[index]

api_url = "https://francecentral.tts.speech.microsoft.com/cognitiveservices/v1"

api_headers = { "Authorization": "Bearer " + token, "X-Microsoft-OutputFormat": 
               "raw-16khz-16bit-mono-pcm", "Content-Type": "application/ssml+xml" }

lang = json_extract(lang_voice, 'Locale')
l = ''.join(lang)
gender = json_extract(lang_voice, 'Gender')
g = ''.join(gender)
name = json_extract(lang_voice, 'ShortName')
n = ''.join(name)

xml = "<speak version='1.0' xml:lang='" + l + "'><voice xml:lang='" + l + "' xml:gender='" + g + "' name='" + n + "'>" + text + "</voice></speak>"

print("XML request:\n", xml)

request = requests.post(api_url, headers = api_headers, data = xml)
response = request.content

wav_file = file + ".wav"

s = io.BytesIO(response)
audio = AudioSegment.from_raw(s, sample_width=2, frame_rate=16000, channels=1).export(wav_file, format='wav')