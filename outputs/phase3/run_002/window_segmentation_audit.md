# Phase 3 Window Segmentation Audit Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_002`  
**Execution Date:** October 15, 2026  
**Status:** `VERIFIED_DIAGNOSTIC_ONLY`  

---

## 1. Sliding Window Parameters & Mathematical Definition

The Phase 3 sliding-window segmentation architecture divides continuous 120-second radar recordings into uniform candidate windows for temporal analysis:
- **Sampling Frequency ($f_s$):** $333.3333\text{ Hz}$ ($40,000\text{ samples} / 120.000\text{ s}$).
- **Nominal Window Duration ($W_s$):** $10.0\text{ seconds}$.
- **Window Length in Samples ($L$):**
  $$L = \text{round}(W_s \times f_s) = \text{round}(10.0 \times 333.3333) = 3333\text{ samples}$$
- **Nominal Hop Duration ($H_s$):** $5.0\text{ seconds}$ (50% overlap).
- **Hop Size in Samples ($H$):**
  $$H = \text{round}(H_s \times f_s) = \text{round}(5.0 \times 333.3333) = 1667\text{ samples}$$

---

## 2. Sample Indexing & Window Count Investigation

For any discrete recording of length $N = 40,000\text{ samples}$, a complete window $k$ (starting at sample index $s_k = k \times H$) is valid if and only if:
$$s_k + L \le N$$

Evaluating this condition sequentially:

| Window Index ($k$) | Sample Start ($s_k$) | Sample End ($s_k + L$) | Nominal Start Time | Nominal End Time | Complete? |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 0 | 3333 | 0.0 s | 10.0 s | Yes |
| **1** | 1667 | 5000 | 5.0 s | 15.0 s | Yes |
| **2** | 3334 | 6667 | 10.0 s | 20.0 s | Yes |
| **3** | 5001 | 8334 | 15.0 s | 25.0 s | Yes |
| **4** | 6668 | 10001 | 20.0 s | 30.0 s | Yes |
| **5** | 8335 | 11668 | 25.0 s | 35.0 s | Yes |
| **...** | ... | ... | ... | ... | ... |
| **19** | 31673 | 35006 | 95.0 s | 105.0 s | Yes |
| **20** | 33340 | 36673 | 100.0 s | 110.0 s | Yes |
| **21** | 35007 | 38340 | 105.0 s | 115.0 s | Yes |
| *Candidate 22* | *36674* | *40007* | *110.0 s* | *120.0 s* | **No (40007 > 40000)** |

### Trailing Tail Accounting:
- **Last Processed Sample Index:** 38,340.
- **Excluded Trailing Samples:**
  $$N_{\text{tail}} = 40,000 - 38,340 = 1660\text{ samples}$$
- **Excluded Trailing Duration:**
  $$T_{\text{tail}} = \frac{1660}{333.3333\text{ Hz}} = 4.9800\text{ seconds}$$

---

## 3. Findings & Governance Enforcements

1. **Exact Complete Window Count:**
   - Exactly **22 complete windows** fit within each 120-second recording without silent zero-padding or length distortion.
   - Across the 48 recordings in the dataset, there are exactly:
     $$22 \times 48 = 1056\text{ candidate windows}$$
2. **Prohibition of Silent Padding:**
   - Candidate window 22 requires 7 additional samples beyond the end of the recording ($40,007 > 40,000$).
   - Silent zero-padding or periodic reflection to force a 23rd window is **strictly prohibited**, preserving authentic physical signal boundaries.
3. **Supervised Window Dataset Stop Condition:**
   - `WindowGenerator.execute_supervised_generation()` raises `LabelGenerationBlockedError`.
   - **No persistent window dataset arrays or supervised training labels were extracted or saved**, as the Phase 2A Finalization Gate remains open.
