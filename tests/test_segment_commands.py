"""Behavior tests for the production delay helper (no HA installation needed)."""

import asyncio
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "segment_commands", ROOT / "custom_components/wled/segment_commands.py"
)
commands = importlib.util.module_from_spec(spec)
spec.loader.exec_module(commands)
real_sleep = asyncio.sleep


class SegmentCommandsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.events = []
        self.sent = []
        self.sleeps = []
        self.release = asyncio.Event()

        async def sleep(seconds):
            self.sleeps.append(seconds)
            await self.release.wait()

        async def on(**kwargs):
            self.sent.append(("on", kwargs))

        async def off(**kwargs):
            self.sent.append(("off", kwargs))

        self.helper = commands.SegmentCommands(
            on, off, lambda request_id: self.events.append("request"), asyncio.create_task
        )
        self.sleep_patch = patch.object(commands, "sleep", sleep)
        self.sleep_patch.start()

    async def asyncTearDown(self):
        await self.helper.close()
        self.sleep_patch.stop()

    async def tick(self):
        await real_sleep(0)

    async def test_event_before_delay_and_no_ack_needed(self):
        await self.helper.turn_on(False, effect="Lake")
        self.assertEqual(self.events, ["request"])
        self.assertEqual(self.sent, [])
        await self.tick()
        self.assertEqual(self.sleeps, [1.0])
        self.release.set()
        await self.tick()
        self.assertEqual(self.sent, [("on", {"effect": "Lake"})])

    async def test_off_during_delay_cancels_on(self):
        await self.helper.turn_on(False)
        await self.tick()
        await self.helper.turn_off(transition=0.5)
        self.release.set()
        await self.tick()
        self.assertEqual(self.sent, [("off", {"transition": 0.5})])

    async def test_off_before_task_starts_cancels_on(self):
        await self.helper.turn_on(False)
        await self.helper.turn_off()
        self.release.set()
        await self.tick()
        self.assertEqual(self.sent, [("off", {})])

    async def test_running_light_updates_immediately(self):
        await self.helper.turn_on(True, brightness=100, rgb_color=(1, 2, 3))
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(self.events, [])
        self.assertEqual(self.sleeps, [])

    async def test_repeated_on_merges_without_restart(self):
        await self.helper.turn_on(False, brightness=20, effect="Solid")
        await self.tick()
        await self.helper.turn_on(False, brightness=90)
        self.release.set()
        await self.tick()
        self.assertEqual(self.events, ["request"])
        self.assertEqual(self.sleeps, [1.0])
        self.assertEqual(self.sent, [("on", {"brightness": 90, "effect": "Solid"})])

    async def test_off_on_starts_fresh_countdown(self):
        await self.helper.turn_on(False, effect="Lake")
        await self.tick()
        await self.helper.turn_off()
        await self.helper.turn_on(False, effect="Solid")
        await self.tick()
        self.assertEqual(self.sleeps, [1.0, 1.0])
        self.release.set()
        await self.tick()
        self.assertEqual(self.sent, [("off", {}), ("on", {"effect": "Solid"})])

    async def test_unload_cancels_on(self):
        await self.helper.turn_on(False)
        await self.tick()
        await self.helper.close()
        self.release.set()
        await self.tick()
        await self.helper.turn_on(False)
        self.assertEqual(self.sent, [])

    async def test_segments_do_not_block_each_other(self):
        other_sent = []

        async def other_on(**kwargs):
            other_sent.append(kwargs)

        other = commands.SegmentCommands(
            other_on, self.helper._send_off, lambda request_id: None, asyncio.create_task
        )
        try:
            await self.helper.turn_on(False)
            await other.turn_on(False)
            await self.tick()
            self.assertEqual(self.sleeps, [1.0, 1.0])
            self.release.set()
            await self.tick()
            self.assertEqual(len(self.sent), 1)
            self.assertEqual(len(other_sent), 1)
        finally:
            await other.close()

    async def test_off_follows_http_command_already_started(self):
        entered = asyncio.Event()
        finish = asyncio.Event()

        async def slow_on(**kwargs):
            entered.set()
            await finish.wait()
            self.sent.append(("on", kwargs))

        self.helper._send_on = slow_on
        await self.helper.turn_on(False)
        self.release.set()
        await entered.wait()
        off = asyncio.create_task(self.helper.turn_off())
        await self.tick()
        self.assertEqual(self.sent, [])
        finish.set()
        await off
        self.assertEqual(self.sent, [("on", {}), ("off", {})])

    async def test_send_failure_does_not_block_next_request(self):
        async def fail(**kwargs):
            raise RuntimeError("offline")

        self.helper._send_on = fail
        await self.helper.turn_on(False)
        task = self.helper._timer_task
        self.release.set()
        with self.assertRaisesRegex(RuntimeError, "offline"):
            await task
        await self.helper.turn_off()
        self.assertEqual(self.sent, [("off", {})])

    async def test_ready_before_timer_starts_sends_once(self):
        await self.helper.turn_on(False, effect="Lake")
        request_id = self.helper._request_id
        self.assertTrue(self.helper.ready(request_id))
        self.assertFalse(self.helper.ready(request_id))
        await self.tick()
        self.assertEqual(self.sent, [("on", {"effect": "Lake"})])
        self.release.set()
        await self.tick()
        self.assertEqual(len(self.sent), 1)

    async def test_ready_during_wait_keeps_latest_parameters(self):
        await self.helper.turn_on(False, brightness=10)
        await self.tick()
        await self.helper.turn_on(False, brightness=80)
        self.assertTrue(self.helper.ready(self.helper._request_id))
        await self.tick()
        self.assertEqual(self.sent, [("on", {"brightness": 80})])
        self.assertFalse(self.release.is_set())

    async def test_wrong_request_id_keeps_timeout(self):
        await self.helper.turn_on(False)
        self.assertFalse(self.helper.ready("wrong"))
        await self.tick()
        self.assertEqual(self.sent, [])
        self.release.set()
        await self.tick()
        self.assertEqual(self.sent, [("on", {})])

    async def test_late_ready_after_timeout_is_ignored(self):
        await self.helper.turn_on(False)
        request_id = self.helper._request_id
        self.release.set()
        await self.tick()
        self.assertFalse(self.helper.ready(request_id))
        self.assertEqual(self.sent, [("on", {})])

    async def test_off_wins_over_queued_ready(self):
        await self.helper.turn_on(False)
        request_id = self.helper._request_id
        self.helper.ready(request_id)
        await self.helper.turn_off()
        await self.tick()
        self.assertFalse(self.helper.ready(request_id))
        self.assertEqual(self.sent, [("off", {})])

    async def test_old_ready_cannot_release_new_request(self):
        await self.helper.turn_on(False)
        old_id = self.helper._request_id
        self.helper.ready(old_id)
        await self.helper.turn_off()
        await self.helper.turn_on(False, effect="Solid")
        new_id = self.helper._request_id
        self.assertNotEqual(old_id, new_id)
        self.assertFalse(self.helper.ready(old_id))
        await self.tick()
        self.assertEqual(self.sent, [("off", {})])
        self.assertTrue(self.helper.ready(new_id))
        await self.tick()
        self.assertEqual(self.sent[-1], ("on", {"effect": "Solid"}))

    async def test_ready_after_unload_is_ignored(self):
        await self.helper.turn_on(False)
        request_id = self.helper._request_id
        self.helper.ready(request_id)
        await self.helper.close()
        self.assertFalse(self.helper.ready(request_id))
        self.assertEqual(self.sent, [])

    async def test_timeout_and_ready_same_turn_send_once(self):
        await self.helper.turn_on(False)
        await self.tick()
        self.release.set()
        self.helper.ready(self.helper._request_id)
        await self.tick()
        self.assertEqual(self.sent, [("on", {})])


class EffectsTests(unittest.TestCase):
    def test_blends_and_bpm_use_exact_firmware_names(self):
        self.assertEqual(
            commands.filtered_effects({"Bpm", "Blends", "Solid", "Blink"}),
            ["Solid", "Blends", "Bpm"],
        )
        self.assertNotIn("Bends", commands.ALLOWED_EFFECTS)
        self.assertNotIn("BPM", commands.ALLOWED_EFFECTS)

    def test_exact_29_effects_solid_first(self):
        self.assertEqual(len(commands.ALLOWED_EFFECTS), 29)
        self.assertEqual(len(set(commands.ALLOWED_EFFECTS)), 29)
        self.assertEqual(commands.ALLOWED_EFFECTS[0], "Solid")

    def test_unsupported_names_removed_and_order_kept(self):
        self.assertEqual(
            commands.filtered_effects({"Rainbow", "Solid", "Lake", "Blink"}),
            ["Solid", "Lake", "Rainbow"],
        )


if __name__ == "__main__":
    unittest.main()
