from rtttl import RTTTL
from ptttl.audio import ptttl_to_mp3
from notemapper import create_auto_note_map

rtttl_str = "Cantina:d=4, o=5, b=250:8a, 8p, 8d6, 8p, 8a, 8p, 8d6, 8p, 8a, 8d6, 8p, 8a, 8p, 8g#, a, 8a, 8g#, 8a, g, 8f#, 8g, 8f#, f., 8d., 16p, p., 8a, 8p, 8d6, 8p, 8a, 8p, 8d6, 8p, 8a, 8d6, 8p, 8a, 8p, 8g#, 8a, 8p, 8g, 8p, g., 8f#, 8g, 8p, 8c6, a#, a, g"
song_num = 2

def generate_song_artifacts(rtttl_source: str, output_mp3: str, song_id: int = 2) -> str:
    ptttl_to_mp3(rtttl_source, output_mp3)
    lanes, times, _ = create_auto_note_map(output_mp3)

    rtttl = RTTTL(rtttl_source)

    fs, ds = zip(*[t for t in rtttl.notes()])
    fs, ds = list(fs), list(ds)

    lines = []
    melody = ",".join(str(int(f)) for f in fs) + ",0"
    lines.append(f"static const int song{song_id}_melody[]={{{melody}}};")

    t = 0
    ticks = []
    for d in ds:
        ticks.append(str(int(t)))
        t += d
    ticks.append(str(int(t)))
    lines.append(f"static const int song{song_id}_note_ticks[]={{{','.join(ticks)}}};")

    lines.append(f"static const int song{song_id}_lanes[] = {{{', '.join(map(str, lanes))}}};")
    lines.append(f"static const int song{song_id}_tickNs[] = {{{', '.join(map(str, (int(t/10) for t in times)))}}};")
    lines.append(f"static const int song{song_id}_num_notes={len(lanes)};")

    return "\n".join(lines)


if __name__ == "__main__":
    output = generate_song_artifacts(rtttl_str, "audio.mp3", song_num)
    print(output)
