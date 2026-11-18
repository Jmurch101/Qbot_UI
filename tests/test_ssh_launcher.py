"""SSH launcher validation without opening a network session."""

from __future__ import annotations

import builtins
import unittest
from unittest import mock

from qbotui.ssh_launcher import SshLaunchError, SshTarget, launch_remote_script


class SshLauncherTest(unittest.TestCase):
    def test_rejects_empty_host_or_user(self) -> None:
        with self.assertRaises(SshLaunchError):
            launch_remote_script(SshTarget("", "nvidia", ""), "true", "x.py")
        with self.assertRaises(SshLaunchError):
            launch_remote_script(SshTarget("10.0.0.2", "", ""), "true", "x.py")

    def test_missing_paramiko_is_reported(self) -> None:
        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "paramiko" or name.startswith("paramiko."):
                raise ImportError("no paramiko")
            return real_import(name, globals, locals, fromlist, level)

        with mock.patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(SshLaunchError) as raised:
                launch_remote_script(
                    SshTarget("10.0.0.2", "nvidia", "secret"),
                    "echo 1",
                    "line_follow.py",
                )
        self.assertIn("Paramiko", str(raised.exception))

    def test_successful_remote_start(self) -> None:
        stdout = mock.Mock()
        stdout.channel.recv_exit_status.return_value = 0
        stdout.read.return_value = b"4321\n"
        stderr = mock.Mock()
        stderr.read.return_value = b""
        client = mock.Mock()
        client.exec_command.return_value = (mock.Mock(), stdout, stderr)

        fake_paramiko = mock.Mock()
        fake_paramiko.SSHClient.return_value = client
        fake_paramiko.AutoAddPolicy.return_value = object()

        with mock.patch.dict("sys.modules", {"paramiko": fake_paramiko}):
            result = launch_remote_script(
                SshTarget("10.0.0.2", "nvidia", "secret"),
                "echo 4321",
                "line_follow.py",
            )
        self.assertEqual(result.remote_pid, "4321")
        self.assertIn("line_follow.py", result.detail)
        client.connect.assert_called_once()
        client.close.assert_called_once()
