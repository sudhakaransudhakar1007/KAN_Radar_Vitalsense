"""Window indexing analysis: integer hop vs exact time vs ECG starts."""

import numpy as np


def main():
    rad_fs = 1000.0 / 3.0  # 333.3333333333333 Hz
    rad_samples = 40000
    win_s = 10.0
    hop_s = 5.0

    print("=== (a) Current Integer Hop 1667 (cumulative) ===")
    win_samples_a = int(round(win_s * rad_fs))  # 3333
    hop_samples_a = int(round(hop_s * rad_fs))  # 1667

    starts_a = []
    ends_a = []
    start_idx = 0
    k = 0
    while start_idx + win_samples_a <= rad_samples:
        starts_a.append(start_idx)
        ends_a.append(start_idx + win_samples_a)
        start_idx += hop_samples_a
        k += 1

    last_overflow_start = k * hop_samples_a
    last_overflow_end = last_overflow_start + win_samples_a
    tail_a = rad_samples - ends_a[-1]

    print(f"Windows per recording: {len(starts_a)}")
    print(f"Total across 48:       {len(starts_a) * 48}")
    print(f"Last valid window (idx {k-1}): start={starts_a[-1]}, end={ends_a[-1]}")
    print(f"Excluded tail:         {tail_a} samples ({tail_a/rad_fs:.4f} s)")
    print(f"Overflow window (idx {k}): start={last_overflow_start}, end={last_overflow_end} (exceeds {rad_samples} by {last_overflow_end - rad_samples} samples)")

    print("\n=== (b) Exact Formula start_k = int(round(k * 5.0 * fs)) ===")
    win_samples_b = int(round(win_s * rad_fs))  # 3333
    starts_b = []
    ends_b = []
    k = 0
    while True:
        s_k = int(round(k * hop_s * rad_fs))
        e_k = s_k + win_samples_b
        if e_k <= rad_samples:
            starts_b.append(s_k)
            ends_b.append(e_k)
            k += 1
        else:
            break

    tail_b = rad_samples - ends_b[-1]
    print(f"Windows per recording: {len(starts_b)}")
    print(f"Total across 48:       {len(starts_b) * 48}")
    print(f"Last valid window (idx {k-1}): start={starts_b[-1]}, end={ends_b[-1]}")
    print(f"Excluded tail:         {tail_b} samples ({tail_b/rad_fs:.4f} s)")

    print("\n=== (c) Exact-Time Starts on ECG at 500 Hz ===")
    ecg_fs = 500.0
    ecg_samples = 60000  # 120s * 500 Hz
    win_samples_c = int(round(win_s * ecg_fs))  # 5000
    hop_samples_c = int(round(hop_s * ecg_fs))  # 2500

    starts_c = []
    ends_c = []
    k = 0
    start_c = 0
    while start_c + win_samples_c <= ecg_samples:
        starts_c.append(start_c)
        ends_c.append(start_c + win_samples_c)
        start_c += hop_samples_c
        k += 1

    tail_c = ecg_samples - ends_c[-1]
    print(f"Windows per recording: {len(starts_c)}")
    print(f"Total across 48:       {len(starts_c) * 48}")
    print(f"Last valid window (idx {k-1}): start={starts_c[-1]}, end={ends_c[-1]}")
    print(f"Excluded tail:         {tail_c} samples ({tail_c/ecg_fs:.4f} s)")


if __name__ == "__main__":
    main()
