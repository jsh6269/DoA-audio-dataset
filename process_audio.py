import os
import numpy as np
import soundfile as sf

original_audio_parent_dir = "./RawAudio"
noise_audio_path = "./drone2.wav"
output_parent_dir = "./ProcessedAudio"
sample_rate = 48000

noise, _ = sf.read(noise_audio_path)

def calculate_rms(audio):
    return np.sqrt(np.mean(audio**2))

def process(input_dir, output_dir, file_name):
    print(f"Input: {os.path.join(input_dir, file_name)}")
    original_path = os.path.join(input_dir, file_name)
    original_audio, _ = sf.read(original_path)

    if len(noise) >= len(original_audio):
        noise_start = np.random.randint(0, len(noise) - len(original_audio))
        noise_trimmed = noise[noise_start:noise_start + len(original_audio)]
    else:
        repeat_count = (len(original_audio) // len(noise)) + 1
        noise_trimmed = np.tile(noise, repeat_count)[:len(original_audio)]

    rms_original = calculate_rms(original_audio)
    rms_noise = calculate_rms(noise_trimmed)

    # Adjust noise level to achieve a desired SNR
    desired_snr_db = 0  # Desired signal-to-noise ratio in decibels
    desired_snr_linear = 10 ** (desired_snr_db / 20)

    # Scale noise to achieve desired SNR
    scaling_factor = rms_original / (desired_snr_linear * rms_noise)
    adjusted_noise = noise_trimmed * scaling_factor

    # Mix audio with adjusted noise level
    mixed_audio = original_audio + adjusted_noise
    mixed_audio = np.clip(mixed_audio, -1.0, 1.0)

    # Save the result
    output_path = os.path.join(output_dir, file_name)
    sf.write(output_path, mixed_audio, sample_rate)
    print(f"Processed and saved: {output_path}")


def process_directory(azimuth):
    input_dir = os.path.join(original_audio_parent_dir, str(azimuth))
    output_dir = os.path.join(output_parent_dir, str(azimuth))
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".wav"):
            process(input_dir, output_dir, file_name)


if __name__ == "__main__":
    azimuths = range(0, 181, 20)

    # Sequential processing for single-core execution
    for azimuth in azimuths:
        process_directory(azimuth)

    print("All audio files have been processed.")
