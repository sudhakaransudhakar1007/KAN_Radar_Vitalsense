# PHASE 4: ERROR LOG & LIMITATION REGISTER

| Issue ID | Severity | Category | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ERR-P4-01** | BLOCKING | Governance Gate | Phase 2A Finalization Gate status is `OPEN`. Persistent real-data supervised model training cannot proceed without formal user gate closure. | BLOCKED |
| **ERR-P4-02** | INFORMATIONAL | Dependency Environment | PyTorch / pykan is not installed in the Windows Python 3.10 environment. A mathematically authentic, differentiable Cox-de Boor B-spline KAN layer was implemented in TensorFlow/Keras. | RESOLVED |
| **ERR-P4-03** | SCIENTIFIC | Hardware Clock | Ground truth ECG R-peak reference timestamps assume nominal $t_0 = 0$ s start time; hardware clock synchronization remains unverified. | ACKNOWLEDGED |
| **ERR-P4-04** | ARCHITECTURAL | Parameter Dimensionality | Direct connection of 3,333 radar samples to KAN would produce $>400,000$ parameters, causing catastrophic overfitting. Resolved via Conv1D feature extractor downsampling to 16 latent features. | RESOLVED |
