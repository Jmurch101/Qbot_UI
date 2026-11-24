# QbotUI

Windows viewer for a physical Quanser QBot Platform hardware session.

One window shows the four probe feeds from the robot's existing `quick_start_qbot_platform.py`. This application is only the PC viewer. It does not replace that script, drive the wheels, or open the robot's driver port.

This repository is separate from the Quanser lab tree. It does not import `pal` or `quanser`, and it does not put the lab tree on `sys.path`.

Repository: https://github.com/telepath01/Qbot_UI.git

## Pull / update

Branch with the current Init + Platform UI and QBot presets:

```text
git fetch jmurch
git checkout feature/ui-revamp
git pull jmurch feature/ui-revamp
```

(If your remote is only `origin`, use that name instead of `jmurch`.)

## Run

Use Python 3.11 through 3.14.

**Laptop / Mac (venv):**

```text
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m qbotui
```

**Lab Windows PC (`quanser_env`):**

```text
conda activate quanser_env
python -m qbotui
```

Activating `quanser_env` sets that environment's own `PYTHONPATH` to the lab libraries. The viewer does not use those modules.

Do not run the lab `observer.py` at the same time. It binds these same ports.

1. Pick a **QBot** (1 / 2 / 3). That fills the SSH host (`192.168.2.145` / `.25` / `.128`).
2. Confirm the one PC IPv4 on the robot subnet (`Quanser_UVS`). That address is `ipHost`.
3. Press **VERIFY SSH CONNECTION**, then **START**. Listeners bind on `ipHost` only; the app SSHs to the QBot and starts the selected task script.
4. Startup runs `/home/nvidia/Desktop/quick_start_qbot_platform.py`. Other labs use `/home/nvidia/Documents/Quanser/...`. On the robot, `ipDriver` stays `localhost`.

Do not start `quick_start_qbot_platform.py` on the Windows/Mac PC. After the robot script has connected, it does not dial the PC again until that script is started over.

Each status row shows listening, connected, disconnected, or bind failure, plus bytes and frames received. The depth title shows the raw 8-bit range. The picture is that received buffer, stretched so the shapes are visible.

## Ports

Start listeners binds only the confirmed address, on these ports and no others:

- `18801` Downward Facing Image — 200×320×1 uint8
- `18802` RealSense RGB Image — 240×320×3 uint8, BGR on the wire
- `18803` RealSense Depth Image — 240×320×1 uint8
- `18601` Leishen M10P Lidar — 210 little-endian float32 pairs

Port `18888` is the robot's own driver. This viewer does not open it.

## Stop

**Stop** closes these PC viewer servers only. It is not a hardware e-stop. Closing the window does not stop the wheels, unload the QUARC model, or release the gamepad. After the robot script has connected, it can keep applying the Logitech F710. Right bumper, or Ctrl+C in the robot script's terminal, is how that script leaves its loop. The robot script stops its own loop at 90 seconds.

This milestone does not use SSH.

## Tests

```text
conda activate quanser_env
python -m unittest
```
