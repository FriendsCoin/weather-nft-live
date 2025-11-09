# Meditation Science Integration

How THE LISTENER incorporates neurofeedback research findings.

## Research Foundation

Based on **Kovacevic et al. (2015)** "My Virtual Dream" neurofeedback study:

> "Unprecedented speed of learning changes in the power spectrum (~1 min)"

Key findings integrated into THE LISTENER:
- **Fast learning**: Brain states modulate in ~1 minute
- **Alpha (8-12 Hz)**: Primary meditation/relaxation marker
- **Beta (18-30 Hz)**: Concentration/mental activity marker
- **Relative Spectral Power (RSP)**: More robust than absolute power
- **Frontal sensors**: Critical for state detection (Fp1, Fp2 ~ Muse S AF7, AF8)

## Enhanced Features

### 1. Relative Spectral Power (RSP)

**What it is:**
- Band power divided by total power across all bands
- Normalizes individual differences in absolute EEG amplitude
- More consistent across sessions and individuals

**Why it matters:**
- Absolute power varies with skin conductance, electrode contact
- RSP focuses on the _distribution_ of power across bands
- Better for tracking meditation quality over time

**Implementation:**
```python
from src.utils.meditation_analysis import MeditationAnalyzer

analyzer = MeditationAnalyzer()
features = pd.read_hdf("session.h5")
metrics = analyzer.analyze_session(features)

# RSP values are 0-1 (percentages of total power)
print(f"Alpha RSP: {metrics['mean_alpha_rsp']:.3f}")  # e.g., 0.350 = 35% of total
print(f"Beta RSP: {metrics['mean_beta_rsp']:.3f}")    # e.g., 0.180 = 18% of total
```

### 2. Meditation Depth Score

**Formula:**
```
depth = (0.5 * alpha + 0.3 * theta - 0.3 * beta - 0.2 * delta) * normalized
```

**Interpretation:**
- **0-30**: Beginner - Mind wandering, high mental activity
- **30-50**: Intermediate - Developing focus, some relaxation
- **50-70**: Advanced - Consistent relaxation, low mental chatter
- **70-100**: Expert - Deep meditation, strong alpha dominance

**What it measures:**
- ↑ Alpha = relaxed awareness (meditation)
- ↑ Theta = deep meditation (not drowsiness if delta low)
- ↓ Beta = reduced mental chatter
- ↓ Delta = awake (not falling asleep)

### 3. Alpha/Beta Ratio

**Significance:**
- **> 1.5**: Deep relaxation state
- **1.0-1.5**: Balanced meditation (ideal)
- **0.7-1.0**: Active meditation with some concentration
- **< 0.7**: Concentration-dominant (not typical meditation)

Research shows meditation increases alpha while decreasing beta.

### 4. Learning Curve Tracking

Tracks progression across sessions:

```python
learning = analyzer.track_learning_curve(session_files)

# Shows:
# - Session-by-session depth improvement
# - Overall learning trend (slope)
# - Quality score evolution
# - Stability development
```

**Expected patterns:**
- Early sessions: Variable depth, frequent transitions
- Mid practice: Increasing stability, rising mean depth
- Advanced: High depth, stable states, few transitions

### 5. State Transition Detection

**What are transitions:**
- Significant shifts in meditation depth (>10-15 points)
- "Deepening" = depth increasing
- "Surfacing" = depth decreasing

**Why track them:**
- Fewer transitions = more stable meditation
- Pattern of deepening/surfacing shows session arc
- Can correlate with external events (sounds, thoughts)

```python
transitions = analyzer.detect_state_transitions(depth_timeseries)

# Example output:
# {
#   'time_seconds': 240,
#   'type': 'deepening',
#   'magnitude': 18.5,
#   'depth_before': 42.3,
#   'depth_after': 60.8
# }
```

### 6. Quality Score

Composite metric (0-100):
- **50%**: Mean depth
- **25%**: Stability (inverse of variance)
- **15%**: Alpha dominance (alpha / (alpha + beta))
- **10%**: Learning slope (positive trend)

**Interpretation:**
- **80-100**: Excellent session
- **60-80**: Good session
- **40-60**: Average session
- **20-40**: Challenging session
- **0-20**: Very difficult session

## Scientific Validity

### What THE LISTENER does:

✅ Uses established frequency bands (delta, theta, alpha, beta, gamma)
✅ Employs relative spectral power (research-validated)
✅ Focuses on frontal channels (meditation research standard)
✅ Tracks learning over time (neurofeedback principle)
✅ Analyzes temporal dynamics (state transitions)

### What THE LISTENER does NOT do:

❌ Diagnose medical conditions
❌ Replace clinical EEG analysis
❌ Make absolute judgments about meditation quality
❌ Claim scientific measurement of "enlightenment"

