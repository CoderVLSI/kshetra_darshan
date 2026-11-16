# -*- coding: utf-8 -*-
"""
Generate authentic sacred Sanskrit chant audio for all 18 Maha Shakti Peethas
using ElevenLabs API with Sudha Devarakonda's voice clone (voice_id: AfGQOwNTk8JotVVaad3o).
"""
import os
import sys
import json
import urllib.request
import urllib.error

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = "AfGQOwNTk8JotVVaad3o"
OUTPUT_DIR = os.path.join("d:\\Kshetra_Darshan", "godot", "assets", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MANTRAS = {
    "kamakhya": "ॐ कामरूपे कामाख्या सर्वकामप्रदायिनी ।",
    "kalighat": "ॐ कालीघाटे कालिका देवी सर्वशत्रुविनाशिनी ।",
    "kashi_vishalakshi": "ॐ वाराणस्यां विशालाक्षी मणिकर्णी सुशोभिता ।",
    "kanchipuram_kamakshi": "ॐ कामाक्षी काञ्चिकापुरे सर्वमङ्गलदायिनी ।",
    "madurai_meenakshi": "ॐ मधुरायां मीनाक्षी सर्वपापप्रणाशिनी ।",
    "mysore_chamundeshwari": "ॐ चामुण्डा क्रौञ्चपत्तने महिषासुरमर्दिनी ।",
    "kolhapur_mahalakshmi": "ॐ कोल्हापुरे महालक्ष्मीः करवीरनिवासिनी ।",
    "tuljapur_bhavani": "ॐ तुळजापुरे भवानी त्वं भक्तानां वरदायिनी ।",
    "mahur_renuka": "ॐ माहुरे रेणुका देवी सर्वकामफलप्रदा ।",
    "alampur_jogulamba": "ॐ अलम्पुरे जोगुलाम्बा तुङ्गभद्रातटस्थिता ।",
    "srisailam_bhramaramba": "ॐ श्रीशैले भ्रमराम्बा च मल्लिकार्जुनवल्लभा ।",
    "pithapuram_puruhutika": "ॐ पीठापुरे पुरुहूतिका पादगयानिवासिनी ।",
    "jajpur_biraja": "ॐ जाजपुरे विरजा देवी वैतरणीतटस्थिता ।",
    "ujjain_mahakali": "ॐ उज्जयिन्यां महाकाली हरसिद्धिस्वरूपिणी ।",
    "prayag_madhaveswari": "ॐ प्रयागे माधवेश्वरी वेणीमाधवसन्निधौ ।",
    "gaya_mangalagauri": "ॐ गयायां मङ्गलगौरी सर्वमङ्गलमङ्गले ।",
    "pradyumna_shrinkhala": "ॐ प्रद्युम्ने शृङ्खला देवी बन्धनौघविनाशिनी ।",
    "lanka_shankari": "ॐ लङ्कायां शाङ्करी देवी सर्वदुःखविनाशिनी ।",
    "stotram_intro": "अष्टादश महा शक्ति पीठ दर्शनम् । ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे ॥",
}

def generate_audio(temple_id, text):
    out_file = os.path.join(OUTPUT_DIR, f"mantra_{temple_id}.mp3")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
        print(f"[SKIP] {temple_id} already exists ({os.path.getsize(out_file)} bytes)")
        return True

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.85
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            audio_bytes = resp.read()
            with open(out_file, "wb") as f:
                f.write(audio_bytes)
            print(f"[OK] {temple_id} -> {out_file} ({len(audio_bytes)} bytes)")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"[ERROR] {temple_id}: {e.code} - {err_msg}")
        return False
    except Exception as e:
        print(f"[ERROR] {temple_id}: {e}")
        return False

def main():
    print(f"Generating sacred audio with voice Sudha Devarakonda ({VOICE_ID}) for {len(MANTRAS)} chants...")
    success = 0
    for tid, text in MANTRAS.items():
        if generate_audio(tid, text):
            success += 1
    print(f"\nCompleted: {success}/{len(MANTRAS)} audio files generated.")

if __name__ == "__main__":
    main()

