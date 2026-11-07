import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
import edge_tts

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\hp-laptop1\flow-mcp-out")

EP1_DIR = ROOT / "Leo_Time_Freeze"
EP2_DIR = ROOT / "Leo_Episode_2"
EP3_DIR = ROOT / "Leo_Episode_3"

def master_audio(raw, out):
    dsp = (
        "highpass=f=75,"
        "equalizer=f=120:width_type=o:w=1.2:g=3.5,"
        "equalizer=f=3200:width_type=o:w=1.0:g=3.0,"
        "equalizer=f=8000:width_type=o:w=1.5:g=2.5,"
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=60:makeup=2,"
        "loudnorm=I=-14:TP=-1.0:LRA=7"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", raw,
        "-af", dsp,
        "-ar", "48000", "-ac", "2",
        out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def gen_voice(text, raw_path, rate="+10%", pitch="-2Hz"):
    comm = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate=rate, pitch=pitch)
    bounds = []
    with open(raw_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                bounds.append({
                    "start": chunk["offset"] / 10000000,
                    "dur": chunk["duration"] / 10000000,
                    "text": chunk["text"]
                })
    return bounds

def render_film(clips, audio, ass_path, output, duration):
    filter_parts = []
    concat_inputs = []
    for i in range(len(clips)):
        filter_parts.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,fps=24,setpts=PTS-STARTPTS[v{i}]")
        concat_inputs.append(f"[v{i}]")

    concat_chain = f"{''.join(concat_inputs)}concat=n={len(clips)}:v=1:a=0[vmerged]"
    filter_parts.append(concat_chain)
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    filter_parts.append(f"[vmerged]ass='{escaped_ass}'[vout]")
    full_filter = ";".join(filter_parts)

    inputs = []
    for c in clips:
        inputs.extend(["-i", c])

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", audio,
        "-filter_complex", full_filter,
        "-map", "[vout]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "24",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", str(round(duration, 2)),
        output
    ]
    subprocess.run(cmd, check=True)

# =========================================================================
# 1. PROCESS EPISODE 1
# =========================================================================
async def process_ep1():
    print("\n" + "="*50)
    print("  Processing Episode 1 (Natural Urdu Voice)")
    print("="*50)
    
    ep1_text = (
        "کیا آپ جانتے ہیں کہ اٹھارہ سو نوے میں، لندن کے کلاک ٹاور میں ایک ایسا راز چھپا تھا، جس نے وقت کو ہی روک دیا؟ "
        "رات کے ٹھیک تین بج کر سترہ منٹ پر، جب لیو نے جادوئی گھڑی کو گھمایا، تو بارش ہوا میں ٹھہر گئی! "
        "پوری دنیا تھم گئی! "
        "کیا وقت دوبارہ چل پائے گا؟ "
        "دیکھیے اگلے حصے میں!"
    )
    raw = str(EP1_DIR / "raw_audio_clean.mp3")
    mastered = str(EP1_DIR / "mastered_clean.wav")
    bounds = await gen_voice(ep1_text, raw, rate="-12%", pitch="-2Hz")
    master_audio(raw, mastered)
    
    ass_path = str(EP1_DIR / "ep1_clean.ass")
    ass_content = """[Script Info]
Title: Leo Episode 1
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,Impact,44,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.0,2.5,2,40,40,280,1
Style: Yellow,Impact,46,&H0000E5FF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.5,3.0,2,40,40,280,1
Style: CTA,Impact,48,&H0000FFFF,&H000000FF,&H00000000,&HFF0000FF,-1,0,0,0,105,105,1.5,0,1,5.0,3.5,2,30,30,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.10,0:00:04.20,Yellow,,0,0,0,,KYA AAP JAANTE HAIN KE 1890 MEIN...
Dialogue: 0,0:00:04.25,0:00:08.60,White,,0,0,0,,LONDON KE CLOCK TOWER MEIN\\NEK AISA RAAZ CHUPA THA...
Dialogue: 0,0:00:08.65,0:00:11.80,Yellow,,0,0,0,,JISNE WAQT KO HI ROK DIYA!
Dialogue: 0,0:00:11.85,0:00:14.20,White,,0,0,0,,RAAT KE THEEK 3:17 PAR...
Dialogue: 0,0:00:14.25,0:00:16.30,Yellow,,0,0,0,,JAB LEO NE JAADUI GHADI KO GHUMAYA,
Dialogue: 0,0:00:16.35,0:00:18.65,White,,0,0,0,,POORI DUNIYA THAM GAYI!
Dialogue: 0,0:00:18.70,0:00:21.60,Yellow,,0,0,0,,KYA WAQT DOBAARA CHAL PAAYE GA?
Dialogue: 0,0:00:21.65,0:00:26.50,CTA,,0,0,0,,DEKHIYE AGLE HISSAY MEIN!
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content.strip())
        
    out_mp4 = str(EP1_DIR / "Leo_Episode_1_Final.mp4")
    render_film([str(EP1_DIR / "merged_raw_27s.mp4")], mastered, ass_path, out_mp4, 28.2)
    print(f"Episode 1 Complete: {out_mp4}")

# =========================================================================
# 2. PROCESS EPISODE 2
# =========================================================================
async def process_ep2():
    print("\n" + "="*50)
    print("  Processing Episode 2 (Natural Urdu Voice)")
    print("="*50)
    
    ep2_text = (
        "پچھلی بار: لیو نے پورے لندن میں وقت کو روک دیا تھا۔ "
        "مگر اب، وہ جمی ہوئی بارش پر سیڑھیوں کی طرح چل سکتا تھا! "
        "جیسے ہی وہ بگ بین پر چڑھا، ایک سونے کی چابی کا سوراخ ملا! "
        "مگر چابی گھومتے ہی سائے زندہ ہو گئے! ایک پراسرار محافظ حرکت کرنے لگا! "
        "کیا لیو اپنی جان بچا پائے گا؟ "
        "ملتے ہیں اگلے حصے میں!"
    )
    raw = str(EP2_DIR / "raw_audio_clean.mp3")
    mastered = str(EP2_DIR / "mastered_clean.wav")
    bounds = await gen_voice(ep2_text, raw, rate="+8%", pitch="-2Hz")
    master_audio(raw, mastered)

    ass_path = str(EP2_DIR / "ep2_clean.ass")
    ass_content = """[Script Info]
