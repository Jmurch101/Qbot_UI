"""Start a robot task script over SSH with Paramiko only."""
from __future__ import annotations

from dataclasses import dataclass


class SshLaunchError(Exception):
    """Remote connect or command failed."""


@dataclass(frozen=True)
class SshTarget:
    host: str
    username: str
    password: str
    port: int = 22


@dataclass(frozen=True)
class SshLaunchResult:
    host: str
    script: str
    remote_pid: str
    detail: str


def _friendly_ssh_error(host: str, exc: Exception) -> str:
    text = str(exc).lower()
    if "no route" in text or "network is unreachable" in text:
        return (
            f"SSH to {host} failed: no route to the QBot. "
            "Rejoin Quanser_UVS Wi‑Fi (en0), confirm ping works, then retry."
        )
    if "timed out" in text or "timeout" in text:
        return (
            f"SSH to {host} failed: timed out. "
            "QBot may be off, on another IP, or Wi‑Fi client isolation is blocking you."
        )
    if "authentication" in text or "auth fail" in text or "permission denied" in text:
        return (
            f"SSH to {host} failed: login rejected. "
            "Enter the nvidia password in the SSH password field (or set up a key)."
        )
    return f"SSH to {host} failed: {exc}"


def launch_remote_script(target: SshTarget, remote_command: str, script_name: str) -> SshLaunchResult:
    """Open an SSH session and start the task script on the device."""
    host = target.host.strip()
    username = target.username.strip()
    if not host:
        raise SshLaunchError("SSH host is empty")
    if not username:
        raise SshLaunchError("SSH username is empty")
    try:
        import paramiko
    except ImportError as exc:
        raise SshLaunchError(
            "Paramiko is not installed. Install it in this environment to start tasks over SSH."
        ) from exc

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=target.port,
            username=username,
            password=target.password if target.password else None,
            look_for_keys=True,
            allow_agent=True,
            timeout=12,
            auth_timeout=12,
            banner_timeout=12,
        )
        _stdin, stdout, stderr = client.exec_command(remote_command, timeout=20)
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
    except SshLaunchError:
        raise
    except Exception as exc:
        raise SshLaunchError(_friendly_ssh_error(host, exc)) from exc
    finally:
        client.close()

    if exit_status != 0:
        detail = err or out or f"remote exit status {exit_status}"
        raise SshLaunchError(f"Remote start of {script_name} failed: {detail}")

    pid = out.splitlines()[-1].strip() if out else "(unknown)"
    return SshLaunchResult(
        host=host,
        script=script_name,
        remote_pid=pid,
        detail=f"Started {script_name} on {host} (pid {pid})",
    )
