import importlib.util
import json
from pathlib import Path
import re
import tarfile
import tempfile
import tomllib
import unittest
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / 'tests/service_contract.json').read_text())

class ExtensionContractTests(unittest.TestCase):
    def setUp(self):
        self.m = json.loads((ROOT / 'gemini-extension.json').read_text())

    def test_native_sensitive_secret_only_goes_to_own_server(self):
        self.assertEqual(self.m['name'], C['id'])
        self.assertEqual(len(self.m['settings']), 1)
        setting = self.m['settings'][0]
        self.assertTrue(setting['sensitive'])
        self.assertEqual(setting['envVar'], C['secret'])
        self.assertEqual(list(self.m['mcpServers']), [C['id']])
        server = self.m['mcpServers'][C['id']]
        self.assertEqual(server['httpUrl'], C['endpoint'])
        self.assertEqual(server['headers'], {'Authorization': 'Bearer ${' + C['secret'] + '}'})
        self.assertNotIn('trust', server)
        self.assertNotIn('hooks', self.m)
        self.assertNotIn('command', server)

    def test_live_schema_allowlist_and_exact_task_parameter(self):
        tools = self.m['mcpServers'][C['id']]['includeTools']
        self.assertEqual(tools, C['tools'])
        self.assertEqual(len(tools), len(set(tools)))
        schema = {t['name']: t['inputSchema'] for t in C['schemas']}
        self.assertEqual(set(tools), set(schema))
        self.assertIn(C['task_arg'], schema[C['task_tool']]['properties'])
        if C['repo'] == 'GPTImageGemini':
            self.assertNotIn('task_id', schema[C['task_tool']]['properties'])
            self.assertIn('image', schema['openai_edit_image']['properties'])
            self.assertNotIn('image_urls', schema['openai_edit_image']['properties'])
            self.assertFalse(any('chat' in t or 'speech' in t or 'embedding' in t for t in tools))
        if C['repo'] == 'NanoBananaGemini':
            self.assertIsNone(C['reference'])
            self.assertIn('image_urls', schema['nanobanana_edit_image']['properties'])

    def test_commands_parse_and_task_uses_argument_as_data(self):
        commands = {p.stem: tomllib.loads(p.read_text()) for p in (ROOT / 'commands').glob('*.toml')}
        self.assertEqual(set(commands), {C['prefix'] + '-check', C['prefix'] + '-task'})
        task = commands[C['prefix'] + '-task']['prompt']
        self.assertIn('{{args}}', task)
        self.assertIn(C['task_tool'], task)
        self.assertIn(C['task_arg'], task)
        self.assertNotIn('!{', str(commands))

    def test_archive_has_root_manifest_and_attributed_assets(self):
        spec = importlib.util.spec_from_file_location('package_extension', ROOT / 'scripts/package_extension.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            output = module.build(Path(folder) / 'extension.tar.gz')
            with tarfile.open(output) as archive:
                names = archive.getnames()
                self.assertIn('gemini-extension.json', names)
                self.assertIn('skills/' + C['skill'] + '/SKILL.md', names)
                self.assertIn('THIRD_PARTY_NOTICES.md', names)
                self.assertIn('_assets/tutorial/GEMINI-APACHE-LICENSE.txt', names)
                self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in names))
                self.assertFalse(any('.env' in Path(n).parts or '.git' in Path(n).parts for n in names))
                self.assertFalse(any(m.issym() or m.islnk() for m in archive.getmembers()))

    def test_readme_relative_links_and_four_utm_ctas(self):
        for document in (ROOT / 'README.md', ROOT / 'readme/README_zh_Hans.md'):
            for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
                if target.startswith('https://platform.acedata.cloud'):
                    query = parse_qs(urlsplit(target).query)
                    self.assertTrue({'utm_source', 'utm_medium', 'utm_campaign', 'utm_content'} <= query.keys(), target)
                    self.assertEqual(query['utm_source'], ['gemini-cli'])
                    self.assertTrue(all(re.fullmatch(r'[a-z0-9][a-z0-9_.-]{0,95}', query[k][0]) for k in ('utm_source','utm_medium','utm_campaign','utm_content')))
                elif not urlsplit(target).scheme and not target.startswith('#'):
                    self.assertTrue((document.parent / target.split('#', 1)[0]).is_file(), target)

if __name__ == '__main__':
    unittest.main()
