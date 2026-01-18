import numpy as np
import librosa
from scipy.fft import rfft as scipy_rfft

NOTE_CONFIG = {
    'UP_MOD': 2.0,                 
    'RECOVERY_RATE': 0.05,         # Recovery relative to the auto-threshold
    'BUFFERSIZE': 2048,      
    'MIN_NOTE_GAP_MS': 250,  
    'GLOBAL_COOLDOWN_MS': 120, 
    'STREAK_LIMIT': 2,
    'TARGET_NOTES_PER_MINUTE': 80, # Adjust this to change map density
    'RNG_SEED': 42
}

def create_auto_note_map(file_path):
    audio_data, sr = librosa.load(file_path, sr=None, mono=True)
    duration_mins = len(audio_data) / sr / 60
    
    num_lanes = 3
    lane_ranges = [0.10, 0.45, 1.0] 
    buffer_size = NOTE_CONFIG['BUFFERSIZE']
    
    # --- PHASE 1: AUTO-CALIBRATION ---
    # Scan the song to find the "typical" peak for each lane
    all_peaks = [[], [], []]
    start = 0
    while start + buffer_size < len(audio_data):
        chunk = audio_data[start : start + buffer_size]
        spectrum = np.abs(scipy_rfft(chunk))
        spectrum_len = len(spectrum)
        
        lane_peaks = [0.0, 0.0, 0.0]
        for i in range(spectrum_len):
            p = i / spectrum_len
            idx = 0 if p < lane_ranges[0] else 1 if p < lane_ranges[1] else 2
            if spectrum[i] > lane_peaks[idx]:
                lane_peaks[idx] = spectrum[i]
        
        for i in range(3):
            if lane_peaks[i] > 0.1: # Ignore silence
                all_peaks[i].append(lane_peaks[i])
        start += buffer_size

    # Set base thresholds to the 75th percentile of peaks for each lane
    # This ensures Lane 2 (Treble) gets a fair threshold even if it's quiet
    auto_thresholds = [np.percentile(p, 75) if p else 10.0 for p in all_peaks]
    current_thresholds = list(auto_thresholds)
    
    # --- PHASE 2: NOTE GENERATION ---
    lane_indices = []
    timestamps_ms = []
    last_note_time = [-1000] * num_lanes 
    global_last_note_time = -1000 
    lane_history = []
    rng = np.random.default_rng(NOTE_CONFIG['RNG_SEED'])
    
    start = 3 * buffer_size 
    while start + buffer_size < len(audio_data):
        current_ms = int((start / sr) * 1000)
        chunk = audio_data[start : start + buffer_size]
        spectrum = np.abs(scipy_rfft(chunk))
        
        lane_peaks = [0.0, 0.0, 0.0]
        for i in range(len(spectrum)):
            p = i / len(spectrum)
            idx = 0 if p < lane_ranges[0] else 1 if p < lane_ranges[1] else 2
            if spectrum[i] > lane_peaks[idx]:
                lane_peaks[idx] = spectrum[i]

        best_lane = -1
        max_strength = 0

        if (current_ms - global_last_note_time) > NOTE_CONFIG['GLOBAL_COOLDOWN_MS']:
            check_order = [0, 1, 2]
            rng.shuffle(check_order)

            for l_idx in check_order:
                strength = lane_peaks[l_idx] - current_thresholds[l_idx]
                
                if strength > 0 and strength > max_strength:
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
            
            # Use UP_MOD to prevent double-hits
            current_thresholds[best_lane] *= NOTE_CONFIG['UP_MOD']

        # Recovery based on the auto-calculated base
        for l_idx in range(num_lanes):
            if current_thresholds[l_idx] > auto_thresholds[l_idx]:
                current_thresholds[l_idx] -= (auto_thresholds[l_idx] * NOTE_CONFIG['RECOVERY_RATE'])

        start += buffer_size

    return lane_indices, timestamps_ms, auto_thresholds

if __name__ == "__main__":
    lanes, times, final_thresh = create_auto_note_map("audio.mp3")
    
    # Printing results even if empty
    print(f"int lane_indices[] = {{{', '.join(map(str, lanes))}}};")
    print(f"int timestamps_ms[] = {{{', '.join(map(str, times))}}};")
    print(f"\n// AUTO-CALIBRATION RESULTS:")
    print(f"// Thresholds used: Bass={final_thresh[0]:.2f}, Mid={final_thresh[1]:.2f}, Treb={final_thresh[2]:.2f}")
    print(f"// Total Notes: {len(lanes)}")