Title: Leo Episode 2
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: RecapBadge,Impact,38,&H0000FFFF,&H000000FF,&H00000000,&HFF0000FF,-1,0,0,0,105,105,2,0,1,4.5,2.5,8,30,30,90,1
Style: White,Impact,44,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.0,2.5,2,40,40,280,1
Style: Yellow,Impact,46,&H0000E5FF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.5,3.0,2,40,40,280,1
Style: CTA,Impact,48,&H0000FFFF,&H000000FF,&H00000000,&HFF0000FF,-1,0,0,0,105,105,1.5,0,1,5.0,3.5,2,30,30,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.10,0:00:03.95,RecapBadge,,0,0,0,,[ PICHLI BAAR / RECAP ]
Dialogue: 0,0:00:00.10,0:00:03.95,Yellow,,0,0,0,,LEO NE POORE LONDON MEIN\\NWAQT KO ROK DIYA THA...
Dialogue: 0,0:00:03.95,0:00:07.75,White,,0,0,0,,MAGAR AB, WOH JAMI HUI BAARISH PAR\\NSEERHIYON KI TARAH CHAL SAKTA THA!
Dialogue: 0,0:00:07.75,0:00:12.05,Yellow,,0,0,0,,JAISE HI WOH BIG BEN PAR CHARHA,\\nEK SONE KA CHABI KA SOORAKH MILA!
Dialogue: 0,0:00:12.05,0:00:14.95,White,,0,0,0,,MAGAR CHABI GHUUMTE HI\\nSAAYE ZINDA HO GAYE!
Dialogue: 0,0:00:14.98,0:00:17.85,Yellow,,0,0,0,,EK SHADOW GUARDIAN HARKAT KARNE LAGA!
Dialogue: 0,0:00:17.89,0:00:20.35,White,,0,0,0,,KYA LEO APNI JAAN BACHA PAAYE GA?
Dialogue: 0,0:00:20.37,0:00:23.80,CTA,,0,0,0,,MILTE HAIN AGLE HISSAY MEIN!
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content.strip())

    clips = [
        str(EP2_DIR / "recap_3s.mp4"),
        str(EP2_DIR / "scene-01.mp4"),
        str(EP2_DIR / "scene-02.mp4"),
        str(EP2_DIR / "scene-03.mp4"),
        str(EP2_DIR / "scene-04.mp4"),
        str(EP2_DIR / "scene-05.mp4"),
        str(EP2_DIR / "scene-06.mp4"),
    ]
    out_mp4 = str(EP2_DIR / "Leo_Episode_2_Final.mp4")
    render_film(clips, mastered, ass_path, out_mp4, 24.0)
    print(f"Episode 2 Complete: {out_mp4}")

