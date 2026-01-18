from rtttl import RTTTL
from ptttl.audio import ptttl_to_mp3
from notemapper import create_organic_note_map

rtttl_str = "Cantina:d=4, o=5, b=250:8a, 8p, 8d6, 8p, 8a, 8p, 8d6, 8p, 8a, 8d6, 8p, 8a, 8p, 8g#, a, 8a, 8g#, 8a, g, 8f#, 8g, 8f#, f., 8d., 16p, p., 8a, 8p, 8d6, 8p, 8a, 8p, 8d6, 8p, 8a, 8d6, 8p, 8a, 8p, 8g#, 8a, 8p, 8g, 8p, g., 8f#, 8g, 8p, 8c6, a#, a, g"
song_num = 2
if __name__ == "__main__":
    ptttl_to_mp3(rtttl_str, "audio.mp3")
    lanes, times = create_organic_note_map("audio.mp3")

    rtttl = RTTTL(rtttl_str)

    fs, ds = zip(*[t for t in rtttl.notes()])
    fs, ds = list(fs), list(ds)

    print(f"static const int song{song_num}_melody[]={{", end="")
    for f in fs:
        print(int(f), end=",")
    print(0, end="")
    print("}")

    print(f"static const int song{song_num}_note_ticks[]={{", end="")
    t = 0
    for d in ds:
        print(int(t), end=",")
        t += d
    print(int(t), end="")
    print("}")
    
    print(f"static const int song{song_num}_lanes[] = {{{', '.join(map(str, lanes))}}};")
    print(f"static const int song{song_num}_tickNs[] = {{{', '.join(map(str, (int(t/10) for t in times)))}}};")
    print(f"static const int song{song_num}_num_notes={len(lanes)}")
