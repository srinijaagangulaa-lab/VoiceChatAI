import streamlit as st
import speech_recognition as sr
import subprocess
import sys
import os
import hashlib
import html
import re
import base64
import time


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Voice Chat AI",
    page_icon="🎙️",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "messages": [],
    "processed_audio": None,
    "audio_key": 0,

    "ai_process": None,
    "ai_running": False,
    "ai_status": "Ready",

    "ai_output_file": None,
    "ai_error_file": None,
    "generation_id": None,

    "tts_process": None,

    "assistant_saved": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

.stApp {
    background:
       radial-gradient(
            circle at 10% 10%,
            rgba(110, 75, 180, 0.28),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(45, 105, 170, 0.28),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #090714,
            #0d1220,
            #100b1b
        );
}

.block-container {
    max-width: 900px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    text-align: center;
    padding: 20px 10px 10px;
}

.hero-icon {
    width: 82px;
    height: 82px;

    margin: auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background:
        linear-gradient(
            145deg,
            #ffffff,
            #e8deff
        );

    box-shadow:
        0 15px 40px rgba(90, 70, 140, 0.18);

    font-size: 38px;
}

.hero-title {
    margin-top: 18px;

    font-size: 44px;
    font-weight: 800;

    color: #604a91;
}

.hero-subtitle {
    margin-top: 7px;

    color: #777080;

    font-size: 17px;
}

.status {
    display: inline-flex;

    align-items: center;
    gap: 8px;

    margin-top: 15px;

    padding: 8px 16px;

    border-radius: 30px;

    background: rgba(255,255,255,0.85);

    color: #665f70;

    font-size: 13px;
}

.status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #68c88b;
}


/* =========================================================
   VOICE CARD
   ========================================================= */

.voice-card {
    margin-top: 25px;

    padding: 38px 25px;

    border-radius: 30px;

    background: rgba(255,255,255,0.75);

    border: 1px solid rgba(255,255,255,0.9);

    box-shadow:
        0 20px 50px rgba(78,64,110,0.10);

    text-align: center;
}

.voice-orb {
    width: 135px;
    height: 135px;

    margin: auto;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background:
        radial-gradient(
            circle at 35% 30%,
            #ffffff,
            #eee6ff 55%,
            #ddd1ff
        );

    box-shadow:
        0 0 0 12px rgba(126,94,190,0.05),
        0 0 0 25px rgba(126,94,190,0.025),
        0 20px 45px rgba(99,75,153,0.18);

    font-size: 50px;
}

.voice-title {
    margin-top: 20px;

    color: black;

    font-size: 22px;
    font-weight: 700;
}

.voice-description {
    margin-top: 7px;

    color: #817a8d;

    font-size: 14px;
}


/* =========================================================
   CHAT
   ========================================================= */

.section-title {
    margin-top: 30px;
    margin-bottom: 15px;

    color: #030164;

    font-size: 20px;
    font-weight: 700;
}

.user-message {
    display: flex;

    justify-content: flex-end;

    margin: 15px 0;
}

.user-bubble {
    max-width: 72%;

    padding: 14px 18px;

    border-radius:
        20px
        20px
        5px
        20px;

    background:
        linear-gradient(
            135deg,
            #ddd1ff,
            #e9dfff
        );

    color: #45385d;

    line-height: 1.5;

    box-shadow:
        0 7px 20px rgba(95,73,145,0.08);
}

.ai-message {
    display: flex;

    align-items: flex-start;

    gap: 10px;

    margin: 15px 0;
}

.ai-avatar {
    width: 40px;
    height: 40px;

    min-width: 40px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background:
        linear-gradient(
            135deg,
            #eee5ff,
            #dfeaff
        );

    font-size: 18px;
}

.ai-bubble {
    max-width: 78%;

    padding: 15px 18px;

    border-radius:
        5px
        20px
        20px
        20px;

    background: rgba(255,255,255,0.92);

    color: #4e4858;

    line-height: 1.6;

    box-shadow:
        0 7px 22px rgba(80,70,100,0.07);
}

.empty-chat {
    text-align: center;

    padding: 30px;

    color: #9a93a5;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {

    min-height: 48px;

    border: none;

    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            #6b51a2,
            #8065bd
        );

    color: white;

    font-weight: 700;

    box-shadow:
        0 10px 25px rgba(101,78,157,0.18);
}

