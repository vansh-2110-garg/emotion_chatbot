import streamlit as st
from textblob import TextBlob
from langdetect import detect
from googletrans import Translator
import random
from gtts import gTTS
import os
import tempfile

translator = Translator()

responses = {
    "happy": ["I'm glad to hear that! 😊", "That’s wonderful! How can I assist you further?"],
    "sad": ["I'm here for you. Can I help with anything?", "I’m sorry you’re feeling this way."],
    "angry": ["I'm really sorry about the inconvenience. Let me fix this for you.", "I understand your frustration. Let’s sort this out."],
    "confused": ["Let me clarify that for you.", "I can help explain that in more detail."],
    "neutral": ["Could you please tell me more?", "I’m here to help!"]
}

def detect_emotion(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.4:
        return "happy"
    elif polarity < -0.3:
        return "angry"
    elif -0.3 <= polarity <= 0.1:
        return "sad"
    elif 0.1 < polarity <= 0.4:
        return "confused"
    else:
        return "neutral"

def generate_reply(user_input):
    user_lang = detect(user_input)

    if user_lang != 'en':
        translated = translator.translate(user_input, dest='en')
        input_en = translated.text
    else:
        input_en = user_input

    emotion = detect_emotion(input_en)
    reply_en = random.choice(responses.get(emotion, responses["neutral"]))

    if user_lang != 'en':
        translated_back = translator.translate(reply_en, dest=user_lang)
        final_reply = translated_back.text
    else:
        final_reply = reply_en

    return final_reply, emotion, user_lang

def speak_text(text, lang):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

st.set_page_config(page_title="Multilingual Emotion Chatbot", page_icon="🤖")
st.title("🤖 Smart Emotion-Aware Chat Assistant")
st.markdown("Supports all languages • Detects Emotion • Translates • Speaks")

user_input = st.text_input("You:", placeholder="Type your message in any language...")

if user_input:
    with st.spinner("Processing..."):
        reply, emotion, lang_code = generate_reply(user_input)
        st.markdown(f"**Detected Emotion:** `{emotion}`")
        st.markdown(f"**Bot:** {reply}")

        try:
            audio_path = speak_text(reply, lang=lang_code)
            with open(audio_path, 'rb') as f:
                st.audio(f.read(), format='audio/mp3')
            os.remove(audio_path)
        except Exception as e:
            st.warning("Voice failed: " + str(e))
