# NESCIENCE Architecture & Code Organization

## Directory Structure

```
listener/
├── src/                          # Core libraries (importable modules)
│   ├── nescience/               # NESCIENCE core systems
│   │   ├── meditation_states.py       # 5 phenomenological states
│   │   ├── character_evolution.py     # Tsukumogami awakening
│   │   └── poetic_interpreter.py      # Anicca-based descriptions
│   │
│   ├── integrations/            # Hardware integrations
│   │   └── osc_bridge.py              # Mind Monitor, TouchDesigner, LED
│   │
│   ├── realtime/                # Legacy wellness neurofeedback
│   │   ├── neurofeedback.py           # Alpha+/beta- states
│   │   └── feedback_cues.py           # Audio/visual feedback
│   │
│   ├── web/                     # Web dashboard
│   │   ├── nescience_server.py        # Unified dashboard hub
│   │   ├── server.py                  # Legacy dashboard
│   │   └── templates/
│   │       └── nescience_hub.html     # Main UI
│   │
│   ├── models/                  # ML models (VAE)
│   ├── data/                    # Data processing
│   └── utils/                   # Shared utilities
│       ├── session_utils.py           # Session helpers
│       ├── caching.py                 # Performance caching
│       └── error_handling.py          # Error management
│
├── scripts/                     # Executable scripts
│   ├── nescience_session.py           # NESCIENCE session (MAIN)
│   ├── autonomous_meditation.py       # Gallery mode
│   ├── calibrate_baseline.py          # EEG calibration
│   ├── visualize_character.py         # Character evolution
│   ├── test_osc.py                    # OSC testing
│   │
│   ├── realtime_feedback.py           # Legacy wellness session
│   ├── analyze_meditation.py          # Legacy analysis
│   ├── train.py                       # VAE training
│   ├── generate_memories.py           # VAE memories
│   └── generate_multimedia.py         # Multimedia output
│
├── start_dashboard.py           # Dashboard launcher (RECOMMENDED ENTRY POINT)
├── data/                        # Runtime data
│   ├── character_state.json           # Companion state
│   ├── baseline_profile.json          # Personal EEG thresholds
│   └── sessions/                      # Session history
│
└── docs/                        # Documentation
    ├── NESCIENCE.md                   # Main concept doc
    ├── QUICKSTART_NESCIENCE.md        # Getting started
    ├── TOUCHDESIGNER_SETUP.md         # Visual integration
    └── scripts/README.md              # Scripts guide
```

---

## Code Organization Principles

### 1. **Clear Separation: NESCIENCE vs Legacy**

**NESCIENCE** (Contemplative Art):
- Philosophy: Witnessing consciousness without judgment
- Scripts: `nescience_session.py`, `autonomous_meditation.py`, `visualize_character.py`
- Modules: `src/nescience/*`, `src/integrations/osc_bridge.py`
- States: SETTLING, FLOW, DEEP, LIMINAL, PRESENT
- Output: Poetic interpretations, character evolution

**Legacy Wellness** (Neurofeedback Training):
- Philosophy: Alpha+/beta- optimization for performance
- Scripts: `realtime_feedback.py`, `analyze_meditation.py`, `train.py`
- Modules: `src/realtime/*`, `src/models/*`
- States: alpha+/-, beta+/-, combined, drowsy
- Output: Performance metrics, VAE memories

**Why kept separate:** Philosophical differences are fundamental. NESCIENCE critiques the wellness optimization culture that Legacy embodies.

### 2. **Shared Utilities** (`src/utils/`)

Common functionality extracted to reduce duplication:

- **session_utils.py** - Character loading, OSC setup, mock data, formatting
- **caching.py** - Performance optimization
- **error_handling.py** - Consistent error messages

### 3. **Scripts as Entry Points**

All scripts in `scripts/` are standalone executables:
- Each has `if __name__ == "__main__"`
- Each does `sys.path.insert(0, ...)` for imports
- Each can run independently
- Each has comprehensive `--help`

**Design choice:** Self-contained scripts > brittle import dependencies

---

## Code Duplication Analysis

### ✅ Acceptable Duplication

1. **`sys.path.insert(0, ...)` in every script**
   - **Why:** Makes each script self-contained
   - **Benefit:** Can run any script from any directory
   - **Cost:** 1 line per file (minimal)
   - **Verdict:** Keep as-is

2. **argparse setup in every script**
   - **Why:** Each script has unique arguments
   - **Benefit:** Clear `--help` per script
   - **Cost:** 10-30 lines per file
   - **Verdict:** Keep as-is (standard pattern)

3. **Similar concepts, different implementations**
   - `realtime_feedback.py` vs `nescience_session.py`
   - Both do real-time sessions, but for different philosophies
   - **Verdict:** Keep separate (conceptual clarity)

### ⚠️ Addressable Duplication

1. **Mock EEG data generation** ✅ **FIXED**
   - Was duplicated in `nescience_session.py`, `calibrate_baseline.py`, etc.
   - Now centralized in `src/utils/session_utils.py::generate_mock_eeg_sample()`

2. **Character loading** ✅ **FIXED**
   - Was duplicated in multiple scripts
   - Now centralized in `src/utils/session_utils.py::load_character()`

3. **OSC receiver setup** ✅ **FIXED**
   - Was duplicated across OSC scripts
   - Now centralized in `src/utils/session_utils.py::setup_osc_receiver()`