# =========================================================================
# 3. PROCESS EPISODE 3
# =========================================================================
async def process_ep3():
    print("\n" + "="*50)
    print("  Processing Episode 3 (Natural Urdu Voice)")
    print("="*50)

    ep3_text = (
        "پچھلی بار: وقت کے سکوت میں ایک پراسرار محافظ نے لیو کو گھیر لیا تھا۔ "
        "جیسے ہی اس نے حملہ کیا، لیو کی گھڑی سے سنہری گیئرز کی ڈھال نکل آئی! "
        "دھماکے سے نقاب ہٹا تو محافظ کے سینے پر بھی وہی قدیم علامت چمک رہی تھی۔ "
        "وہ کوئی دشمن نہیں، بلکہ ماضی کا محافظ تھا! "
        "اور اس نے اشارہ کیا کہ اصل خطرہ آسمانوں کے اس پار ہے۔ "
        "اگلا حصہ دیکھنا مت بھولیے گا!"
    )
    raw = str(EP3_DIR / "raw_audio_clean.mp3")
    mastered = str(EP3_DIR / "mastered_clean.wav")
    bounds = await gen_voice(ep3_text, raw, rate="+8%", pitch="-2Hz")
    master_audio(raw, mastered)

    ass_path = str(EP3_DIR / "ep3_clean.ass")
    ass_content = """[Script Info]
Title: Leo Episode 3
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: RecapBadge,Impact,38,&H0000FFFF,&H000000FF,&H00000000,&HFF0000FF,-1,0,0,0,105,105,2,0,1,4.5,2.5,8,30,30,90,1
Style: White,Impact,44,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.0,2.5,2,40,40,280,1
Style: Yellow,Impact,46,&H0000E5FF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,1.2,0,1,4.5,3.0,2,40,40,280,1
Style: CTA,Impact,48,&H0000FFFF,&H000000FF,&H00000000,&HFF0000FF,-1,0,0,0,105,105,1.5,0,1,5.0,3.5,2,30,30,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.10,0:00:05.05,RecapBadge,,0,0,0,,[ PICHLI BAAR / RECAP ]
Dialogue: 0,0:00:00.10,0:00:05.05,Yellow,,0,0,0,,WAQT KE SUKOOT MEIN EK MUHAAFIZ\\NNE LEO KO GHER LIYA THA...
Dialogue: 0,0:00:05.05,0:00:09.65,White,,0,0,0,,JAISE HI USNE HAMLA KIYA...\\NLEO KI GHADI SE DHAAL NIKAL AAYI!
Dialogue: 0,0:00:09.69,0:00:14.75,Yellow,,0,0,0,,DHAMAKAY SE NAQAB HATA TOH\\NMUHAAFIZ PAR BHI WOHI NISHAN THA!
Dialogue: 0,0:00:14.79,0:00:18.05,White,,0,0,0,,WOH KOI DUSHMAN NAHI THA...\\NBALKE MAAZI KA NIGEHBAAN THA!
Dialogue: 0,0:00:18.08,0:00:22.00,Yellow,,0,0,0,,AUR USNE ISHARA KIYA KE\\NASAL KHATRA ASMAAN KE PAAR HAI!
Dialogue: 0,0:00:22.04,0:00:24.80,CTA,,0,0,0,,AGLA HISSA DEKHNA MAT BHOOLIYE GA!
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content.strip())

    clips = [
        str(EP3_DIR / "recap_5s.mp4"),
        str(EP3_DIR / "scene-01.mp4"),
        str(EP3_DIR / "scene-02.mp4"),
        str(EP3_DIR / "scene-03.mp4"),
        str(EP3_DIR / "scene-06.mp4"),
        str(EP3_DIR / "scene-07.mp4"),
    ]
    out_mp4 = str(EP3_DIR / "Leo_Episode_3_Final.mp4")
    render_film(clips, mastered, ass_path, out_mp4, 25.0)
    print(f"Episode 3 Complete: {out_mp4}")

# =========================================================================
# MAIN
# =========================================================================
async def main():
    print("Starting Rebuild of All 3 Videos with Natural Audio Hooks...")
    await process_ep1()
    await asyncio.sleep(1)
    await process_ep2()
    await asyncio.sleep(1)
    await process_ep3()
    print("\n" + "="*50)
    print("ALL 3 EPISODES SUCCESSFULLY REBUILT AND RENDERED!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
