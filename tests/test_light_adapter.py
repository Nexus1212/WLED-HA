"""Execute the actual segment class against small HA/WLED test doubles.

Only imports and decorators are substituted. This does not claim to test the
full Home Assistant loader, library exception translation or WebSocket updates.
"""

import ast
import asyncio
from enum import IntFlag
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock, patch

from test_segment_commands import commands, real_sleep


class BaseEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.hass = coordinator.hass
        self.entity_id = "light.test_segment_1"

    async def async_will_remove_from_hass(self):
        pass


class Features(IntFlag):
    EFFECT = 1
    TRANSITION = 2


source = Path(__file__).resolve().parents[1] / 'custom_components/wled/light.py'
tree = ast.parse(source.read_text(encoding='utf-8'))
segment = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'WLEDSegmentLight')
module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), segment], type_ignores=[])
ast.fix_missing_locations(module)
namespace = {
    'WLEDEntity': BaseEntity, 'LightEntity': type('LightEntity', (), {}),
    'LightEntityFeature': Features, 'COLOR_TEMP_K_MIN': 1900, 'COLOR_TEMP_K_MAX': 10091,
    'override': lambda fn: fn, 'callback': lambda fn: fn,
    'wled_exception_handler': lambda fn: fn,
    'SegmentCommands': commands.SegmentCommands, 'filtered_effects': commands.filtered_effects,
    'EVENT_SEGMENT_TURN_ON_REQUESTED': commands.EVENT_SEGMENT_TURN_ON_REQUESTED,
}
for key in ['ON', 'SEGMENT_ID', 'RGB_COLOR', 'RGBW_COLOR', 'RGBWW_COLOR',
            'COLOR_PRIMARY', 'CCT', 'COLOR_TEMP_KELVIN', 'TRANSITION', 'BRIGHTNESS', 'EFFECT']:
    namespace['ATTR_' + key] = key.lower()
exec(compile(module, str(source), 'exec'), namespace)
Segment = namespace['WLEDSegmentLight']


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.gate = asyncio.Event()

        async def sleep(seconds):
            self.assertEqual(seconds, 1.0)
            await self.gate.wait()

        self.patcher = patch.object(commands, 'sleep', sleep)
        self.patcher.start()
        self.state = NS(on=True, brightness=255, segments={1: NS(on=False, light_capabilities=None)})
        self.wled = NS(segment=AsyncMock(), master=AsyncMock())
        self.hass = NS(bus=NS(async_fire=Mock()), async_create_task=lambda coro, name: asyncio.create_task(coro, name=name))
        self.coordinator = NS(
            hass=self.hass, wled=self.wled, has_main_light=True,
            config_entry=NS(entry_id='test-entry'),
            data=NS(info=NS(mac_address='001122334455'), state=self.state,
                    effects={42: NS(name='Lake'), 0: NS(name='Solid'), 7: NS(name='Blink')}),
        )
        self.entity = Segment(self.coordinator, 1)

    async def asyncTearDown(self):
        await self.entity.async_will_remove_from_hass()
        self.patcher.stop()

    async def test_event_and_delayed_original_payload(self):
        await self.entity.async_turn_on(brightness=120, rgb_color=(10, 20, 30), effect='Lake', transition=0.5)
        self.hass.bus.async_fire.assert_called_once_with('wled_segment_turn_on_requested', {
            'entity_id':'light.test_segment_1', 'segment_id':1, 'config_entry_id':'test-entry'})
        self.wled.segment.assert_not_awaited()
        self.gate.set()
        await real_sleep(0)
        self.wled.segment.assert_awaited_once_with(
            on=True, segment_id=1, brightness=120, color_primary=(10,20,30), effect='Lake', transition=5)

    async def test_off_cancels_pending_payload(self):
        await self.entity.async_turn_on()
        await self.entity.async_turn_off()
        self.gate.set()
        await real_sleep(0)
        self.wled.segment.assert_awaited_once_with(segment_id=1, on=False, transition=None)

    async def test_on_segment_keeps_immediate_updates(self):
        self.state.segments[1].on = True
        await self.entity.async_turn_on(brightness=50)
        self.hass.bus.async_fire.assert_not_called()
        self.wled.segment.assert_awaited_once_with(on=True, segment_id=1, brightness=50)

    async def test_effect_filter_does_not_modify_ids(self):
        self.assertEqual(self.entity.effect_list, ['Solid', 'Lake'])
        self.assertEqual(list(self.coordinator.data.effects), [42, 0, 7])

    async def test_single_segment_master_handling_preserved(self):
        self.coordinator.has_main_light = False
        self.state.on = False
        self.state.segments[1].on = True
        await self.entity.async_turn_on(brightness=120)
        self.gate.set()
        await real_sleep(0)
        self.wled.segment.assert_awaited_once_with(on=True, segment_id=1, brightness=255)
        self.wled.master.assert_awaited_once_with(on=True, brightness=120)

    async def test_unload_prevents_delayed_command(self):
        await self.entity.async_turn_on()
        await self.entity.async_will_remove_from_hass()
        self.gate.set()
        await real_sleep(0)
        self.wled.segment.assert_not_awaited()
