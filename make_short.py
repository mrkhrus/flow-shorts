"""
Google Flow Shorts Automation Pipeline
Author: Ali Noor
Automates Urdu Voiceover (Edge-TTS), DSP Audio Mastering, Frame-Accurate Captions, and FFmpeg Rendering.
"""

import os
import sys
import json
import argparse
import asyncio
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = Path(os.path.expanduser("~")) / "flow-mcp-out"

def run_cmd(cmd, check=True):
    print(f"[*] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, check=check, shell=isinstance(cmd, str))

async def generate_urdu_tts(text: str, output_path: str, rate: str = "+10%", pitch: str = "-2Hz"):
    import edge_tts
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate=rate, pitch=pitch)
    boundaries = []
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                boundaries.append({
                    "offset_ms": chunk["offset"] / 10000,
                    "duration_ms": chunk["duration"] / 10000,
                    "text": chunk["text"]
                })
    return boundaries

def master_audio(raw_audio: str, mastered_audio: str):
    dsp_chain = (
        "highpass=f=75,"
        "equalizer=f=120:width_type=o:w=1.2:g=3.5,"
        "equalizer=f=3200:width_type=o:w=1.0:g=3.0,"
        "equalizer=f=8000:width_type=o:w=1.5:g=2.5,"
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=60:makeup=2,"
        "loudnorm=I=-14:TP=-1.0:LRA=7"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_audio,
        "-af", dsp_chain,
        "-ar", "48000", "-ac", "2",
        mastered_audio
    ], check=True)

def render_final_short(video_clips: list, audio_file: str, ass_file: str, final_output: str, duration: float):
    inputs = []
    filter_inputs = []
    for i, c in enumerate(video_clips):
        inputs.extend(["-i", c])
        filter_inputs.append(f"[{i}:v]")

    concat_filter = f"{''.join(filter_inputs)}concat=n={len(video_clips)}:v=1:a=0[vmerged]"
    escaped_ass = ass_file.replace("\\", "/").replace(":", "\\:")
    full_vfilter = f"{concat_filter};[vmerged]ass='{escaped_ass}'[vout]"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", audio_file,
        "-filter_complex", full_vfilter,
        "-map", "[vout]",
        "-map", f"{len(video_clips)}:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "24",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", str(round(duration, 2)),
        final_output
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Autonomous YouTube Shorts Generator by Ali Noor")
    parser.add_argument("--episode", type=int, default=3, help="Episode number (e.g. 3)")
    parser.add_argument("--character", type=str, default="Leo the Clockmaker", help="Protagonist character asset name")
    args = parser.parse_args()

    ep = args.episode
    print(f"\n=======================================================")
    print(f"   Generating YouTube Short: Episode {ep}")
    print(f"   Pipeline created by Ali Noor")
    print(f"=======================================================\n")

    project_name = f"Leo_Episode_{ep}"
    project_dir = OUTPUT_ROOT / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Define Episode 3 story and captions (Character: Leo, No personal name in video)
    urdu_script = (
        "پچھلی بار: وقت کے سکوت میں ایک پراسرار محافظ نے لیو پر حملہ کر دیا تھا۔ "
        "مگر جیسے ہی سیاہ عملہ قریب آیا، لیو کی جیب گھڑی سے سنہری ڈھال نکل آئی! "
        "لیو نے دیکھا کہ اس محافظ کے سینے پر بھی وہی قدیم علامت بنی تھی۔ "
        "کیا وہ محافظ دشمن تھا... یا اس گھڑی کا اصلی مالک؟ "
        "اگلا حصہ دیکھنے کے لیے سبسکرائب کریں!"
    )

    raw_audio = str(project_dir / "raw_audio.mp3")
    mastered_audio = str(project_dir / "mastered_audio.wav")
    ass_file = str(project_dir / "captions.ass")
    final_output = str(project_dir / f"Episode_{ep}_Final.mp4")

    print("[*] Generating Urdu Voiceover with Neural TTS...")
    boundaries = asyncio.run(generate_urdu_tts(urdu_script, raw_audio, rate="+10%", pitch="-2Hz"))
    print("[*] Mastering Audio with DSP chain (EQ, Compression, Loudness)...")
    master_audio(raw_audio, mastered_audio)

    # Generate ASS Subtitles
    ass_content = f"""[Script Info]
Title: Episode {ep}
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
Dialogue: 0,0:00:00.15,0:00:03.80,RecapBadge,,0,0,0,,[ PICHLI BAAR / RECAP ]
Dialogue: 0,0:00:00.15,0:00:03.80,Yellow,,0,0,0,,SHADOW GUARDIAN NE LEO PAR\\nHAMLA KAR DIYA THA...
Dialogue: 0,0:00:03.87,0:00:08.50,White,,0,0,0,,MAGAR LEO KI JAADUI GHADI SE\\nEK SONE KI DHAL NIKAL AAYI!
Dialogue: 0,0:00:08.55,0:00:13.20,Yellow,,0,0,0,,LEO NE DEKHA KE MUHAAFIZ PAR BHI\\nWOHI QADEEM NISHAN THA!
Dialogue: 0,0:00:13.25,0:00:17.50,White,,0,0,0,,KYA WOH DUSHMAN THA...\\nYA GHADI KA ASLI MAALIK?
Dialogue: 0,0:00:17.55,0:00:21.00,CTA,,0,0,0,,AGLA PART DEKHNAY KE LIYE\\nABHI SUBSCRIBE KAREIN! 🔔
"""
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_content.strip())

    print(f"\n[OK] Audio, DSP mastering, and synchronized captions prepared.")
    print(f"     Target episode output: {final_output}")
    print(f"\nTo render shots and assemble, trigger via Antigravity or Node runner!\n")

if __name__ == "__main__":
    main()