.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 14px 30px rgba(101,78,157,0.25);
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    margin-top: 30px;

    text-align: center;

    color: #a09aaa;

    font-size: 12px;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media(max-width:600px) {

    .hero-title {
        font-size: 34px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

    .voice-orb {
        width: 115px;
        height: 115px;

        font-size: 42px;
    }

    .user-bubble,
    .ai-bubble {
        max-width: 88%;
    }
}

</style>
""")


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="hero-icon">
        🎙️
    </div>

    <div class="hero-title">
        Voice Chat AI
    </div>

    <div class="hero-subtitle">
        A natural voice conversation with your personal AI assistant
    </div>

    <div class="status">
        <span class="status-dot"></span>
        AI Assistant • Ready
    </div>

</div>
""")


# ============================================================
# VOICE CARD
# ============================================================

st.html("""
<div class="voice-card">

    <div class="voice-orb">
        🎙️
    </div>

    <div class="voice-title">
        Ready when you are
    </div>

    <div class="voice-description">
        Record your question using the microphone below
    </div>

</div>
""")


# ============================================================
# CLEAN AI TEXT
# ============================================================

def clean_ai_text(text):

    if not text:
        return ""

    # Remove ANSI escape sequences
    ansi_pattern = re.compile(
        r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    )

    text = ansi_pattern.sub("", text)

    # Remove replacement characters
    text = text.replace("�", "")

    # Remove common terminal artifacts
    text = text.replace("[K", "")
    text = text.replace("[2K", "")
    text = text.replace("[1K", "")
    text = text.replace("[0K", "")

    # Remove other control characters
    text = "".join(
        char
        for char in text
        if char == "\n"
        or char == "\t"
        or ord(char) >= 32
    )

    # Remove excessive blank lines
    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    return text.strip()


# ============================================================
# SPEECH TO TEXT
# ============================================================

def speech_to_text(audio_file):

    recognizer = sr.Recognizer()

    temp_audio = "user_voice.wav"

    try:

        with open(
            temp_audio,
            "wb"
        ) as f:

            f.write(
                audio_file.getvalue()
            )

        with sr.AudioFile(
            temp_audio
        ) as source:

            audio = recognizer.record(
                source
            )

        text = recognizer.recognize_google(
            audio
        )

        return text.strip()

    except sr.UnknownValueError:

        return None

    except sr.RequestError:

        st.error(
            "Speech recognition service is unavailable."
        )

        return None

    except Exception as e:

        st.error(
            f"Speech error: {e}"
        )

        return None

    finally:

        if os.path.exists(temp_audio):

            try:
                os.remove(temp_audio)
            except:
                pass


# ============================================================
# START AI
# ============================================================

