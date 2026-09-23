from pathlib import Path
import sounddevice as sd
import numpy as np
import soundfile as sf
from groq import Groq
from datetime import datetime

from helper import get_settings,logger
from memory import get_user_info,save_user_info,get_or_create_user_id

BASE_DIR = Path(__file__).resolve().parent.parent
settings = get_settings()
now = datetime.now()

user_id = get_or_create_user_id()

def record_and_transcribe(user_id: str=user_id, conversation_id=None, sample_rate: int = 16000,stage="Voice recording",model_name=settings.GROQ_VOICE_MODEL) -> str:
    """
    بتسجل صوت من الميك (تبدأ فورًا، وتوقف لما تدوس Enter)،
    تحفظه كملف .wav، وترجع النص المستخرج منه عبر Whisper.
    """
    
    # لو محدش بعت conversation_id صراحة، هات القيمة الحالية من ملف المستخدم مباشرة
    # (مش من متغيّر بيتحدد وقت تشغيل الشات — ده اللي كان بيسبب مشكلة "فتحلي شات")
    if conversation_id is None:
        record=get_user_info(user_id=user_id)          # dictionary كامل من memory/
        conversation_id = record["conversation_count"]   # وصول بالمفتاح، مش بـ ()

    # القايمة دي معمولة *جوه* الدالة، مش برّه خالص —
    # يعني كل استدعاء جديد للدالة بياخد قايمة فاضية جديدة،
    # فمفيش تداخل بين محادثة وتانية.
    recorded_chunks = []

    # الـ callback: بتتنفذ تلقائيًا من جوه sounddevice كل ما توصل قطعة صوت جديدة.
    # بما إنها *جوه* الدالة، هي شايفة recorded_chunks المحلية بتاعة نفس الاستدعاء ده
    # (مفهوم اسمه closure — الدالة الداخلية "فاكرة" متغيرات الدالة اللي اتعرفت جواها)
    def callback(indata, frames, time, status):
        recorded_chunks.append(indata.copy())

    # فتح الـ stream: هيفضل شغال طول ما احنا جوه الـ "with"
    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        # input() هنا هي الدالة العادية بتاعة بايثون (زي "print")،
        # مش تابعة لأي حاجة. البرنامج بيقف هنا لحد ما تدوس Enter.
        input("اضغط Enter لبدء ايقاف التسجيل...")
    # لما نخرج من الـ with، الـ stream بيتقفل تلقائيًا ويوقف الاستماع

    # دلوقتي recorded_chunks فيها قطع صغيرة كتير، كل واحدة numpy array منفصل.
    # concatenate بتلزقهم كلهم في array واحد كبير متصل
    full_recording = np.concatenate(recorded_chunks)

    # نجهز مسار الحفظ ونتأكد إن الفولدر موجود
    files_path = BASE_DIR / "data" / "chats_sounds" / f"{conversation_id}_{now.strftime("%d%m%Y_%H%M%S")}"
    files_path.mkdir(parents=True, exist_ok=True)
    existing_files = list(files_path.glob("recording*.wav"))
    i = len(existing_files)
    wav_name=f"recording{i}.wav"
    wav_path = files_path / wav_name
    sf.write(wav_path, full_recording, sample_rate)
    # نبعت الملف لـ Whisper عبر Groq، ونرجع النص المستخرج
    client = Groq(api_key=settings.GROQ_API_KEY.get_secret_value())
    with open(wav_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=f,
            model=model_name,
        )
    logger.info(f"[{stage}] Model Run successfuly : {model_name} (Groq) ✅")
    logger.debug(f"x_groq['id']:\n**{transcription.x_groq}**")
    i=+1
    #print(transcription)
    #print(type(transcription))
    return transcription.text


if __name__ == "__main__":
    # لازم تبعت user_id فعلي هنا وقت الاختبار (نفس الـ UUID الموجود في local_user.json)
    text = record_and_transcribe(user_id="6d2d1401-a273-45fc-943a-56737c6433fb")
    print("النص المستخرج:", text)