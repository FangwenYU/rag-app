import openai
import os


def asr_file(audio_file):
    audio = open(audio_file, "rb")
    openai.api_key = os.environ['OPENAI_API_KEY']
    transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript


# def asr_stream(audio_stream):
#     # audio_file = io.BytesIO(audio_stream)
#     transcript = openai.Audio.transcribe_raw("whisper-1", audio_stream, 'test')
#     return transcript


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    print(asr_file('../tmp_file/郭美美.mp3').text)
