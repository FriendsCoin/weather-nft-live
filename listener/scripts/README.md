# Scripts Directory Organization

This directory contains scripts for both **NESCIENCE** (contemplative art) and **legacy wellness** workflows.

## 🎨 NESCIENCE Scripts (Recommended)

**Philosophy:** Witnessing consciousness without judgment. Not wellness optimization.

### Primary Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `nescience_session.py` | Real-time meditation session | `python scripts/nescience_session.py --mock --duration 600` |
| `calibrate_baseline.py` | Personal EEG calibration | `python scripts/calibrate_baseline.py --mock --duration 600` |
| `autonomous_meditation.py` | Companion meditates alone (gallery mode) | `python scripts/autonomous_meditation.py --touchdesigner localhost:9000` |
| `visualize_character.py` | Character evolution visualization | `python scripts/visualize_character.py` |
| `test_osc.py` | Test Mind Monitor/TouchDesigner connections | `python scripts/test_osc.py --receive` |

### NESCIENCE Workflow

```bash
# 1. Setup
python scripts/setup.py

# 2. First session (mock)
python scripts/nescience_session.py --mock --duration 600

# 3. Calibrate (optional but recommended)
python scripts/calibrate_baseline.py --duration 600

# 4. Regular sessions
python scripts/nescience_session.py --duration 1200

# 5. Visualize companion evolution
python scripts/visualize_character.py

# 6. When fully awakened (60+ sessions)
python scripts/autonomous_meditation.py
```

**Or use the unified dashboard:**
```bash
python start_dashboard.py
# Open: http://localhost:8080
```

---

## ⚕️ Legacy Wellness Scripts

**Philosophy:** Alpha+/Beta- optimization, performance metrics, neurofeedback training.

### Legacy Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `realtime_feedback.py` | Wellness neurofeedback (alpha+/beta-) | Legacy wellness approach |
| `analyze_meditation.py` | Meditation quality analysis | Statistical wellness metrics |
| `train.py` | Train VAE model | VAE-based memory generation |
| `generate_memories.py` | Generate VAE memories | After VAE training |
| `generate_multimedia.py` | Full multimedia memories | Gallery-ready outputs |
| `optimize_hyperparameters.py` | Hyperparameter tuning | Before VAE training |

### Legacy Workflow

```bash
# 1. Generate or collect data
python scripts/generate_mock_data.py

# 2. Train VAE
python scripts/train.py --epochs 100

# 3. Generate memories
python scripts/generate_memories.py

# 4. Create multimedia
python scripts/generate_multimedia.py
```

---

## 🛠️ Utility Scripts

| Script | Purpose |
|--------|---------|
| `setup.py` | Interactive setup wizard |
| `test_gpu_setup.py` | Verify GPU configuration |
| `generate_mock_data.py` | Generate test EEG data |
| `visualize.py` | Visualize VAE latent space |

---

## 🔀 Key Differences: NESCIENCE vs Legacy

### Philosophy

| Aspect | NESCIENCE | Legacy Wellness |
|--------|-----------|-----------------|
| Goal | Witnessing without judgment | Optimization & performance |
| States | SETTLING, FLOW, DEEP, LIMINAL, PRESENT | alpha+/-, beta+/-, combined, drowsy |
| Feedback | Poetic interpretation (anicca) | Success/fail audio cues |
| Character | Tsukumogami awakening over 60-100 sessions | No character system |
| Output | Contemplative art installation | Personal training tool |

### Technical

| Aspect | NESCIENCE | Legacy Wellness |
|--------|-----------|-----------------|
| Real-time | `nescience_session.py` | `realtime_feedback.py` |
| Analysis | Character evolution, phenomenology | Statistical metrics, performance ratios |
| Hardware | Muse S + Mind Monitor (OSC) | Generic EEG devices |
| Visuals | TouchDesigner + LED mask | Terminal-based feedback |
| Training | No training needed (rule-based) | VAE training required |

---

## 📋 Duplication Notes

Some functionality is duplicated between NESCIENCE and legacy scripts:

1. **Real-time sessions:**
   - `nescience_session.py` (NESCIENCE, recommended)
   - `realtime_feedback.py` (Legacy wellness)

2. **Analysis:**
   - `visualize_character.py` (NESCIENCE character evolution)
   - `analyze_meditation.py` (Legacy statistical analysis)

3. **Data generation:**
   - Both use mock EEG data for testing
   - NESCIENCE has built-in mock mode in session scripts
   - Legacy uses separate `generate_mock_data.py`

### Why Not Merged?

The philosophies are fundamentally different:
- **NESCIENCE** critiques wellness optimization culture
- **Legacy** embodies wellness optimization culture

Merging would dilute the conceptual clarity of NESCIENCE as an art piece.

---

## 🎯 Recommendation

**For new users:** Start with NESCIENCE workflow (it's the main project)

**For researchers:** Legacy scripts provide statistical wellness analysis

**For artists:** NESCIENCE + TouchDesigner integration for installations

---

## 🚀 Quick Start

### NESCIENCE (Recommended)
```bash
# Dashboard (easiest)
python start_dashboard.py

# CLI
python scripts/nescience_session.py --mock --duration 600
```

### Legacy Wellness
```bash
python scripts/realtime_feedback.py --duration 300
python scripts/analyze_meditation.py --sessions-dir data/sessions
```
