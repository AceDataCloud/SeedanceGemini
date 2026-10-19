#!/usr/bin/env python3
"""Native lifecycle with local model fixtures; never generates paid media.
Local-only mode also checks exact original-task argument mapping. Live mode
performs reference information or schema-only discovery, never fabricated IDs.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pexpect

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / 'tests/service_contract.json').read_text())
NAME = C['id']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cli', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--live-info', action='store_true')
args = parser.parse_args()
token = os.environ.get('ACEDATACLOUD_SERVICE_TEST_TOKEN') if args.live_info else 'local-fixture-' + secrets.token_hex(16)
if not token:
    parser.error('Export ACEDATACLOUD_SERVICE_TEST_TOKEN for a live check')
base = Path(tempfile.mkdtemp(prefix=C['prefix'] + '-gemini-'))
workspace = base / 'workspace'
workspace.mkdir()
user = base / 'user'
(user / '.gemini').mkdir(parents=True)
source = base / NAME
shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', 'artifacts', '__pycache__', 'dist'))
checks = {}
e = {'service': C['display'], 'as_of': '2026-10-18', 'model': 'localhost deterministic fixture',
     'mcp': 'hosted service information/schema only' if args.live_info else 'localhost fixture',
     'paid_requests': 0, 'checks': checks, 'commands': [], 'model_requests': [], 'mcp_calls': [],
     'native_secret_storage': 'isolated native encrypted fallback, not user keychain'}
fixture_task = 'fixture-original-task-' + secrets.token_hex(6)

class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *unused):
        pass

    def do_GET(self):
        self.send_response(405)
        self.end_headers()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        if self.path.startswith('/mcp'):
            method = body.get('method')
            if method and method.startswith('notifications/'):
                self.send_response(202)
                self.end_headers()
                return
            result = {}
            if method == 'initialize':
                result = {'protocolVersion': '2025-03-26', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'local-service-fixture', 'version': 'test-only'}}
            elif method == 'tools/list':
                result = {'tools': C['schemas'] + [{'name': 'unrelated_delete_account', 'description': 'Must be filtered', 'inputSchema': {'type': 'object', 'properties': {}}}]}
            elif method == 'tools/call':
                params = body['params']
                e['mcp_calls'].append(params)
                name = params['name']
                if name == C['reference']:
                    result = {'content': [{'type': 'text', 'text': 'LOCAL_REFERENCE ' + str(C['marker'])}]}
                elif name == C['task_tool']:
                    checks['exact_task_field'] = params.get('arguments') == {C['task_arg']: fixture_task}
                    result = {'content': [{'type': 'text', 'text': 'LOCAL_TASK_ONLY: complete; fixture media, not real generation'}]}
                else:
                    checks['unexpected_operation'] = False
                    result = {'isError': True, 'content': [{'type': 'text', 'text': 'Test forbids all generation/edit calls'}]}
            elif method == 'resources/list':
                result = {'resources': []}
            elif method == 'prompts/list':
                result = {'prompts': []}
            if method == 'tools/call' and not result.get('isError'):
                result['structuredContent'] = {'result': result['content'][0]['text']}
            checks['header_expanded'] = self.headers.get('Authorization') == 'Bearer ' + token
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'jsonrpc': '2.0', 'id': body.get('id'), 'result': result}).encode())
            return
        declarations = [d for tool in body.get('tools', []) for d in tool.get('functionDeclarations', [])]
        names = [d['name'] for d in declarations]
        responses = [p['functionResponse'] for content in body.get('contents', []) for p in content.get('parts', []) if 'functionResponse' in p]
        seen = [r['name'] for r in responses]
        raw = json.dumps(body)
        task_phase = fixture_task in raw
        reference = next((name for name in names if C['reference'] and name.endswith(C['reference'])), None)
        task_tool = next((name for name in names if name.endswith(C['task_tool'])), None)
        e['model_requests'].append({'path': self.path, 'tools': names, 'responses': seen, 'phase': 'local-task' if task_phase else 'check', 'command_loaded': (('Retrieve this existing ' + C['display'] + ' task ID:') if task_phase else ('Activate the ' + C['skill'] + ' skill.')) in raw})
        if 'activate_skill' in names and 'activate_skill' not in seen:
            part = {'functionCall': {'name': 'activate_skill', 'args': {'name': C['skill']}}}
        elif task_phase and task_tool:
            if task_tool in seen:
                checks['task_result_returned'] = 'LOCAL_TASK_ONLY' in json.dumps(responses)
                part = {'text': 'LOCAL_TASK_CHECK_OK'}
            else:
                part = {'functionCall': {'name': task_tool, 'args': {C['task_arg']: fixture_task}}}
        elif reference:
            if reference in seen:
                checks['reference_result_returned'] = str(C['marker']).lower() in json.dumps(responses).lower()
                part = {'text': 'REFERENCE_CHECK_OK'}
            else:
                part = {'functionCall': {'name': reference, 'args': {}}}
        else:
            present = all(any(name.endswith(tool) for name in names) for tool in C['tools'])
            checks['schema_visible_without_operation'] = present
            part = {'text': 'DISCOVERY_CHECK_OK: no media or task tool called.'}
        data = {'candidates': [{'content': {'role': 'model', 'parts': [part]}, 'finishReason': 'STOP', 'index': 0}], 'usageMetadata': {'promptTokenCount': 1, 'candidatesTokenCount': 1, 'totalTokenCount': 2}}
        streaming = ':streamGenerateContent' in self.path
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream' if streaming else 'application/json')
        self.end_headers()
        self.wfile.write((('data: ' + json.dumps(data) + '\n\n') if streaming else json.dumps(data)).encode())

server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
threading.Thread(target=server.serve_forever, daemon=True).start()
manifest_path = source / 'gemini-extension.json'
manifest = json.loads(manifest_path.read_text())
if not args.live_info:
    manifest['mcpServers'][NAME]['httpUrl'] = f'http://127.0.0.1:{server.server_port}/mcp'
    manifest_path.write_text(json.dumps(manifest))
(user / '.gemini/settings.json').write_text(json.dumps({'security': {'auth': {'selectedType': 'gemini-api-key'}}, 'telemetry': {'enabled': False}, 'experimental': {'extensionConfig': True}}))
(user / '.gemini/trustedFolders.json').write_text(json.dumps({str(source.resolve()): 'TRUST_FOLDER', str(workspace.resolve()): 'TRUST_FOLDER'}))
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'LANG', 'TMPDIR')}
env.update(HOME=str(user), GEMINI_CLI_HOME=str(user), GEMINI_FORCE_FILE_STORAGE='true', NO_COLOR='1', TERM='xterm-256color', GEMINI_API_KEY='localhost-model-key', GOOGLE_GEMINI_BASE_URL=f'http://127.0.0.1:{server.server_port}', GOOGLE_GENAI_API_VERSION='v1beta', GEMINI_API_KEY_AUTH_MECHANISM='bearer')
exe = ['node', str(args.cli.resolve())]

def run(command, timeout=60):
    r = subprocess.run(exe + command, env=env, cwd=workspace, text=True, capture_output=True, timeout=timeout)
    e['commands'].append({'args': command, 'exit': r.returncode, 'stdout': r.stdout.replace(token, '[REDACTED]'), 'stderr': r.stderr.replace(token, '[REDACTED]')})
    if r.returncode:
        raise RuntimeError('CLI command failed: ' + str(command) + ': ' + r.stderr[-600:])
    return r.stdout + r.stderr

try:
    e['cli_version'] = run(['--version']).strip()
    run(['extensions', 'validate', str(source)])
    command = ['extensions', 'install', str(source), '--consent']
    child = pexpect.spawn(exe[0], exe[1:] + command, env=env, cwd=str(workspace), encoding='utf-8', timeout=90, echo=False)
    child.expect(C['key_label'])
    transcript = child.before + child.after
    child.sendline(token)
    child.expect(pexpect.EOF)
    transcript += child.before
    child.close()
    e['commands'].append({'args': command, 'exit': child.exitstatus, 'transcript': transcript.replace(token, '[REDACTED]')})
    checks['native_password_prompt'] = True
    checks['installed'] = child.exitstatus == 0 and 'installed successfully' in transcript
    if not checks['installed']:
        raise RuntimeError('Installation failed: ' + transcript[-600:].replace(token, '[REDACTED]'))
    checks['listed'] = NAME in run(['extensions', 'list'])
    checks['mcp_connected'] = 'Connected' in run(['mcp', 'list'])
    checks['skill_discovered'] = C['skill'] + ' [Enabled]' in run(['skills', 'list'])
    plaintext = [str(p.relative_to(user)) for p in user.rglob('*') if p.is_file() and token.encode() in p.read_bytes()]
    checks['no_plaintext_secret'] = not plaintext
    e['plaintext_files'] = plaintext
    command = ['-m', 'gemini-3.5-flash-lite', '-p', '/' + C['prefix'] + '-check', '--approval-mode', 'yolo', '--output-format', 'json']
    result = run(command, 90)
    checks['check_result_visible'] = ('REFERENCE_CHECK_OK' if C['reference'] else 'DISCOVERY_CHECK_OK') in result
    checks['skill_activated'] = any('activate_skill' in r['responses'] for r in e['model_requests'])
    checks['command_resolved'] = any(r['command_loaded'] for r in e['model_requests'])
    checks['only_allowlisted_tools'] = bool(e['model_requests']) and all(not any(name.endswith('unrelated_delete_account') for name in r['tools']) for r in e['model_requests'])
    if not args.live_info:
        run(['-m', 'gemini-3.5-flash-lite', '-p', '/' + C['prefix'] + '-task ' + fixture_task, '--approval-mode', 'yolo', '--output-format', 'json'], 90)
        checks['only_reference_and_fixture_task_called'] = all(call['name'] in [C['reference'], C['task_tool']] for call in e['mcp_calls'])
    run(['extensions', 'uninstall', NAME])
    checks['uninstalled'] = NAME not in run(['extensions', 'list'])
    e['status'] = 'PASS' if all(checks.values()) else 'FAIL'
except Exception as error:
    e['status'] = 'FAIL'
    e['error'] = str(error).replace(token, '[REDACTED]')
finally:
    server.shutdown()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(e, ensure_ascii=False, indent=2).replace(token, '[REDACTED]') + '\n')
print(json.dumps({k: e.get(k) for k in ('service', 'status', 'cli_version', 'checks', 'error')}, indent=2))
raise SystemExit(0 if e['status'] == 'PASS' else 1)
