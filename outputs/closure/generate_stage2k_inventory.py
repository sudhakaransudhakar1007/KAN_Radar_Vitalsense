"""Generate stage2k_file_inventory.csv for all files created in Stage 2J and 2K."""

import csv
import hashlib
from pathlib import Path


def get_h(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def main():
    # Files created in Stage 2J and 2K, plus authors_technical_validation_results.csv whose purpose is corrected
    file_purposes = {
        # Corrected file from Stage 2HI
        "outputs/closure/authors_technical_validation_results.csv": (
            "Summary comparison of technical validation statistics between independent Python replication and authors' published MATLAB results from TechValidation.m"
        ),
        # Stage 2J files
        "outputs/closure/stage2j_hashes_before.txt": "Baseline SHA-256 hashes of 154 tracked files before Stage 2J",
        "outputs/closure/stage2j_record_before_hashes.py": "Utility script recording baseline SHA-256 hashes before Stage 2J",
        "outputs/closure/run_ablation_j2.py": "Script executing 2x2 factorial ablation across all 48 recordings",
        "outputs/closure/respiratory_2x2_ablation.csv": "48-recording data table evaluating 2x2 factorial ablation cells",
        "outputs/closure/window_indexing_j3.py": "Simulation script evaluating integer hop vs round-based 23-window formula",
        "outputs/closure/update_register_j5.py": "Script updating ISS-23 evidence and recommended action per J5",
        "outputs/closure/generate_j1_table.py": "Formatting script generating 48-row J1 comparison table",
        "outputs/closure/stage2j_verify_after_hashes.py": "Verification script comparing before and after hashes for Stage 2J",
        "outputs/closure/stage2j_hashes_after.txt": "Post-stage SHA-256 hashes of 154 tracked files after Stage 2J",
        "outputs/closure/stage2h_notes.md": "Synthesis notes with range-based argument, hardware boundary, and window accounting",
        # Stage 2K files
        "outputs/closure/stage2k_record_before_hashes.py": "Utility script recording baseline SHA-256 hashes of 157 tracked files before Stage 2K",
        "outputs/closure/stage2k_hashes_before.txt": "Baseline SHA-256 hashes of 157 tracked files before Stage 2K",
        "outputs/closure/run_k1_k2.py": "Analysis script evaluating K1 provenance, VS10 in-memory test, and K2 aggregate label stats",
        "outputs/closure/run_k3_robustness.py": "Script evaluating K3 respiratory robustness, DC offset ratio, and peak flatness",
        "outputs/closure/respiratory_robustness_k3.csv": "48-recording data table of DC ratios, peak flatness ranges, and zero-lag correlations",
        "outputs/closure/run_001_status_note.md": "Governance status note classifying run_001 manifests as UNAPPROVED and SUPERSEDED",
        "outputs/closure/stage2k_file_inventory.csv": "Inventory of all files created across Stage 2J and 2K with corrected purposes",
    }

    out_csv = Path("outputs/closure/stage2k_file_inventory.csv")
    rows = []

    for path_str, purpose in file_purposes.items():
        p = Path(path_str)
        if path_str == "outputs/closure/stage2k_file_inventory.csv":
            # Placeholder for itself
            sha = "PENDING_SELF_HASH"
            sz = 0
        else:
            assert p.exists(), f"File does not exist: {p}"
            sha = get_h(p)
            sz = p.stat().st_size
        rows.append({
            "path": path_str,
            "sha256": sha,
            "size": sz,
            "purpose": purpose,
        })

    # Write initial
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "sha256", "size", "purpose"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Now update self-hash
    self_sha = get_h(out_csv)
    self_sz = out_csv.stat().st_size
    for r in rows:
        if r["path"] == "outputs/closure/stage2k_file_inventory.csv":
            r["sha256"] = self_sha
            r["size"] = self_sz

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "sha256", "size", "purpose"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Recompute final self hash
    final_sha = get_h(out_csv)
    final_sz = out_csv.stat().st_size
    for r in rows:
        if r["path"] == "outputs/closure/stage2k_file_inventory.csv":
            r["sha256"] = final_sha
            r["size"] = final_sz
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "sha256", "size", "purpose"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Generated {len(rows)} rows in {out_csv}")
    for r in rows:
        print(f"{r['path']:50s} | {r['sha256'][:16]}... | {r['size']:6d} B | {r['purpose'][:45]}...")


if __name__ == "__main__":
    main()
