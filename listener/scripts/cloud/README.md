# Cloud GPU Scripts

Helper scripts for hybrid local+cloud workflows with vast.ai, RunPod, etc.

## Quick Start

### 1. Setup SSH Config

Add to `~/.ssh/config`:

```
Host vast-listener
    HostName <your-instance-ip>
    Port <your-instance-port>
    User root
    LocalForward 8080 localhost:8080
    ServerAliveInterval 60
```

### 2. Setup Cloud Instance

```bash
# SSH to your cloud instance
ssh vast-listener

# Run setup (first time only)
bash < scripts/cloud/setup_cloud_instance.sh
```

### 3. Sync Data to Cloud

```bash
# From your local machine
./scripts/cloud/sync_to_cloud.sh
```

### 4. Train on Cloud

```bash
# Option A: Remote command from local
./scripts/cloud/remote_train.sh

# Option B: SSH and run manually
ssh vast-listener
cd weather-nft-live/listener
python scripts/train.py --data data/sessions --epochs 50
```

### 5. Download Results

```bash
# From your local machine
./scripts/cloud/sync_from_cloud.sh
```

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup_cloud_instance.sh` | Initial cloud setup | Run on cloud instance |
| `sync_to_cloud.sh` | Upload local data | Run from local machine |
| `sync_from_cloud.sh` | Download results | Run from local machine |
| `remote_train.sh` | Train remotely | Run from local machine |

## Configuration

All scripts use the SSH host `vast-listener` by default.

You can override:
```bash
./sync_to_cloud.sh my-other-host
./remote_train.sh my-other-host 100 32  # 100 epochs, batch 32
```

## See Also

- [Full hybrid cloud setup guide](../../docs/HYBRID_CLOUD_SETUP.md)
- [Low-memory GPU guide](../../docs/LOW_MEMORY_GPU.md)
