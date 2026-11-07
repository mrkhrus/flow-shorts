import os
import sys
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EP4_DIR = Path(r"C:\Users\hp-laptop1\flow-mcp-out\Leo_Episode_4")

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
    ], check=True)

def render_ep4():
    raw_audio = str(EP4_DIR / "raw_audio.mp3")
    mastered_audio = str(EP4_DIR / "mastered_audio.wav")
    
    # Copy ep4_paced.mp3 to raw_audio
    import shutil
    shutil.copy("ep4_paced.mp3", raw_audio)
    print("[*] Mastering audio...")
    master_audio(raw_audio, mastered_audio)

    # Subtitles
    ass_path = str(EP4_DIR / "ep4.ass")
    ass_content = """[Script Info]
Title: Leo Episode 4 - The Sky Citadel
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
Dialogue: 0,0:00:00.10,0:00:04.80,RecapBadge,,0,0,0,,[ PICHLI BAAR / RECAP ]
Dialogue: 0,0:00:00.10,0:00:04.80,Yellow,,0,0,0,,MUHAAFIZ NE ISHARA KIYA KE\\NASAL KHATRA BAADLON KE PAAR HAI...
Dialogue: 0,0:00:04.85,0:00:07.90,White,,0,0,0,,USNE LEO KO EK PUR'ASRAAR\\NSUNEHRI CHABI DI!
Dialogue: 0,0:00:07.95,0:00:11.60,Yellow,,0,0,0,,CHABI LAGTE HI, SUNEHRI ROSHNI\\NBAADLON KI TARAF LAPKI!
Dialogue: 0,0:00:11.65,0:00:15.25,White,,0,0,0,,AUR OOPAR EK TEERTA HUA\\NAZEEM QIL'A NAZAR AAYA!
Dialogue: 0,0:00:15.30,0:00:18.35,Yellow,,0,0,0,,LEO PANKH PHAILA KAR\\nUS QILAY KI TARAF URDNE LAGA!
Dialogue: 0,0:00:18.40,0:00:21.65,White,,0,0,0,,MAGAR DARWAZAY PAR EK\\nKHOUFNAAK LAAL AANKH KHUL GAYI!
Dialogue: 0,0:00:21.70,0:00:24.16,CTA,,0,0,0,,DEKHIYE AGLE HISSAY MEIN!
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content.strip())

    clips = [
        str(EP4_DIR / "recap_4s.mp4"),
        str(EP4_DIR / "scene-06.mp4"),
        str(EP4_DIR / "scene-02.mp4"),
        str(EP4_DIR / "scene-03.mp4"),
        str(EP4_DIR / "scene-04.mp4"),
        str(EP4_DIR / "scene-05.mp4"),
    ]

    out_mp4 = str(EP4_DIR / "Leo_Episode_4_Final.mp4")

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
        "-i", mastered_audio,
        "-filter_complex", full_filter,
        "-map", "[vout]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "24",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", "24.16",
        out_mp4
    ]
    print("[*] Rendering Episode 4 Final...")
    subprocess.run(cmd, check=True)
    print(f"[OK] Episode 4 Complete: {out_mp4}")

if __name__ == "__main__":
    render_ep4()