def start_ai(question):

    generation_id = (
        hashlib.md5(
            f"{question}-{time.time()}".encode()
        ).hexdigest()
    )

    output_file = (
        f"ai_output_{generation_id}.txt"
    )

    error_file = (
        f"ai_error_{generation_id}.txt"
    )


    # Python code executed in a separate process.
    #
    # IMPORTANT:
    # We use the Ollama Python API here instead of
    # "ollama run", so terminal escape characters
    # don't get mixed into the response.

    worker_code = r'''
import sys
import base64
import ollama

question = base64.b64decode(
    sys.argv[1]
).decode("utf-8")

try:

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    answer = response["message"]["content"]

    print(
        answer,
        end=""
    )

except Exception as e:

    print(
        f"ERROR: {e}",
        file=sys.stderr
    )

    sys.exit(1)
'''


    encoded_question = base64.b64encode(
        question.encode("utf-8")
    ).decode("ascii")


    try:

        process = subprocess.Popen(

            [
                sys.executable,
                "-c",
                worker_code,
                encoded_question
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0
            )
        )


        st.session_state.ai_process = process

        st.session_state.ai_running = True

        st.session_state.ai_status = (
            "AI is thinking..."
        )

        st.session_state.ai_output_file = (
            output_file
        )

        st.session_state.ai_error_file = (
            error_file
        )

        st.session_state.generation_id = (
            generation_id
        )

        st.session_state.assistant_saved = False


        # ----------------------------------------------------
        # Background reader
        # ----------------------------------------------------

        import threading


        def collect_result():

            stdout_data, stderr_data = (
                process.communicate()
            )


            try:

                answer = stdout_data.decode(
                    "utf-8",
                    errors="replace"
                )

            except:

                answer = str(
                    stdout_data
                )


            answer = clean_ai_text(
                answer
            )


            try:

                with open(
                    output_file,
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(answer)

            except:
                pass


            if stderr_data:

                try:

                    error_text = stderr_data.decode(
                        "utf-8",
                        errors="replace"
                    )

                except:

                    error_text = str(
                        stderr_data
                    )


                try:

                    with open(
                        error_file,
                        "w",
                        encoding="utf-8"
                    ) as f:

                        f.write(
                            error_text
                        )

                except:
                    pass


        thread = threading.Thread(
            target=collect_result,
            daemon=True
        )

        thread.start()


    except Exception as e:

        st.error(
            f"Could not start AI: {e}"
        )


# ============================================================
# STOP AI GENERATION
# ============================================================

def stop_ai():

    process = st.session_state.ai_process


    if process is not None:

        try:

            if process.poll() is None:

                process.terminate()

                time.sleep(0.2)

                if process.poll() is None:

                    process.kill()

        except:

            pass


    st.session_state.ai_process = None

    st.session_state.ai_running = False

    st.session_state.ai_status = (
        "Response stopped"
    )


    # IMPORTANT:
    #
    # We DO NOT save the incomplete response.
    #
    # This fixes the problem shown in your screenshot.


# ============================================================
# START AI VOICE
# ============================================================

def speak(text):

    stop_voice()


    # Base64 avoids quotation/apostrophe problems.

    encoded_text = base64.b64encode(
        text.encode("utf-8")
    ).decode("ascii")


    # Run pyttsx3 in a completely separate Python process.
    #
    # This prevents:
    #
    # RuntimeError: run loop already started

    tts_code = r'''
import sys
import base64
import pyttsx3

text = base64.b64decode(
    sys.argv[1]
).decode("utf-8")

engine = pyttsx3.init()

engine.setProperty(
    "rate",
    170
)

engine.setProperty(
    "volume",
    1.0
)

engine.say(text)

engine.runAndWait()

engine.stop()
'''


    try:

        process = subprocess.Popen(

            [
                sys.executable,
                "-c",
                tts_code,
                encoded_text
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0
            )
        )


        st.session_state.tts_process = process


    except Exception as e:

        st.error(
            f"Voice output error: {e}"
        )


# ============================================================
# STOP AI VOICE
# ============================================================

def stop_voice():

    process = st.session_state.tts_process


    if process is not None:

        try:

            if process.poll() is None:

                process.terminate()

                time.sleep(0.2)

                if process.poll() is None:

                    process.kill()

        except:

            pass


    st.session_state.tts_process = None


# ============================================================
# READ AI RESPONSE
# ============================================================

def get_ai_response():

    file_name = (
        st.session_state.ai_output_file
    )


    if not file_name:
        return ""


    if not os.path.exists(
        file_name
    ):
        return ""


    try:

        with open(
            file_name,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:

            text = f.read()


        return clean_ai_text(
            text
        )


    except:

        return ""


# ============================================================
# MICROPHONE
# ============================================================

st.markdown("### 🎙️ Ask your question")


audio = st.audio_input(
    "Record your voice",
    sample_rate=16000,
    key=f"microphone_{st.session_state.audio_key}"
)


# ============================================================
# PROCESS NEW RECORDING
# ============================================================

if audio is not None:

    audio_hash = hashlib.md5(
        audio.getvalue()
    ).hexdigest()


    # Process this recording ONLY once.

    if audio_hash != st.session_state.processed_audio:

        st.session_state.processed_audio = (
            audio_hash
        )


        if st.session_state.ai_running:

            st.warning(
                "AI is already responding. "
                "Stop the current response first."
            )

        else:

            with st.spinner(
                "🎧 Converting your voice to text..."
            ):

                user_text = speech_to_text(
                    audio
                )


            if user_text:

                # =========================================
                # USER MESSAGE
                # =========================================

                st.session_state.messages.append({

                    "role": "user",

                    "content": user_text

                })


                # =========================================
                # START AI
                # =========================================

                start_ai(
                    user_text
                )


                st.rerun()


            else:

                st.warning(
                    "I couldn't understand your voice. "
                    "Please try again."
                )


# ============================================================
# AI MONITOR
# ============================================================

if st.session_state.ai_running:

    @st.fragment(
        run_every=0.5
    )
    def monitor_ai():

        process = (
            st.session_state.ai_process
        )


        # -----------------------------------------------
        # PROCESS STILL RUNNING
        # -----------------------------------------------

        if process is not None:

            if process.poll() is None:

                st.info(
                    "🤖 AI is thinking..."
                )


                if st.button(
                    "⏹️ Stop AI Response",
                    use_container_width=True,
                    key="stop_ai_button"
                ):

                    stop_ai()

                    st.rerun()


                return


        # -----------------------------------------------
        # PROCESS FINISHED
        # -----------------------------------------------

        response = get_ai_response()


        # Check for errors

        error_file = (
            st.session_state.ai_error_file
        )


        error_text = ""


        if error_file and os.path.exists(
            error_file
        ):

            try:

                with open(
                    error_file,
                    "r",
                    encoding="utf-8",
                    errors="replace"
                ) as f:

                    error_text = f.read().strip()

            except:

                pass


        # -----------------------------------------------
        # ERROR
        # -----------------------------------------------

        if error_text:

            st.session_state.ai_running = False

            st.session_state.ai_process = None

            if "model" in error_text.lower():

                st.error(
                    "Ollama could not find llama3.2. "
                    "Run: ollama pull llama3.2"
                )

            else:

                st.error(
                    error_text
                )

            st.rerun()


        # -----------------------------------------------
        # SUCCESS
        # -----------------------------------------------

        if response:

            if not st.session_state.assistant_saved:

                st.session_state.messages.append({

                    "role": "assistant",

                    "content": response

                })

                st.session_state.assistant_saved = True


                # Start voice

                speak(
                    response
                )


            st.session_state.ai_running = False

            st.session_state.ai_process = None

            st.session_state.ai_status = (
                "Response complete"
            )


            st.rerun()


        else:

            st.warning(
                "The AI returned an empty response."
            )

            st.session_state.ai_running = False

            st.session_state.ai_process = None

            st.rerun()


    monitor_ai()


# ============================================================
# AI VOICE STOP BUTTON
# ============================================================

tts_process = (
    st.session_state.tts_process
)


if tts_process is not None:

    if tts_process.poll() is None:

        st.warning(
            "🔊 AI is speaking..."
        )


        if st.button(
            "🔇 Stop AI Voice",
            use_container_width=True,
            key="stop_voice_button"
        ):

            stop_voice()

            st.rerun()

    else:

        st.session_state.tts_process = None


# ============================================================
# DIVIDER
# ============================================================

st.html("""
<div style="
    height:1px;
    margin:30px 0;
    background:rgba(100,90,120,0.12);
"></div>
""")


# ============================================================
# CONVERSATION
# ============================================================

st.html("""
<div class="section-title">
    💬 Conversation
</div>
""")


if not st.session_state.messages:

    st.html("""
    <div class="empty-chat">
        ✨ Your conversation will appear here
    </div>
    """)


else:

    for message in st.session_state.messages:

        content = html.escape(
            message["content"]
        )


        # ================================================
        # USER
        # ================================================

        if message["role"] == "user":

            st.html(
                f"""
                <div class="user-message">

                    <div class="user-bubble">

                        👤 <b>You</b><br>

                        {content}

                    </div>

                </div>
                """
            )


        # ================================================
        # AI
        # ================================================

        else:

            st.html(
                f"""
                <div class="ai-message">

                    <div class="ai-avatar">
                        🤖
                    </div>

                    <div class="ai-bubble">

                        <b>AI</b><br>

                        {content}

                    </div>

                </div>
                """
            )


# ============================================================
# CLEAR CHAT
# ============================================================

st.markdown("")


if st.button(
    "🗑️ Clear Chat",
    use_container_width=True,
    key="clear_chat"
):

    # Stop AI generation

    stop_ai()


    # Stop AI voice

    stop_voice()


    # Clear messages

    st.session_state.messages = []


    # Forget previous audio

    st.session_state.processed_audio = None


    # Create a completely new microphone widget

    st.session_state.audio_key += 1


    # Reset AI

    st.session_state.ai_running = False

    st.session_state.ai_process = None

    st.session_state.ai_output_file = None

    st.session_state.ai_error_file = None

    st.session_state.generation_id = None

    st.session_state.assistant_saved = False

    st.session_state.ai_status = "Ready"


    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">
    🎧 Voice Chat AI • Streamlit + Ollama
</div>
""")