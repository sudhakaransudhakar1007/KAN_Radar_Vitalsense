"""
R5 Script: Generate outputs/closure/spec_gap_register.csv.
Author: Antigravity Assistant (Stage 6C)
"""
import json
import csv
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]

def main():
    spec_path = repo_root / "outputs/closure/spec/label_spec_v1.json"
    assert spec_path.exists(), f"Missing spec: {spec_path}"
    
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
        
    rows = []
    
    # Define mapping of all keys to code location and status
    entries = [
        ("spec_version", spec["spec_version"], "src/phase3/supervised_dataset_generator.py:101", "IMPLEMENTED", "N"),
        ("created_at", spec["created_at"], "outputs/closure/spec/label_spec_v1.json:3", "IMPLEMENTED", "N"),
        ("approved_by", spec["approved_by"], "outputs/closure/spec/label_spec_v1.json:4", "IMPLEMENTED", "N"),
        ("governance.decision_file", spec["governance"]["decision_file"], "src/phase3/supervised_dataset_generator.py:106-135", "IMPLEMENTED", "N"),
        ("governance.status", spec["governance"]["status"], "outputs/closure/spec/label_spec_v1.json:7", "IMPLEMENTED", "N"),
        ("governance.hardware_timing_limitation", spec["governance"]["hardware_timing_limitation"], "src/phase3/supervised_dataset_generator.py:255", "HARDCODED", "N"),
        ("governance.threshold_provenance", spec["governance"]["threshold_provenance"], "outputs/closure/spec/label_spec_v1.json:9", "IMPLEMENTED", "N"),
        ("governance.prespecified_before_training", str(spec["governance"]["prespecified_before_training"]), "outputs/closure/spec/label_spec_v1.json:10", "IMPLEMENTED", "N"),
        
        ("windowing.window_duration_seconds", str(spec["windowing"]["window_duration_seconds"]), "src/phase3/supervised_dataset_generator.py:65", "IMPLEMENTED", "N"),
        ("windowing.hop_duration_seconds", str(spec["windowing"]["hop_duration_seconds"]), "src/phase3/supervised_dataset_generator.py:66", "IMPLEMENTED", "N"),
        ("windowing.num_windows", str(spec["windowing"]["num_windows"]), "src/phase3/supervised_dataset_generator.py:67", "IMPLEMENTED", "N"),
        ("windowing.radar_sample_start_formula", spec["windowing"]["radar_sample_start_formula"], "src/phase3/supervised_dataset_generator.py:270", "IMPLEMENTED", "N"),
        ("windowing.radar_sample_end_formula", spec["windowing"]["radar_sample_end_formula"], "src/phase3/supervised_dataset_generator.py:271", "IMPLEMENTED", "N"),
        ("windowing.ecg_time_start_formula", spec["windowing"]["ecg_time_start_formula"], "src/phase3/supervised_dataset_generator.py:274", "IMPLEMENTED", "N"),
        ("windowing.ecg_time_end_formula", spec["windowing"]["ecg_time_end_formula"], "src/phase3/supervised_dataset_generator.py:275", "IMPLEMENTED", "N"),
        ("windowing.ecg_sample_start_formula", spec["windowing"]["ecg_sample_start_formula"], "src/phase3/supervised_dataset_generator.py:276", "IMPLEMENTED", "N"),
        ("windowing.ecg_sample_end_formula", spec["windowing"]["ecg_sample_end_formula"], "src/phase3/supervised_dataset_generator.py:277", "IMPLEMENTED", "N"),
        
        ("reference_source.lead", spec["reference_source"]["lead"], "src/phase3/supervised_dataset_generator.py:255", "HARDCODED", "N"),
        ("reference_source.label_source", spec["reference_source"]["label_source"], "src/phase3/supervised_dataset_generator.py:255-265", "IMPLEMENTED", "N"),
        ("reference_source.monitor_hr_allowed", str(spec["reference_source"]["monitor_hr_allowed"]), "src/phase3/supervised_dataset_generator.py:48-52", "IMPLEMENTED", "N"),
        ("reference_source.monitor_hr_status", spec["reference_source"]["monitor_hr_status"], "src/phase3/supervised_dataset_generator.py:52", "IMPLEMENTED", "N"),
        
        ("signal_processing.cleaning_module", spec["signal_processing"]["cleaning_module"], "src/phase3/ecg_reference.py:16", "WRAPPER_ONLY", "N"),
        ("signal_processing.cleaning_function", spec["signal_processing"]["cleaning_function"], "src/sync_validation/ecg_processor.py:112", "IMPLEMENTED", "N"),
        ("signal_processing.cleaning_options.only_isolated", str(spec["signal_processing"]["cleaning_options"]["only_isolated"]), "src/sync_validation/ecg_processor.py:112", "HARDCODED", "N"),
        ("signal_processing.cleaning_options.fill_boundary", str(spec["signal_processing"]["cleaning_options"]["fill_boundary"]), "src/sync_validation/ecg_processor.py:127", "HARDCODED", "N"),
        ("signal_processing.detector_module", spec["signal_processing"]["detector_module"], "src/phase3/ecg_reference.py:16", "WRAPPER_ONLY", "N"),
        ("signal_processing.detector_function", spec["signal_processing"]["detector_function"], "src/sync_validation/ecg_processor.py:170", "IMPLEMENTED", "N"),
        ("signal_processing.detector_refinement", spec["signal_processing"]["detector_refinement"], "src/sync_validation/ecg_processor.py:230", "IMPLEMENTED", "N"),
        ("signal_processing.fs_radar_nominal", str(spec["signal_processing"]["fs_radar_nominal"]), "src/phase3/supervised_dataset_generator.py:60", "IMPLEMENTED", "N"),
        ("signal_processing.fs_ecg_nominal", str(spec["signal_processing"]["fs_ecg_nominal"]), "src/phase3/supervised_dataset_generator.py:61", "IMPLEMENTED", "N"),
        
        ("label_definition.hr_formula", spec["label_definition"]["hr_formula"], "src/phase3/supervised_dataset_generator.py:216", "IMPLEMENTED", "N"),
        ("label_definition.hr_type", spec["label_definition"]["hr_type"], "src/phase3/supervised_dataset_generator.py:217", "IMPLEMENTED", "N"),
        ("label_definition.interval_assignment_rule", spec["label_definition"]["interval_assignment_rule"], "src/phase3/supervised_dataset_generator.py:190-194", "IMPLEMENTED", "N"),
        ("label_definition.interval_assignment_formula", spec["label_definition"]["interval_assignment_formula"], "src/phase3/supervised_dataset_generator.py:190-194", "IMPLEMENTED", "N"),
        ("label_definition.min_phys_bpm", str(spec["label_definition"]["min_phys_bpm"]), "src/phase3/supervised_dataset_generator.py:93", "IMPLEMENTED", "N"),
        ("label_definition.max_phys_bpm", str(spec["label_definition"]["max_phys_bpm"]), "src/phase3/supervised_dataset_generator.py:94", "IMPLEMENTED", "N"),
        ("label_definition.min_phys_rr_s", str(spec["label_definition"]["min_phys_rr_s"]), "src/phase3/supervised_dataset_generator.py:95", "IMPLEMENTED", "N"),
        ("label_definition.max_phys_rr_s", str(spec["label_definition"]["max_phys_rr_s"]), "src/phase3/supervised_dataset_generator.py:96", "IMPLEMENTED", "N"),
        
        ("window_quality_gating.outlier_rule", spec["window_quality_gating"]["outlier_rule"], "src/phase3/supervised_dataset_generator.py:200-202", "IMPLEMENTED", "N"),
        ("window_quality_gating.min_covered_duration_s", str(spec["window_quality_gating"]["min_covered_duration_s"]), "src/phase3/supervised_dataset_generator.py:209", "IMPLEMENTED", "N"),
        ("window_quality_gating.coverage_rule", spec["window_quality_gating"]["coverage_rule"], "src/phase3/supervised_dataset_generator.py:209", "IMPLEMENTED", "N"),
        ("window_quality_gating.max_rr_gap_threshold_s", str(spec["window_quality_gating"]["max_rr_gap_threshold_s"]), "src/phase3/supervised_dataset_generator.py:98,213", "UNDECIDED_EXTRA_RULE", "Y"),
        
        ("recording_level_sqi.min_coverage_ratio", str(spec["recording_level_sqi"]["min_coverage_ratio"]), "src/sync_validation/ecg_processor.py:290", "IMPLEMENTED", "N"),
        ("recording_level_sqi.max_rr_gap_s", str(spec["recording_level_sqi"]["max_rr_gap_s"]), "src/sync_validation/ecg_processor.py:295", "IMPLEMENTED", "N"),
        ("recording_level_sqi.amplitude_stability", spec["recording_level_sqi"]["amplitude_stability"], "src/sync_validation/ecg_processor.py:305", "IMPLEMENTED", "N"),
        ("recording_level_sqi.verdict_rule", spec["recording_level_sqi"]["verdict_rule"], "src/sync_validation/ecg_processor.py:310", "IMPLEMENTED", "N"),
        
        ("seed_policy.cardiac_surrogate_seed", str(spec["seed_policy"]["cardiac_surrogate_seed"]), "src/sync_validation/cardiac_radar_validator.py:165", "IMPLEMENTED", "N"),
        ("seed_policy.rng_implementation", spec["seed_policy"]["rng_implementation"], "src/sync_validation/cardiac_radar_validator.py:166", "IMPLEMENTED", "N"),
        ("spec_sha256", spec["spec_sha256"], "src/phase3/supervised_dataset_generator.py:100-135", "IMPLEMENTED", "N"),
        
        # Undecided extra rules not in spec but in src:
        ("recording_sqi.min_valid_beats_20", "20 beats", "src/phase3/ecg_reference.py:283", "UNDECIDED_EXTRA_RULE", "Y"),
    ]
    
    out_csv = repo_root / "outputs/closure/spec_gap_register.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "spec_value", "code_location", "status", "needs_PI_decision"])
        for r in entries:
            writer.writerow(r)
            
    print(f"Generated {out_csv} with {len(entries)} rows.")

if __name__ == "__main__":
    main()
