# Advanced Meditation Analysis Features

Based on Kovacevic et al. (2015) neurofeedback research paper.

## Table of Contents

1. [Performance Ratios](#performance-ratios)
2. [Personal Thresholds](#personal-thresholds)
3. [Learning Potential Prediction](#learning-potential-prediction)
4. [Delta Reduction Tracking](#delta-reduction-tracking)
5. [Real-time State Messages](#real-time-state-messages)
6. [Training Effect](#training-effect)

---

## Performance Ratios

### What Are They?

Performance ratios quantify **how well you're hitting your meditation targets** vs missing them.

**Metrics:**
- **Alpha Performance (aP)** = (alpha+ states) / (alpha- states)
- **Beta Performance (bP)** = (beta+ states) / (beta- states)

**State Definitions:**
- **alpha+** = RSP above upper threshold → "Good relaxation!"
- **alpha-** = RSP below lower threshold → "Too tense"
- **beta+** = RSP above upper threshold → "Strong concentration"
- **beta-** = RSP below lower threshold → "Mind wandering"

### Why It Matters

Instead of just tracking average power, you get a **success/failure ratio**:
- **aP = 5.0** → You hit relaxation 5× more than you miss it (excellent!)
- **aP = 0.5** → You miss relaxation 2× more than you hit it (struggling)

### Example Output

```
Alpha Performance (aP): 3.25 (76% success rate)
  - alpha+ states: 87 (good relaxation)
  - alpha- states: 27 (too tense)

Beta Performance (bP): 1.80 (65% success rate)
  - beta+ states: 54 (good concentration)
  - beta- states: 30 (mind wandering)
```

### How to Use

```python
from utils.meditation_analysis import MeditationAnalyzer
import numpy as np

analyzer = MeditationAnalyzer()

# Get alpha/beta timeseries from your session
performance = analyzer.compute_performance_ratios(
    alpha_timeseries=alpha_arr,
    beta_timeseries=beta_arr
)

print(f"Alpha Performance: {performance['alpha_performance']:.2f}")
print(f"Success rate: {performance['alpha_success_pct']:.1f}%")
```

**Automatically included** when you call `analyzer.analyze_session()`!

---

## Personal Thresholds

### What Are They?

Instead of using generic one-size-fits-all targets, **your first session becomes your baseline**. All future thresholds are personalized to you.

**Formula (from research):**
- Lower threshold = 0.9 × your_baseline_mean
- Upper threshold = 1.1 × your_baseline_mean (alpha) or 1.2× (beta)

### Why It Matters

Everyone's brain is different:
- **Person A:** Naturally high alpha (0.30 RSP)
- **Person B:** Naturally low alpha (0.15 RSP)

Without personalization, generic thresholds would be too easy for Person A and impossible for Person B.

With personalization: **You vs You** comparison!

### Example

**Your baseline session:** Mean alpha RSP = 0.22

**Your personal thresholds:**
- Lower: 0.9 × 0.22 = **0.198**
- Upper: 1.1 × 0.22 = **0.242**

Now you're aiming for **10-20% improvement over YOUR baseline**, not some arbitrary number.

### How to Use

```python
# Option 1: Initialize with baseline
analyzer = MeditationAnalyzer(
    baseline_session="data/sessions/session_001_features.h5"
)

# Now all analyses use YOUR personal thresholds
metrics = analyzer.analyze_session(current_session_df)
# Performance ratios automatically use your thresholds!

# Option 2: Set baseline later
analyzer = MeditationAnalyzer()
analyzer._compute_personal_thresholds("data/sessions/session_001_features.h5")
```

**Via CLI:**
```bash
# Track learning with personal thresholds
python scripts/analyze_meditation.py \
    --sessions-dir data/sessions \
    --baseline session_001_features.h5 \
    --plot
```

---

## Learning Potential Prediction

### What Is It?

**Predict your meditation learning trajectory from just your FIRST session!**

Based on the research finding:
- **High delta + low beta/gamma at baseline** → 169% improvement (fast learner)
- **Low delta + high beta/gamma at baseline** → -44% improvement (slow learner)

### The Science

The paper found that baseline brain patterns predict who will respond well to neurofeedback meditation training vs who will struggle.

**Predictor Score** = delta_RSP - (beta_RSP + gamma_RSP)

### Categories

**1. Fast Learner** (predictor > 0.05)
- Expected improvement: +100% to +200%
- You're naturally suited for meditation
- Rapid gains in weeks, not months

**2. Moderate Learner** (predictor -0.05 to +0.05)
- Expected improvement: +20% to +80%
- Steady, consistent progress
- Most people fall here

**3. Slow Learner** (predictor < -0.05)
- Expected improvement: -20% to +40%
- May need different approach
- Try body-scan, breathwork, or movement practices

### Example Output

```
╔══════════════════════════════════════════════════════════════╗
║           LEARNING POTENTIAL PREDICTION                      ║
╚══════════════════════════════════════════════════════════════╝

📊 Category: FAST LEARNER
📈 Expected Improvement: +100% to +200%
🧠 Predictor Score: 0.085

💭 High learning potential! Your baseline brain patterns suggest
   you'll respond very well to meditation practice.

💡 RECOMMENDATIONS:
   1. You're naturally suited for meditation practice
   2. Expect to see rapid improvements (weeks, not months)
   3. Focus on consistency - even short daily sessions will compound
   4. Track your progress to see the rapid gains

🔬 BASELINE BRAIN FEATURES:
   Delta RSP: 0.245
   Beta RSP:  0.145
   Gamma RSP: 0.015
```

### How to Use

```python
# Analyze first session
analyzer = MeditationAnalyzer()
first_session_df = pd.read_hdf("session_001_features.h5", key='features')
metrics = analyzer.analyze_session(first_session_df)

# Predict learning potential
prediction = analyzer.predict_learning_potential(metrics)

print(f"Category: {prediction['category']}")
print(f"Expected: {prediction['expected_improvement']}")
for rec in prediction['recommendations']:
    print(f"  - {rec}")
```

**Via CLI:**
```bash
# Predict from your first session
python scripts/analyze_meditation.py \
    --predict-learning data/sessions/session_001_features.h5
```

**When to Use:**
- After your FIRST meditation session
- To set realistic expectations
- To choose the best practice approach for your brain
- To decide if you need alternative techniques

---

## Delta Reduction Tracking

### What Is It?

Tracks whether you stay **alert vs drowsy** during meditation.

**Delta waves (<4 Hz)** increase when you're falling asleep. During good meditation:
- **Delta should decrease** (staying awake)
- **Beta increase** (concentration)

This is **complementary to beta tracking**.

### Interpretation

- **>10% reduction:** Excellent alertness
- **0-10% reduction:** Good, slight improvement
- **0 to -10%:** Stable alertness
- **< -10%:** Caution! Increasing drowsiness

### Example Output

```
Delta Reduction:
  Early session: 0.235 RSP
  Late session:  0.198 RSP
  Reduction: 15.7%

  ✅ Excellent: Maintained alertness throughout session
```

### How to Use

```python
# Already included in analyze_session()!
metrics = analyzer.analyze_session(session_df)

print(f"Delta reduction: {metrics['delta_reduction_pct']:.1f}%")
print(f"Interpretation: {metrics['delta_reduction_interpretation']}")

# Or compute manually
delta_reduction = analyzer.compute_delta_reduction(
    delta_timeseries=delta_arr,
    window_size=30  # Compare first/last 30 windows (~1 min)
)
```

**Why it matters:**
- Falling asleep ≠ meditation
- If delta increases, sessions may be too long or at wrong time of day
- Helps optimize session timing (morning vs evening)

---

## Real-time State Messages

### What Are They?

Instant feedback on your current meditation state, like the research participants received.

**State Codes:**
- **a+** = Good relaxation! (alpha above upper threshold)
- **a-** = Too tense (alpha below lower threshold)
- **a=** = Neutral alpha
- **b+** = Good concentration! (beta above upper threshold)
- **b-** = Mind wandering (beta below lower threshold)
- **b=** = Neutral beta

### Combined States

| Alpha | Beta | Interpretation |
|-------|------|---------------|
| a+ | b- | 🧘 **Perfect meditation**: Relaxed yet aware |
| a+ | b+ | 🎯 **Focused relaxation**: Calm concentration |
| a- | b+ | 😤 **Tense concentration**: Try to relax |
| a- | b- | 😴 **Low engagement**: Drowsy or distracted |
| a= | b= | 😌 **Neutral state**: Baseline |

### Example Output

```
Real-time State Analysis:

Alpha: a+
  "Good relaxation! Deep meditative state."
  Current: 0.265 RSP (threshold: 0.198-0.242)

Beta: b-
  "Mind wandering. Gently return attention to breath."
  Current: 0.148 RSP (threshold: 0.180-0.270)

Combined: 🧘 Perfect meditation state: Relaxed yet aware
```

### How to Use

```python
# Get state message for current moment
state = analyzer.get_state_message(
    alpha_rsp=0.265,
    beta_rsp=0.148,
    use_personal_thresholds=True
)

print(f"Alpha: {state['alpha_state']} - {state['alpha_message']}")
print(f"Beta: {state['beta_state']} - {state['beta_message']}")
print(f"\n{state['combined_state']}")
```

**Use cases:**
- Real-time feedback during live sessions
- Post-session review to see when you were "in the zone"
- Training to recognize different states
- Building biofeedback apps

---

## Training Effect

### What Is It?

**Percentage improvement from baseline** to current session.

**Formula:** ((current - baseline) / baseline) × 100

### Research Context

In the paper:
- **Fast learners:** +169% beta performance improvement
- **Slow learners:** -44% beta performance (got worse)

### Example

**Session 1 (baseline):**
- Beta Performance = 1.5

**Session 20 (current):**
- Beta Performance = 3.8

**Training Effect:**
- ((3.8 - 1.5) / 1.5) × 100 = **+153%** 🚀

You're a fast learner!

### How to Use

```python
# Get baseline performance
baseline_metrics = analyzer.analyze_session(session_001_df)
baseline_perf = {
    'alpha_performance': baseline_metrics['alpha_performance'],
    'beta_performance': baseline_metrics['beta_performance']
}

# Get current performance
current_metrics = analyzer.analyze_session(session_020_df)
current_perf = {
    'alpha_performance': current_metrics['alpha_performance'],
    'beta_performance': current_metrics['beta_performance']
}

# Compute training effect
beta_training_effect = analyzer.compute_training_effect(
    baseline_performance=baseline_perf,
    current_performance=current_perf,
    metric='beta_performance'
)

print(f"Beta Training Effect: {beta_training_effect:+.1f}%")

if beta_training_effect > 100:
    print("🚀 Fast learner! Exceptional progress")
elif beta_training_effect > 20:
    print("📈 Steady improvement")
elif beta_training_effect > 0:
    print("📊 Slight improvement")
else:
    print("📉 Consider adjusting practice approach")
```

---

## Complete Example Workflow

### Step 1: First Session - Predict Learning Potential

```bash
# Record your first meditation session
python scripts/capture_session.py --duration 300 --output session_001

# Process features
python scripts/extract_features.py --input session_001.csv

# Predict your learning trajectory
python scripts/analyze_meditation.py \
    --predict-learning data/sessions/session_001_features.h5

# Output: "Fast Learner: Expect +100-200% improvement"
```

### Step 2: Establish Personal Thresholds

Your first session automatically becomes your baseline! All future analyses will use YOUR personal thresholds.

### Step 3: Track Progress with All Metrics

```bash
# After 10 sessions...
python scripts/analyze_meditation.py \
    --sessions-dir data/sessions \
    --baseline session_001_features.h5 \
    --plot \
    --report
```

**You get:**
- Traditional metrics (depth, quality, stability)
- **Performance ratios** (alpha+/alpha-, beta+/beta-)
- **Training effect** (% improvement from baseline)
- **Delta reduction** (alertness tracking)
- Personal thresholds comparison

### Step 4: Real-time Feedback (Optional)

Build a live meditation app:

```python
# During meditation session
for window in realtime_windows:
    alpha_rsp = compute_alpha_rsp(window)
    beta_rsp = compute_beta_rsp(window)

    state = analyzer.get_state_message(alpha_rsp, beta_rsp)

    # Show user their current state
    display_feedback(state['combined_state'])

    # Play sound or visual cue
    if state['alpha_state'] == 'a+':
        play_success_sound()
```

---

## Scientific Background

### The Paper

**Title:** "My Virtual Dream: Collective Neurofeedback in an Immersive Art Environment"

**Authors:** Kovacevic et al. (2015)

**Key Findings:**
1. Brain states can be modulated in **~1 minute** with feedback
2. **Relative spectral power** more informative than absolute
3. **Personalized thresholds** better than generic ones
4. **Baseline predicts learning:** High delta + low beta/gamma → fast learning
5. **Performance ratios** (success/failure) better than simple averages

**Why we trust it:**
- 523 participants (large sample)
- Rigorous statistical methods (PLS, bootstrap, split-half resampling)
- Published in peer-reviewed journal (PLOS ONE)
- Real-world art installation context

### How THE LISTENER Implements It

✅ **Relative Spectral Power (RSP)** - Core metric throughout
✅ **Performance Ratios** - New metrics: `alpha_performance`, `beta_performance`
✅ **Personal Thresholds** - Baseline-derived, individualized
✅ **Learning Prediction** - `predict_learning_potential()` method
✅ **Delta Reduction** - Alertness tracking
✅ **Real-time Feedback** - `get_state_message()` method
✅ **Training Effect** - % improvement calculation

---

## API Reference

### MeditationAnalyzer

```python
from utils.meditation_analysis import MeditationAnalyzer

# Initialize
analyzer = MeditationAnalyzer(
    sampling_rate=256,
    baseline_session="path/to/first/session.h5"  # Optional
)

# Compute performance ratios
performance = analyzer.compute_performance_ratios(
    alpha_timeseries: np.ndarray,
    beta_timeseries: np.ndarray,
    use_personal_thresholds: bool = True
) -> Dict

# Compute training effect
training_effect = analyzer.compute_training_effect(
    baseline_performance: Dict,
    current_performance: Dict,
    metric: str = 'beta_performance'
) -> float

# Predict learning potential
prediction = analyzer.predict_learning_potential(
    first_session_metrics: Dict
) -> Dict

# Get real-time state message
state = analyzer.get_state_message(
    alpha_rsp: float,
    beta_rsp: float,
    use_personal_thresholds: bool = True
) -> Dict

# Track delta reduction
delta_reduction = analyzer.compute_delta_reduction(
    delta_timeseries: np.ndarray,
    window_size: int = 30
) -> Dict
```

---

## FAQ

**Q: Do I need to use all these features?**

A: No! The basic `analyze_session()` includes everything. Advanced features are optional for deeper insights.

**Q: Should I always use personal thresholds?**

A: YES if you're tracking your own progress. NO if comparing across people.

**Q: When should I check my learning prediction?**

A: After your FIRST session. It helps set expectations and choose the best approach.

**Q: What if I'm a "slow learner"?**

A: Don't be discouraged! The research shows some brains need a different approach (body-scan, movement, longer sessions). You CAN learn, just differently.

**Q: Can I use this for real-time biofeedback?**

A: YES! Use `get_state_message()` during live sessions for instant feedback.

**Q: How often should I meditate?**

A: The research shows learning happens in ~1 minute. Even 5-10 minute daily sessions are effective!

---

## Further Reading

- **Original paper:** https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0130129
- **THE LISTENER docs:** `docs/MEDITATION_SCIENCE.md`
- **Technical implementation:** `src/utils/meditation_analysis.py`

---

Generated by THE LISTENER - AI Meditation Witness