4. **Matplotlib dark theme setup**
   - Currently duplicated in `analyze_meditation.py` and `visualize_character.py`
   - Could extract to `src/utils/plotting_utils.py`
   - **Priority:** Low (only 2 files)

---

## Recommended Entry Points

### For Users

**Web Dashboard (Easiest):**
```bash
python start_dashboard.py
# → http://localhost:8080
```

**CLI (Power Users):**
```bash
# NESCIENCE session
python scripts/nescience_session.py --mock --duration 600

# Character evolution
python scripts/visualize_character.py
```

### For Developers

**Importing modules:**
```python
from nescience.character_evolution import CharacterEvolution
from integrations.osc_bridge import MindMonitorReceiver
from utils.session_utils import load_character, generate_mock_eeg_sample
```

**Adding new features:**
1. Core logic → `src/nescience/` or `src/integrations/`
2. Executable → `scripts/`
3. Utilities → `src/utils/`
4. Documentation → `docs/`

---

## Import Patterns

### Scripts (Executable)
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nescience.character_evolution import CharacterEvolution
from utils.session_utils import load_character
```

### Modules (Library Code)
```python
# No sys.path manipulation!
# Assumes proper PYTHONPATH or installed package

from nescience.meditation_states import MeditationState
from integrations.osc_bridge import TouchDesignerSender
```

### Web Server
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nescience.character_evolution import CharacterEvolution
```

---

## Testing Strategy

### Unit Tests (Future)
```
tests/
├── test_meditation_states.py
├── test_character_evolution.py
├── test_osc_bridge.py
└── test_poetic_interpreter.py
```

### Integration Tests
```bash
# Mock session (no hardware)
python scripts/nescience_session.py --mock --duration 60

# OSC loopback test
python scripts/test_osc.py --receive &
python scripts/test_osc.py --send
```

### Manual Testing
```bash
# Dashboard end-to-end
python start_dashboard.py
# → Test all features via UI
```

---

## Performance Considerations

### Caching (`src/utils/caching.py`)
- Session-level caching for EEG processing
- Model-level caching for VAE inference
- TTL-based invalidation

### Memory Management
- Stream large sessions (don't load all in RAM)
- Use generators for data processing
- Clear matplotlib figures after saving

### Real-time Latency
- Target: <1 second EEG → feedback
- OSC @ 10-12 Hz (Muse S standard)
- Minimal processing in hot path

---

## Dependency Management

### Core Dependencies
```
numpy, scipy          # Numerical computing
torch                 # VAE models (legacy)
python-osc            # OSC protocol
flask, flask-socketio # Web dashboard
matplotlib            # Visualization
```

### Optional Dependencies
```
tensorboard           # Training monitoring
optuna                # Hyperparameter optimization
pytorch-lightning     # Training framework
```

### Hardware Integrations
```
Mind Monitor app      # Muse S → OSC
TouchDesigner         # OSC → Visuals
Arduino/ESP32         # LED mask control
```

---

## Future Refactoring Opportunities

### Low Priority
1. Extract matplotlib theme to `utils/plotting_utils.py`
2. Create base class for session scripts (if more added)
3. Type hints throughout codebase
4. Proper test suite

### Medium Priority
1. Session data format standardization (currently mix of .pkl, .json, .h5)
2. Unified config file (currently scattered)
3. Plugin system for new meditation states

### High Priority (If Scaling)
1. Database for session history (currently JSON files)
2. Multi-user support
3. API for external integrations

---

## Contributing Guidelines

### Adding New Features

1. **Character trait:** → `src/nescience/character_evolution.py`
2. **Meditation state:** → `src/nescience/meditation_states.py`
3. **OSC integration:** → `src/integrations/osc_bridge.py`
4. **Script:** → `scripts/` + update `scripts/README.md`
5. **Dashboard feature:** → `src/web/nescience_server.py`

### Code Style
- Use type hints where practical
- Docstrings for all public functions
- Comments explain "why", not "what"
- Keep scripts self-contained

### Commit Messages
```
Add autonomous meditation mode for COMPANIONSHIP phase

- Companion meditates alone when fully awakened
- Generates states based on personality traits
- Useful for gallery installations
```

---

## Questions & Decisions

### Q: Why not merge NESCIENCE and Legacy code?
**A:** Philosophical differences are fundamental. NESCIENCE critiques wellness optimization; Legacy embodies it. Merging would dilute the art concept.

### Q: Why duplicate real-time session logic?
**A:** `nescience_session.py` and `realtime_feedback.py` serve different audiences with different mental models. Shared abstraction would confuse both.

### Q: Why `sys.path.insert` instead of proper packaging?
**A:** Scripts are meant to be run directly from repo. No `pip install` required. Lowers barrier to entry for artists/non-developers.

### Q: Why JSON for character state instead of database?
**A:** Single-user system. JSON is human-readable and version-controllable. Easy to backup and transfer.

### Q: When to use dashboard vs CLI?
**A:** Dashboard for ease-of-use and monitoring. CLI for advanced users, scripting, and integrations.

---

## Summary

**Well-organized duplication < poorly-abstracted shared code**

Current architecture prioritizes:
1. ✅ Conceptual clarity (NESCIENCE vs Legacy separation)
2. ✅ Self-contained scripts (sys.path patterns)
3. ✅ Shared utilities where truly generic (`session_utils.py`)
4. ✅ Documentation over DRY fanaticism

The codebase is intentionally **pragmatic** rather than **perfectly DRY**.