### Artistic vs Scientific Goals

**Scientific neurofeedback:**
- Goal: Train specific brain states
- Method: Real-time feedback, reinforcement
- Outcome: Measurable behavior change

**THE LISTENER (art project):**
- Goal: Witness and interpret meditation
- Method: Retrospective analysis, poetic interpretation
- Outcome: Subjective meaning-making

We use science to inform the interpretation, not to optimize or judge.

## Usage Guide

### Analyze Single Session

```bash
python scripts/analyze_meditation.py \
    --session data/sessions/session_015_features.h5 \
    --plot

# Output:
# - Meditation depth: 64.2/100
# - Alpha/Beta ratio: 1.42
# - Stability: 3.45
# - Quality score: 71.8/100
# - Plot: depth over time, alpha vs beta, transitions
```

### Track Learning Across Sessions

```bash
python scripts/analyze_meditation.py \
    --sessions-dir data/sessions \
    --plot \
    --report

# Outputs:
# - learning_curve.csv (data)
# - learning_progression.png (plots)
# - meditation_report.txt (comprehensive analysis)
```

### Integrate with Memory Generation

Enhanced memory generation includes quality metrics:

```python
from src.models.sampler import LatentSampler
from src.utils.meditation_analysis import MeditationAnalyzer

# Sample from high-quality sessions only
analyzer = MeditationAnalyzer()

for session_file in session_files:
    features = pd.read_hdf(session_file)
    metrics = analyzer.analyze_session(features)

    if metrics['quality_score'] > 70:
        # Generate memories from excellent sessions
        sampler.generate_from_session(session_file)
```

## Visualization Examples

### Session Analysis Plot

Shows:
- Depth over time (primary metric)
- Alpha vs Beta power (state indicators)
- Quality metrics (bar chart)
- Alpha/Beta ratio (balance)
- State transitions (marked on timeline)

### Learning Progression Plot

Shows across multiple sessions:
- Meditation depth evolution
- Quality score progression
- Alpha/Beta ratio changes
- Stability development

## Research References

1. **Kovacevic et al. (2015)**
   "My Virtual Dream: Collective Neurofeedback in an Immersive Art Environment"
   _PLOS ONE_
   - Fast learning (~1 min)
   - RSP superiority
   - Alpha/beta markers

2. **Cahn & Polich (2006)**
   "Meditation states and traits: EEG, ERP, and neuroimaging studies"
   _Psychological Bulletin_
   - Meditation increases alpha
   - Decreases beta during practice

3. **Lomas et al. (2015)**
   "A systematic review of the neurophysiology of mindfulness"
   _Clinical Psychology Review_
   - Alpha power correlates with meditation depth
   - Theta in advanced meditators

## Interpreting Your Results

### High Alpha, Low Beta
**= Classic meditation**
- Relaxed but alert
- Mental chatter reduced
- Often reported as "peaceful"

### High Alpha, Moderate Beta
**= Engaged meditation**
- Focused attention maintained
- Active awareness
- Often reported as "clear"

### Low Alpha, High Beta
**= Mind wandering**
- Difficulty settling
- Thoughts dominant
- Often reported as "restless"

### High Theta, High Alpha
**= Deep meditation**
- Advanced practitioners
- Deeply relaxed
- Often reported as "profound"

### High Delta
**= Drowsiness**
- Falling asleep (not meditation)
- Session may need adjustment
- Common in evening sessions

## Practical Applications

### 1. Session Timing

Find your optimal meditation time:
```python
# Analyze by time of day
morning_sessions = [s for s in sessions if '06' <= s.time <= '10']
evening_sessions = [s for s in sessions if '18' <= s.time <= '22']

# Compare quality scores
```

### 2. Progress Tracking

See if you're improving:
```python
# Compare first 10 vs last 10 sessions
early = sessions[:10]
late = sessions[-10:]

# Metric comparison
```

### 3. Optimal Session Length

Find your concentration window:
```python
# Plot depth by session minute
# Peak usually 10-25 minutes in
```

### 4. Technique Comparison

Try different meditation styles:
```python
# Compare breath-focused vs body-scan vs mantra
# Which produces highest alpha?
```

## Limitations

### What to be careful about:

1. **Individual Variation**: Your baseline differs from others
2. **Artifacts**: Movement, eye blinks affect readings
3. **Context**: Time of day, caffeine, stress all matter
4. **Not Diagnostic**: This is art, not medicine
5. **Subjectivity**: Metrics capture signals, not experience

### Best practices:

- Track trends, not absolute values
- Compare your sessions to your baseline
- Use consistent conditions (time, location)
- Don't over-interpret single sessions
- Remember: this is witnessing, not optimizing

---

**Science informs the interpretation, art gives it meaning.** 🧘‍♀️🔬✨
