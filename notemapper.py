import numpy as np
import librosa
from scipy.fft import rfft as scipy_rfft

NOTE_CONFIG = {
    # 1. PEAK SENSITIVITY: Lower these if you still get too few notes
    # Lane 0 (Bass), Lane 1 (Mid), Lane 2 (Treble)
    'THRESHOLD': [8.0, 6.0, 4.0],  
    
    # 2. AGGRESSIVE RECOVERY: Threshold drops by 0.5 every 46ms
    # This ensures the 'gate' re-opens quickly for the next beat.
    'RECOVERY': [0.5, 0.4, 0.6],   
    
    'UP_MOD': 1.6,                 # How much the gate 'slams shut' after a hit
    'MAX_LIMIT': 150,            
    'BUFFERSIZE': 2048,      
    'MIN_NOTE_GAP_MS': 200,        # Allows for faster 16th note rhythms
    'GLOBAL_COOLDOWN_MS': 100, 
    'STREAK_LIMIT': 2,             
    'RNG_SEED': 42
}

def create_organic_note_map(file_path):
    audio_data, sr = librosa.load(file_path, sr=None, mono=True)
    
    num_lanes = 3
    lane_ranges = [0.10, 0.45, 1.0] 
    current_thresholds = list(NOTE_CONFIG['THRESHOLD'])
    buffer_size = NOTE_CONFIG['BUFFERSIZE']
    rng = np.random.default_rng(NOTE_CONFIG['RNG_SEED'])
    
    lane_indices = []
    timestamps_ms = []
    last_note_time = [-1000] * num_lanes 
    global_last_note_time = -1000 
    lane_history = []
    
    start = 3 * buffer_size 
    
    while start + buffer_size < len(audio_data):
        current_ms = int((start / sr) * 1000)
        chunk = audio_data[start : start + buffer_size]
        spectrum = np.abs(scipy_rfft(chunk))
        spectrum_len = len(spectrum)
        
        # FIND PEAKS: Use the MAX value in the band, not the average.
        # This catches sharp transients (drums/plucks).
        lane_peaks = [0.0, 0.0, 0.0]
        for i in range(spectrum_len):
            p = i / spectrum_len
            idx = 0 if p < lane_ranges[0] else 1 if p < lane_ranges[1] else 2
            if spectrum[i] > lane_peaks[idx]:
                lane_peaks[idx] = spectrum[i]

        best_lane = -1
        max_strength = 0

        if (current_ms - global_last_note_time) > NOTE_CONFIG['GLOBAL_COOLDOWN_MS']:
            check_order = [0, 1, 2]
            rng.shuffle(check_order)

            for l_idx in check_order:
                # Signal strength is Peak Magnitude minus current Threshold
                strength = lane_peaks[l_idx] - current_thresholds[l_idx]
                
                if strength > 0 and strength > max_strength:
                    # Prevent 3-in-a-row of the same lane
                    if len(lane_history) >= NOTE_CONFIG['STREAK_LIMIT']:
                        if all(x == l_idx for x in lane_history[-NOTE_CONFIG['STREAK_LIMIT']:]):
                            continue 
                    
                    if (current_ms - last_note_time[l_idx]) > NOTE_CONFIG['MIN_NOTE_GAP_MS']:
                        max_strength = strength
                        best_lane = l_idx

        if best_lane != -1:
            lane_indices.append(best_lane)
            timestamps_ms.append(current_ms)
            lane_history.append(best_lane)
            
            last_note_time[best_lane] = current_ms
            global_last_note_time = current_ms
            
            # Raise the bar for the next note in this lane
            current_thresholds[best_lane] *= NOTE_CONFIG['UP_MOD']
            if current_thresholds[best_lane] > NOTE_CONFIG['MAX_LIMIT']:
                current_thresholds[best_lane] = NOTE_CONFIG['MAX_LIMIT']

        # Rapidly recover thresholds so we don't miss the next beat
        for l_idx in range(num_lanes):
            if current_thresholds[l_idx] > NOTE_CONFIG['THRESHOLD'][l_idx]:
                current_thresholds[l_idx] -= NOTE_CONFIG['RECOVERY'][l_idx]

        start += buffer_size

    return lane_indices, timestamps_ms

if __name__ == "__main__":
    lanes, times = create_organic_note_map("audio.mp3")
    print(f"int lane_indices[] = {{{', '.join(map(str, lanes))}}};")
    print(f"int timestamps_ms[] = {{{', '.join(map(str, times))}}};")
    print(f"// Total Notes: {len(lanes)}")
