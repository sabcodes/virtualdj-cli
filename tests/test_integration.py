"""Real macOS IPC plus CLI against fake SDK callbacks. Does not open/control VirtualDJ."""
import ctypes as c
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('vdj_cli', str(ROOT / 'vdj'))
spec = importlib.util.spec_from_loader(loader.name, loader)
vdj = importlib.util.module_from_spec(spec)
loader.exec_module(vdj)


class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / 'build').mkdir(exist_ok=True)
        executable = ROOT / 'build/test-host'
        subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                        '-framework', 'CoreFoundation', '-isystem', str(ROOT / '.sdk'),
                        str(ROOT / 'tests/host.cpp'), '-o', str(executable)], check=True)
        cls.name = f'com.sabcodes.vdj-cli.test.{uuid.uuid4().hex}'
        cls.env = {**os.environ, 'VDJ_BRIDGE_PORT': cls.name}
        cls.host = subprocess.Popen([str(executable), cls.name], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
        if cls.host.stdout.readline().strip() != 'ready':
            raise RuntimeError('test host failed to start')
        cls.temp = tempfile.TemporaryDirectory()
        cls.song = Path(cls.temp.name) / 'Café track.wav'
        cls.song.write_bytes(b'test fixture, host does not decode audio')

    @classmethod
    def tearDownClass(cls):
        cls.host.terminate()
        cls.host.communicate(timeout=5)
        cls.temp.cleanup()

    def cli(self, *args, code=0, env=None):
        process = subprocess.run([str(ROOT / 'vdj'), *args], env=env or self.env,
                                 capture_output=True, text=True, timeout=8)
        self.assertEqual(process.returncode, code, process.stderr + process.stdout)
        response = json.loads(process.stdout)
        self.assertEqual(response['ok'], code == 0)
        return response

    def test_delayed_filepath_is_verified_without_resubmitting(self):
        delayed = self.song.parent / 'delayed.wav'
        delayed.write_bytes(b'fixture')
        before = self.cli('query', 'load_count')['value']
        response = self.cli('load', '--deck', '2', str(delayed))
        self.assertTrue(response['verified'])
        self.assertEqual(response['path'], str(delayed.resolve()))
        self.assertEqual(self.cli('query', 'load_count')['value'] - before, 1)

    def test_doctor_and_utf8_state(self):
        doctor = self.cli('doctor')
        self.assertEqual(doctor['version'], 'TEST HOST')
        self.assertIsNone(doctor['license'])
        self.assertEqual(doctor['license_query_error']['error'], 'sdk_rejected')
        self.cli('pause', '--deck', '1')
        self.cli('load', '--deck', '1', str(self.song))
        deck = self.cli('status', '--deck', '1')['decks'][0]
        self.assertEqual(deck['title'], 'Café "test"\ntrack')
        self.assertEqual(deck['elapsed_ms'], 1000)

    def test_guarded_loading_transport_and_automix(self):
        self.cli('pause', '--deck', '1')
        self.cli('load', '--deck', '1', str(self.song))
        self.cli('load', '--deck', '2', str(self.song))
        self.cli('play', '--deck', '1')
        self.assertIn('deck_is_playing', self.cli('load', '--deck', '1', str(self.song), code=1)['error'])
        self.cli('load', '--deck', '1', str(self.song), '--replace-playing')
        self.cli('pause', '--deck', '1')
        self.cli('automix', 'stop')
        self.assertTrue(self.cli('transition', '--beats', '8')['submitted'])
        self.cli('automix', 'start')
        self.assertTrue(self.cli('automix', 'status')['active'])
        self.cli('automix', 'next')
        self.assertIn('automix_active', self.cli('transition', code=1)['error'])
        self.cli('automix', 'stop')
        self.cli('automix', 'next', code=1)

    def test_host_rejection_and_nonfinite(self):
        for args in [('script', 'reject'), ('query', 'reject'), ('query', 'nonfinite')]:
            self.cli(*args, code=1)

    def test_invalid_arguments_and_injection(self):
        self.cli('play', '--deck', '3', code=2)
        self.cli('transition', '--beats', 'nan', code=2)
        self.cli('script', 'play\npause', code=1)
        dangerous = self.song.parent / 'song" & play & ".wav'
        dangerous.write_bytes(b'fixture')
        self.assertIn('unsupported_path_characters',
                      self.cli('load', '--deck', '1', str(dangerous), code=1)['error'])

    def test_unloaded_deck_reports_null_fields(self):
        self.cli('script', 'deck 1 unload')
        deck = self.cli('status', '--deck', '1')['decks'][0]
        self.assertFalse(deck['loaded'])
        self.assertIsNone(deck['path'])
        self.assertIsNone(deck['bpm'])
        self.assertFalse(deck['playing'])

    def test_nonfatal_ack_does_not_imply_verified_load(self):
        ignored = self.song.parent / 'ignored.wav'
        ignored.write_bytes(b'fixture')
        response = self.cli('--timeout', '0.1', 'load', '--deck', '2', str(ignored), code=1)
        self.assertIn('verification_timeout', response['error'])

    def test_unavailable_bridge(self):
        env = {**self.env, 'VDJ_BRIDGE_PORT': self.name + '.missing'}
        self.assertIn('bridge_unavailable', self.cli('doctor', env=env, code=1)['error'])

    def test_expired_mutation_never_executes(self):
        self.cli('automix', 'stop')
        previous = os.environ.get('VDJ_BRIDGE_PORT')
        os.environ['VDJ_BRIDGE_PORT'] = self.name
        bridge = vdj.Bridge()
        payload = f'{time.time() - 10}\nautomix on'.encode()
        buffer = c.create_string_buffer(payload)
        data = bridge.cf.CFDataCreate(None, buffer, len(payload))
        reply = c.c_void_p()
        try:
            result = bridge.cf.CFMessagePortSendRequest(bridge.port, 1, data, 2, 2,
                                                       bridge.mode, c.byref(reply))
            self.assertEqual(result, 0)
            response = json.loads(c.string_at(bridge.cf.CFDataGetBytePtr(reply),
                                              bridge.cf.CFDataGetLength(reply)))
            self.assertEqual(response['error'], 'request_expired')
        finally:
            if reply.value:
                bridge.cf.CFRelease(reply)
            bridge.cf.CFRelease(data)
            bridge.close()
            if previous is None:
                os.environ.pop('VDJ_BRIDGE_PORT', None)
            else:
                os.environ['VDJ_BRIDGE_PORT'] = previous
        self.assertFalse(self.cli('automix', 'status')['active'])


if __name__ == '__main__':
    unittest.main()
