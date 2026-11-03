import asyncio
import importlib
import io
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
pkg = types.ModuleType('cute_status')
pkg.__path__ = [str(ROOT)]
sys.modules['cute_status'] = pkg
config = importlib.import_module('cute_status.config')
status = importlib.import_module('cute_status.status')
renderer = importlib.import_module('cute_status.renderer')


def sample():
    return status.Snapshot(23.5, 4, 2.8, status.Resource(3.2, 8, 40),
        status.Resource(0, 0, 0), status.Resource(40, 100, 40),
        'Linux 6.8', 'Example CPU', 93600, 180000, 12, '2026-11-03 12:00:00 CST')


class CoreTests(unittest.TestCase):
    def test_config_validation(self):
        self.assertEqual(config.Settings.parse({}).nickname, 'AstrBot')
        for raw in ({'cooldown': -1}, {'cooldown': float('nan')},
                    {'only_admin': 'false'}, {'disk_path': ''}):
            with self.assertRaises(ValueError):
                config.Settings.parse(raw)

    def test_duration(self):
        self.assertEqual(status.format_uptime(93600), '1d 02h 00m')
        self.assertEqual(status.format_uptime(-1), '0d 00h 00m')

    def test_cpu_without_frequency_and_cores(self):
        memory = NS(used=0, total=0, percent=0)
        with patch.object(status.psutil, 'cpu_freq', return_value=None), \
             patch.object(status.psutil, 'cpu_count', return_value=None), \
             patch.object(status.psutil, 'cpu_percent', return_value=0), \
             patch.object(status.psutil, 'swap_memory', return_value=memory):
            data = status.collect(str(ROOT), 0)
        self.assertIsNone(data.frequency)
        self.assertEqual(data.cores, 1)
        self.assertEqual(data.swap.total, 0)

    def test_png_and_no_swap(self):
        from PIL import Image
        data = sample()
        for nickname in ('AstrBot', '可爱的状态机器人'*15):
            png = renderer.render(data, nickname)
            with Image.open(io.BytesIO(png)) as img:
                self.assertEqual(img.size, (1000, 1340))
                self.assertEqual(img.format, 'PNG')

    def test_real_collect(self):
        data = status.collect(str(ROOT), 1)
        self.assertGreater(data.ram.total, 0)
        self.assertTrue(0 <= data.cpu_percent <= 100)


# SDK boundary doubles test our handler logic, not the AstrBot dispatcher.
class At:
    def __init__(self, qq): self.qq = qq


class Event:
    def __init__(self, admin=False, private=False, at=False):
        self.admin, self.private, self.at = admin, private, at
        self.stopped = False
    def is_admin(self): return self.admin
    def is_private_chat(self): return self.private
    def get_self_id(self): return '123'
    def get_messages(self): return [At('123')] if self.at else []
    def stop_event(self): self.stopped = True
    def plain_result(self, text): return text
    def chain_result(self, chain): return chain


def load_main():
    modules = {}
    for name in ('astrbot', 'astrbot.api', 'astrbot.api.event',
                 'astrbot.api.message_components', 'astrbot.api.star'):
        modules[name] = types.ModuleType(name)
    modules['astrbot.api'].AstrBotConfig = dict
    modules['astrbot.api'].logger = NS(exception=lambda *a: None)
    modules['astrbot.api.event'].AstrMessageEvent = Event
    def command(name, alias):
        def decorate(fn):
            fn.commands = {name} | alias
            return fn
        return decorate
    modules['astrbot.api.event'].filter = NS(command=command)
    modules['astrbot.api.message_components'].At = At
    modules['astrbot.api.message_components'].Image = NS(fromBytes=lambda data: data)
    class Star:
        def __init__(self, context): self.context = context
    modules['astrbot.api.star'].Star = Star
    modules['astrbot.api.star'].Context = object
    modules['astrbot.api.star'].register = lambda *a: lambda cls: cls
    with patch.dict(sys.modules, modules):
        return importlib.import_module('cute_status.main')


main = load_main()


class HandlerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Keep tests deterministic at the worker boundary; real collection and
        # rendering are exercised separately by CoreTests.
        async def inline_worker(fn, *args):
            return fn(*args)
        self.worker_patch = patch.object(main.asyncio, 'to_thread', side_effect=inline_worker)
        self.worker_patch.start()
        self.addCleanup(self.worker_patch.stop)

    def plugin(self, **cfg):
        return main.CuteStatusPlugin(NS(get_all_stars=lambda: [NS(activated=True)]), cfg)

    async def invoke(self, plugin, event=None):
        async def run():
            return [x async for x in plugin.status(event or Event())]
        return await asyncio.wait_for(run(), timeout=5)

    async def test_aliases(self):
        self.assertEqual(main.CuteStatusPlugin.status.commands, {'status', '状态', '运行状态'})

    async def test_permissions(self):
        plugin = self.plugin(only_admin=True)
        with patch.object(plugin, '_build') as build:
            self.assertIn('管理员', (await self.invoke(plugin))[0])
            build.assert_not_called()

    async def test_at_required(self):
        plugin = self.plugin(to_me=True)
        with patch.object(plugin, '_build', return_value=b'png'):
            self.assertIn('@机器人', (await self.invoke(plugin))[0])
            self.assertEqual(await self.invoke(plugin, Event(at=True)), [[b'png']])
        plugin = self.plugin(to_me=True)
        with patch.object(plugin, '_build', return_value=b'png'):
            self.assertEqual(await self.invoke(plugin, Event(private=True)), [[b'png']])

    async def test_cooldown(self):
        plugin = self.plugin()
        with patch.object(plugin, '_build', return_value=b'png') as build:
            self.assertEqual(await self.invoke(plugin), [[b'png']])
            self.assertIn('冷却', (await self.invoke(plugin))[0])
            self.assertEqual(build.call_count, 1)

    async def test_busy(self):
        plugin = self.plugin()
        async with plugin._lock:
            self.assertIn('正在绘制', (await self.invoke(plugin))[0])

    async def test_collection_failure_does_not_consume_cooldown(self):
        plugin = self.plugin()
        with patch.object(plugin, '_build', side_effect=OSError('bad path')):
            self.assertIn('采集失败', (await self.invoke(plugin))[0])
            self.assertIsNone(plugin._last_success)

    async def test_render_fallback(self):
        plugin = self.plugin(font_path='/missing-font.otf')
        with patch.object(main, 'collect', return_value=sample()):
            result = await self.invoke(plugin)
        self.assertIn('CPU:', result[0])
        self.assertIn('SWAP: 0.00 / 0.00', result[0])

    async def test_cancel_does_not_allow_overlapping_workers(self):
        plugin = self.plugin(cooldown=0)
        gate, started = asyncio.Event(), asyncio.Event()
        async def delayed_worker(fn, *args):
            started.set()
            await gate.wait()
            return b'png'
        with patch.object(main.asyncio, 'to_thread', side_effect=delayed_worker):
            task = asyncio.create_task(self.invoke(plugin))
            await started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertIn('正在绘制', (await self.invoke(plugin))[0])
            gate.set()
            await plugin.terminate()



if __name__ == '__main__':
    unittest.main()
