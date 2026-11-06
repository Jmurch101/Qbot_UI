"""BindPolicy rejects illegal hosts, port 18888, and a second address."""

from __future__ import annotations

import unittest

from qbotui.bind_policy import BindPolicy, BindRejected
from qbotui.contract import ProbeContract


class BindPolicyTest(unittest.TestCase):
    def test_allowed_port_set_is_exact(self) -> None:
        self.assertEqual(
            BindPolicy.ALLOWED_PORTS,
            frozenset({18801, 18802, 18803, 18601}),
        )
        self.assertEqual(ProbeContract.ports(), BindPolicy.ALLOWED_PORTS)

    def test_rejects_unspecified_loopback_and_empty_host(self) -> None:
        for host in ("0.0.0.0", "127.0.0.1", ""):
            policy = BindPolicy()
            with self.assertRaises(BindRejected):
                policy.confirm(host)
            with self.assertRaises(BindRejected):
                policy.authorize_bind(host, 18801)

    def test_rejects_port_outside_the_probe_set(self) -> None:
        policy = BindPolicy()
        policy.confirm("10.1.2.3")
        with self.assertRaises(BindRejected):
            policy.authorize_bind("10.1.2.3", 18888)

    def test_rejects_a_second_address(self) -> None:
        policy = BindPolicy()
        self.assertEqual(policy.confirm("10.1.2.3"), "10.1.2.3")
        with self.assertRaises(BindRejected):
            policy.confirm("10.1.2.4")
        with self.assertRaises(BindRejected):
            policy.authorize_bind("10.9.9.9", 18801)
        for port in (18801, 18802, 18803, 18601):
            self.assertEqual(policy.authorize_bind("10.1.2.3", port), ("10.1.2.3", port))
