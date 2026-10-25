"""
Stage 6D D3: File:line reconciliation and generation of spec_gap_register_v2.csv.
Author: Antigravity Assistant (Stage 6D)
"""
import csv
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]

def main():
    # 1. Verification of Actual Lines via exact grep
    actual_lines = {
        "clean_ecg_nans (sync_val)": "src/sync_validation/ecg_processor.py:96",
        "clean_ecg_nans (phase3)": "src/phase3/ecg_reference.py:22",
        "clean_ecg_isolated_nans": "src/sync_validation/ecg_processor.py:10",
        "only_isolated parameter (sync_val)": "src/sync_validation/ecg_processor.py:98",
        "only_isolated parameter (phase3)": "src/phase3/ecg_reference.py:24",
        "fill_boundary parameter (phase3)": "src/phase3/ecg_reference.py:25",
        "fill_boundary in sync_val": "NOT_PRESENT (does not exist in src/sync_validation/ecg_processor.py)",
        "detect_r_peaks (sync_val)": "src/sync_validation/ecg_processor.py:124",
        "detect_r_peaks (phase3)": "src/phase3/ecg_reference.py:37",
        "detect_r_peaks_pan_tompkins (phase3)": "src/phase3/ecg_reference.py:168",
        "np.abs refinement line": "src/sync_validation/ecg_processor.py:203",
        "compute_ecg_sqi (sync_val)": "src/sync_validation/ecg_processor.py:273",
        "compute_ecg_sqi in phase3": "NOT_PRESENT (phase3 uses ECGReferenceValidator.validate_ecg_recording at line 264)",
        "max_rr_gap threshold (generator)": "src/phase3/supervised_dataset_generator.py:98,213",
        "coverage threshold (generator)": "src/phase3/supervised_dataset_generator.py:97,209",
        "20-beat rule (phase3)": "src/phase3/ecg_reference.py:283",
        "output_dir default 1 (runner)": "src/sync_validation/runner.py:95-96",
        "output_dir default 2 (runner)": "src/sync_validation/runner.py:244-245",
    }
    
    # Comparison Table Data
    table_rows = [
        ("clean_ecg_nans (sync_val)", "src/sync_validation/ecg_processor.py:96", "src/sync_validation/ecg_processor.py:112", "src/sync_validation/ecg_processor.py:96"),
        ("clean_ecg_isolated_nans", "src/sync_validation/ecg_processor.py:10", "Not cited directly", "src/sync_validation/ecg_processor.py:10"),
        ("only_isolated parameter", "src/sync_validation/ecg_processor.py:98", "src/sync_validation/ecg_processor.py:112", "src/sync_validation/ecg_processor.py:98 (and phase3:24)"),
        ("fill_boundary parameter", "NOT_PRESENT in ecg_processor.py", "src/sync_validation/ecg_processor.py:127 (HARDCODED)", "src/phase3/ecg_reference.py:25 (NOT in ecg_processor.py)"),
        ("detect_r_peaks", "src/sync_validation/ecg_processor.py:124", "src/sync_validation/ecg_processor.py:170", "src/sync_validation/ecg_processor.py:124 (and phase3:37)"),
        ("detect_r_peaks_pan_tompkins", "src/phase3/ecg_reference.py:168", "src/phase3/ecg_reference.py:168", "src/phase3/ecg_reference.py:168"),
        ("np.abs refinement line", "src/sync_validation/ecg_processor.py:203", "src/sync_validation/ecg_processor.py:230", "src/sync_validation/ecg_processor.py:203"),
        ("compute_ecg_sqi (sync_val)", "src/sync_validation/ecg_processor.py:273", "src/sync_validation/ecg_processor.py:290,310", "src/sync_validation/ecg_processor.py:273"),
        ("compute_ecg_sqi (phase3)", "NOT_PRESENT", "Not cited directly", "NOT_PRESENT (validate_ecg_recording:264)"),
        ("max_rr_gap threshold (generator)", "src/phase3/supervised_dataset_generator.py:98", "src/phase3/supervised_dataset_generator.py:98,213", "src/phase3/supervised_dataset_generator.py:98,213"),
        ("coverage threshold (generator)", "src/phase3/supervised_dataset_generator.py:97", "src/phase3/supervised_dataset_generator.py:209", "src/phase3/supervised_dataset_generator.py:97,209"),
        ("20-beat rule (phase3)", "src/phase3/ecg_reference.py:283", "src/phase3/ecg_reference.py:283", "src/phase3/ecg_reference.py:283"),
        ("output_dir defaults (runner)", "src/sync_validation/runner.py:95-96,244-245", "src/sync_validation/runner.py:95-96,244-245", "src/sync_validation/runner.py:95-96,244-245"),
    ]
    
    print("=== D3 Comparison Table ===")
    print(f"{'Item':<35} | {'Stage 6B Line':<35} | {'Stage 6C Line':<35} | {'Actual Line':<35}")
    print("-" * 145)
    for r in table_rows:
        print(f"{r[0]:<35} | {r[1]:<35} | {r[2]:<35} | {r[3]:<35}")
        
    # Generate spec_gap_register_v2.csv
    # Read v1 first
    v1_path = repo_root / "outputs/closure/spec_gap_register.csv"
    v2_path = repo_root / "outputs/closure/spec_gap_register_v2.csv"
    
    rows_v2 = []
    with open(v1_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = row["key"]
            loc = row["code_location"]
            stat = row["status"]
            dec = row["needs_PI_decision"]
            
            # Correct locations and statuses
            if k == "signal_processing.cleaning_function":
                loc = "src/sync_validation/ecg_processor.py:96; src/phase3/ecg_reference.py:22"
                stat = "IMPLEMENTED"
            elif k == "signal_processing.cleaning_options.only_isolated":
                loc = "src/sync_validation/ecg_processor.py:98; src/phase3/ecg_reference.py:24"
                stat = "IMPLEMENTED"
            elif k == "signal_processing.cleaning_options.fill_boundary":
                loc = "src/phase3/ecg_reference.py:25 (NOT in ecg_processor.py)"
                stat = "IMPLEMENTED_IN_PHASE3_WRAPPER"
            elif k == "signal_processing.detector_function":
                loc = "src/sync_validation/ecg_processor.py:124; src/phase3/ecg_reference.py:37"
                stat = "IMPLEMENTED"
            elif k == "signal_processing.detector_refinement":
                loc = "src/sync_validation/ecg_processor.py:203"
                stat = "IMPLEMENTED"
            elif k == "recording_level_sqi.min_coverage_ratio":
                loc = "src/sync_validation/ecg_processor.py:276,297-298"
                stat = "IMPLEMENTED"
            elif k == "recording_level_sqi.max_rr_gap_s":
                loc = "src/sync_validation/ecg_processor.py:290,297-298"
                stat = "IMPLEMENTED"
            elif k == "recording_level_sqi.amplitude_stability":
                loc = "src/sync_validation/ecg_processor.py:298,342"
                stat = "IMPLEMENTED"
            elif k == "recording_level_sqi.verdict_rule":
                loc = "src/sync_validation/ecg_processor.py:298,342"
                stat = "IMPLEMENTED"
            elif k == "window_quality_gating.max_rr_gap_threshold_s":
                loc = "src/phase3/supervised_dataset_generator.py:98,213"
                stat = "UNDECIDED_EXTRA_RULE"
                dec = "Y"
            elif k == "recording_sqi.min_valid_beats_20":
                loc = "src/phase3/ecg_reference.py:283"
                stat = "UNDECIDED_EXTRA_RULE"
                dec = "Y"
                
            rows_v2.append({
                "key": k,
                "spec_value": row["spec_value"],
                "code_location": loc,
                "status": stat,
                "needs_PI_decision": dec
            })
            
    with open(v2_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "spec_value", "code_location", "status", "needs_PI_decision"])
        writer.writeheader()
        writer.writerows(rows_v2)
        
    print(f"\nWritten {len(rows_v2)} rows to {v2_path}")

if __name__ == "__main__":
    main()
