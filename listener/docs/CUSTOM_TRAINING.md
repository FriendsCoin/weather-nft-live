# Custom Model Training Guide

Complete guide to advanced training techniques for THE LISTENER VAE models.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Hyperparameter Optimization](#hyperparameter-optimization)
- [PyTorch Lightning Training](#pytorch-lightning-training)
- [Custom Loss Functions](#custom-loss-functions)
- [Training Utilities](#training-utilities)
- [Experiment Tracking](#experiment-tracking)
- [Advanced Techniques](#advanced-techniques)

---

## Overview

THE LISTENER provides advanced training tools for customizing VAE models:

✨ **Features**:
- 🔍 Automated hyperparameter optimization (Optuna)
- ⚡ Simplified training with PyTorch Lightning
- 📊 TensorBoard integration for experiment tracking
- 🎯 Custom loss functions for EEG data
- 🔧 Training utilities (early stopping, checkpointing, etc.)
- 📈 Advanced learning rate scheduling

---

## Quick Start

### Install Advanced Dependencies

```bash
pip install tensorboard optuna pytorch-lightning torchmetrics torchinfo
```

### 1. Standard Training (Existing Method)

```bash
# Generate data
python scripts/generate_mock_data.py --num-sessions 20 --duration 300

# Train with default settings
python scripts/train.py --epochs 100
```

### 2. Optimize Hyperparameters First

```bash
# Find best hyperparameters automatically
python scripts/optimize_hyperparameters.py --trials 50 --data-dir data/sessions

# Train with optimized parameters
python scripts/train.py \
    --latent-dim 32 \
    --lr 0.001234 \
    --batch-size 32 \
    --beta 1.2
```

### 3. Train with PyTorch Lightning

```python
from models.vae_lightning import train_with_lightning
from models.vae import VAEConfig

# Create config
config = VAEConfig(
    input_dim=34,
    latent_dim=32,
    encoder_layers=[128, 64, 32],
    decoder_layers=[32, 64, 128],
    beta=1.0
)

# Train with Lightning (automatic optimization, logging, checkpoints)
model = train_with_lightning(
    config=config,
    train_loader=train_loader,
    val_loader=val_loader,
    max_epochs=100,
    learning_rate=1e-3,
    checkpoint_dir='data/checkpoints',
    experiment_name='my_experiment'
)
```

---

## Hyperparameter Optimization

Use **Optuna** to automatically find the best hyperparameters.

### Basic Usage

```bash
python scripts/optimize_hyperparameters.py \
    --trials 50 \
    --data-dir data/sessions \
    --device cuda
```

### What Gets Optimized

- **Latent dimension**: 16, 32, 48, 64
- **Learning rate**: 1e-5 to 1e-2 (log scale)
- **Batch size**: 16, 32, 64
- **Beta (KL weight)**: 0.5 to 2.0
- **Dropout**: 0.0 to 0.5
- **Encoder size**: 64, 128, 256

### Visualization

```bash
# Generate interactive HTML visualizations
python scripts/optimize_hyperparameters.py \
    --trials 50 \
    --visualize

# Open in browser:
# data/optuna/visualizations/optimization_history.html
# data/optuna/visualizations/param_importances.html
```

### Advanced Configuration

```python
import optuna

# Create study with custom settings
study = optuna.create_study(
    study_name='my_study',
    direction='minimize',
    pruner=optuna.pruners.MedianPruner(
        n_startup_trials=10,
        n_warmup_steps=5
    )
)

# Custom search space
def objective(trial):
    # Your custom hyperparameter suggestions
    latent_dim = trial.suggest_int('latent_dim', 8, 128)
    # ...
```

### Multi-Objective Optimization

Optimize for both reconstruction quality and KL divergence:

```python
study = optuna.create_study(
    directions=['minimize', 'minimize']  # [recon_loss, kl_loss]
)
```

---

## PyTorch Lightning Training

**PyTorch Lightning** simplifies training with automatic optimization, logging, and more.

### Benefits

- ✅ Automatic GPU/CPU handling
- ✅ Built-in logging (TensorBoard)
- ✅ Easy callbacks (checkpointing, early stopping)
- ✅ Multi-GPU support
- ✅ Gradient clipping
- ✅ Learning rate scheduling

### Basic Example

```python
from models.vae_lightning import VAELightningModule
from pytorch_lightning import Trainer

# Create Lightning model
model = VAELightningModule(
    config=vae_config,
    learning_rate=1e-3,
    optimizer_type='adam',
    scheduler_type='cosine'
)

# Create trainer
trainer = Trainer(
    max_epochs=100,
    accelerator='gpu',
    devices=1,
    gradient_clip_val=1.0
)

# Train
trainer.fit(model, train_loader, val_loader)
```

### With Callbacks

```python
from pytorch_lightning.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor
)

callbacks = [
    # Save top 3 models
    ModelCheckpoint(
        monitor='val_loss',
        mode='min',
        save_top_k=3,
        filename='vae-{epoch:02d}-{val_loss:.4f}'
    ),

    # Early stopping
    EarlyStopping(
        monitor='val_loss',
        patience=15,
        mode='min'
    ),

    # Monitor learning rate
    LearningRateMonitor(logging_interval='epoch')
]

trainer = Trainer(
    max_epochs=100,
    callbacks=callbacks
)
```

### Custom Training Loop

```python
class CustomVAE(VAELightningModule):
    def training_step(self, batch, batch_idx):
        x = batch

        # Custom augmentation
        x = self.augment(x)

        # Forward pass
        recon_x, mu, logvar = self(x)

        # Custom loss
        loss = self.custom_loss(recon_x, x, mu, logvar)

        # Log custom metrics
        self.log('custom_metric', self.compute_metric(x, recon_x))

        return loss
```

---

## Custom Loss Functions

Advanced loss functions for specific EEG training needs.

### Available Losses

#### 1. Weighted MSE Loss

Emphasize certain features more:

```python
from utils.training_utils import CustomLosses

# Weight important features more
weights = torch.ones(34)
weights[0:5] = 2.0  # Double weight for first 5 features (e.g., alpha)

loss = CustomLosses.weighted_mse_loss(output, target, weights)
```

#### 2. Beta-VAE Loss

Standard VAE loss with controllable KL weight:

```python
loss, loss_dict = CustomLosses.beta_vae_loss(
    recon_x, x, mu, logvar,
    beta=1.5  # Higher = more disentangled latent space
)

print(loss_dict['recon_loss'])  # Reconstruction component
print(loss_dict['kl_loss'])     # KL divergence component
```

#### 3. Focal Loss

For imbalanced classification:

```python
# If you add classification head to VAE
loss = CustomLosses.focal_loss(
    predictions, targets,
    alpha=0.25,
    gamma=2.0
)
```

### Creating Custom Losses

```python
class MyCustomLoss(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, output, target, mu, logvar):
        # Your custom loss logic
        recon_loss = F.mse_loss(output, target)
        kl_loss = -0.5 * torch.sum(1 + logvar - mu**2 - logvar.exp())

        # Custom regularization
        custom_reg = torch.mean(torch.abs(mu))

        return recon_loss + 0.1 * kl_loss + 0.01 * custom_reg
```

---

## Training Utilities

### 1. Early Stopping

```python
from utils.training_utils import EarlyStopping

early_stop = EarlyStopping(
    patience=10,
    min_delta=0.001,
    mode='min'
)

for epoch in range(num_epochs):
    train_loss = train_epoch()
    val_loss = validate()

    if early_stop(val_loss):
        print("Early stopping triggered!")
        break
```

### 2. Model Checkpointing

```python
from utils.training_utils import ModelCheckpoint

checkpoint = ModelCheckpoint(
    checkpoint_dir='data/checkpoints',
    model_name='vae',
    mode='min',
    save_top_k=3
)

# Save if among top 3
checkpoint.save(
    model=model,
    optimizer=optimizer,
    epoch=epoch,
    metric=val_loss,
    metadata={'config': config}
)
```

### 3. Learning Rate Scheduling

```python
from utils.training_utils import LearningRateScheduler

# Warmup + Cosine annealing
scheduler = LearningRateScheduler.warmup_cosine_schedule(
    optimizer,
    warmup_epochs=5,
    total_epochs=100,
    min_lr=1e-6
)

# One Cycle policy
scheduler = LearningRateScheduler.one_cycle_schedule(
    optimizer,
    max_lr=1e-2,
    total_steps=num_batches * num_epochs
)
```

### 4. Gradient Clipping

```python
from utils.training_utils import GradientClipping

# In training loop
optimizer.zero_grad()
loss.backward()

# Clip gradients
total_norm = GradientClipping.clip_grad_norm(model, max_norm=1.0)

optimizer.step()
```

---

## Experiment Tracking

Track experiments with **TensorBoard** and JSON logs.

### Basic Usage

```python
from utils.training_utils import ExperimentTracker

# Create tracker
tracker = ExperimentTracker(
    experiment_name='vae_exp_001',
    log_dir='runs'
)

# Log metrics
for epoch in range(num_epochs):
    metrics = {
        'train_loss': train_loss,
        'val_loss': val_loss,
        'learning_rate': current_lr
    }
    tracker.log_metrics(metrics, step=epoch)

# Log hyperparameters and final results
tracker.log_hyperparameters(
    hparams={'lr': 1e-3, 'batch_size': 32},
    metrics={'best_val_loss': 0.123}
)

# Log model architecture
tracker.log_model_graph(model, input_size=(1, 34))

tracker.close()
```

### View in TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir runs

# Open browser
# http://localhost:6006
```

### Export to JSON

All metrics are automatically saved to JSON:

```python
# Read experiment logs
import json

with open('runs/vae_exp_001_log.json') as f:
    history = json.load(f)

for entry in history:
    print(f"Epoch {entry['step']}: {entry['train_loss']}")
```

---

## Advanced Techniques

### 1. Mixed Precision Training

Faster training with less memory:

```python
from pytorch_lightning import Trainer

trainer = Trainer(
    precision=16,  # Use half precision
    max_epochs=100
)
```

### 2. Gradient Accumulation

Simulate larger batch sizes:

```python
trainer = Trainer(
    accumulate_grad_batches=4,  # Accumulate 4 batches
    max_epochs=100
)
```

### 3. Multi-GPU Training

```python
trainer = Trainer(
    accelerator='gpu',
    devices=4,  # Use 4 GPUs
    strategy='ddp'  # Distributed Data Parallel
)
```

### 4. Custom Metrics

```python
from torchmetrics import Metric

class CustomMetric(Metric):
    def __init__(self):
        super().__init__()
        self.add_state("sum", default=torch.tensor(0.0))
        self.add_state("count", default=torch.tensor(0))

    def update(self, preds, target):
        self.sum += torch.sum(torch.abs(preds - target))
        self.count += target.numel()

    def compute(self):
        return self.sum / self.count
```

### 5. Learning Rate Finder

Find optimal learning rate automatically:

```python
from pytorch_lightning.tuner import Tuner

trainer = Trainer()
tuner = Tuner(trainer)

# Run learning rate finder
lr_finder = tuner.lr_find(model, train_loader)

# Plot results
fig = lr_finder.plot(suggest=True)
fig.show()

# Get suggested LR
new_lr = lr_finder.suggestion()
model.learning_rate = new_lr
```

### 6. Batch Size Tuning

```python
tuner = Tuner(trainer)

# Auto-scale batch size
tuner.scale_batch_size(model, train_loader, mode='power')
```

---

## Example Workflows

### Workflow 1: Quick Experiment

```bash
# 1. Generate data
python scripts/generate_mock_data.py --num-sessions 10

# 2. Train with defaults
python scripts/train.py --epochs 50

# 3. View in TensorBoard
tensorboard --logdir runs
```

### Workflow 2: Optimized Training

```bash
# 1. Generate larger dataset
python scripts/generate_mock_data.py --num-sessions 50

# 2. Find best hyperparameters
python scripts/optimize_hyperparameters.py --trials 100 --visualize

# 3. Train with best params
python scripts/train.py \
    --latent-dim 48 \
    --lr 0.00234 \
    --batch-size 32 \
    --beta 1.3 \
    --epochs 200

# 4. Analyze results
tensorboard --logdir runs
```

### Workflow 3: Custom Training Script

```python
#!/usr/bin/env python3
from models.vae_lightning import train_with_lightning
from models.vae import VAEConfig
from utils.training_utils import ExperimentTracker, CustomLosses

# Setup
config = VAEConfig(input_dim=34, latent_dim=32)
tracker = ExperimentTracker('my_experiment')

# Load data
train_loader, val_loader = load_data()

# Train
model = train_with_lightning(
    config=config,
    train_loader=train_loader,
    val_loader=val_loader,
    max_epochs=100,
    learning_rate=1e-3,
    experiment_name='my_experiment',
    early_stopping_patience=20
)

# Log final results
tracker.log_hyperparameters(
    hparams={'latent_dim': 32, 'lr': 1e-3},
    metrics={'final_val_loss': model.trainer.callback_metrics['val_loss'].item()}
)

tracker.close()
```

---

## Tips & Best Practices

### Hyperparameter Tuning

✅ **Do**:
- Start with 20-50 trials for quick insights
- Use pruning to stop bad trials early
- Visualize results to understand trade-offs
- Save best configs for future use

❌ **Don't**:
- Run too many trials on small datasets
- Ignore computational cost
- Optimize too many parameters at once

### Training

✅ **Do**:
- Use early stopping (patience=10-20)
- Monitor both train and val loss
- Save multiple checkpoints
- Use gradient clipping (1.0-5.0)
- Start with smaller models, scale up

❌ **Don't**:
- Train without validation set
- Ignore overfitting (train << val)
- Use too high learning rates
- Skip logging/tracking

### Debugging

```python
# Print model summary
from utils.training_utils import print_model_summary, count_parameters

print_model_summary(model, input_size=(1, 34))
params = count_parameters(model)
print(f"Total parameters: {params['total']:,}")
```

---

## Troubleshooting

### NaN Loss

**Cause**: Gradient explosion, bad initialization

**Fix**:
```python
# Lower learning rate
learning_rate = 1e-4

# Enable gradient clipping
trainer = Trainer(gradient_clip_val=1.0)

# Check data for NaN/Inf
assert not torch.isnan(data).any()
```

### Slow Training

**Cause**: CPU training, large batch size, inefficient data loading

**Fix**:
```bash
# Use GPU
--device cuda

# Reduce batch size
--batch-size 16

# Use multiple workers
DataLoader(dataset, num_workers=4)
```

### Out of Memory

**Cause**: Batch size too large, model too big

**Fix**:
```python
# Reduce batch size
batch_size = 16

# Use gradient accumulation
trainer = Trainer(accumulate_grad_batches=4)

# Use mixed precision
trainer = Trainer(precision=16)
```

---

## References

- [Optuna Documentation](https://optuna.readthedocs.io/)
- [PyTorch Lightning Docs](https://lightning.ai/docs/pytorch/stable/)
- [TensorBoard Guide](https://www.tensorflow.org/tensorboard)
- [β-VAE Paper](https://openreview.net/pdf?id=Sy2fzU9gl)

---

**Ready to train custom models!** 🚀
