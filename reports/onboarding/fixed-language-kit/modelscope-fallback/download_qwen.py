"""Download public Qwen weights via ModelScope; verify pinned HF file identities.

Run with a separate downloader venv. No HF token is sent to ModelScope.
Small config/tokenizer files are fetched from the pinned public HF revision.
This helper does not modify the project source or experiment dependencies.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def file_matches(path, spec):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != spec['size']:
        return False
    h = hashlib.sha256() if spec['algorithm'] == 'sha256' else hashlib.sha1()
    if spec['algorithm'] == 'git-blob-sha1':
        h.update(f'blob {spec["size"]}\0'.encode())
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest() == spec['digest']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    root = Path(os.environ['EXP_ROOT'])
    kit = Path(os.environ['KIT'])
    spec = json.loads((kit / 'models.json').read_text())['qwen']
    manifest = json.loads((here / 'qwen-pinned-manifest.json').read_text())
    assert (manifest['repo'], manifest['revision']) == (spec['repo'], spec['revision'])
    target = root / 'models' / spec['directory']
    target.mkdir(parents=True, exist_ok=True)
    files = manifest['files']
    marker = target / 'experiment_download.json'
    def invalidate_marker():
        if marker.exists():
            marker.replace(target / f'experiment_download.unverified-{time.time_ns()}.json')
    if not args.verify_only:
        if marker.exists() and any(not file_matches(target / f['name'], f) for f in files):
            invalidate_marker()
        # Preserve already verified HF files. No metadata HEAD request is needed.
        for item in files:
            if item['name'].endswith('.safetensors') or file_matches(target / item['name'], item):
                continue
            url = f'https://huggingface.co/{spec["repo"]}/resolve/{spec["revision"]}/{item["name"]}'
            part = target / (item['name'] + '.pinned.part')
            print('Fetching pinned small file:', item['name'], flush=True)
            subprocess.run(['curl', '-fL', '--connect-timeout', '15', '--max-time', '300',
                '--retry', '3', '--retry-delay', '3', '-o', str(part), url], check=True)
            assert file_matches(part, item), f'Pinned small-file checksum mismatch: {item["name"]}'
            part.replace(target / item['name'])
        needed = [item['name'] for item in files if item['name'].endswith('.safetensors')
                  and not file_matches(target / item['name'], item)]
        if needed:
            from modelscope.hub.snapshot_download import snapshot_download
            print('Fetching weights from ModelScope:', needed, flush=True)
            snapshot_download(model_id=spec['repo'], revision='master', local_dir=str(target),
                cache_dir=str(root / 'cache' / 'modelscope'), allow_patterns=needed, max_workers=1)
    checked = []
    for item in files:
        print('Verifying:', item['name'], flush=True)
        if not file_matches(target / item['name'], item):
            invalidate_marker()
            raise RuntimeError(f'{item["name"]}: missing or differs from pinned HF snapshot. '
                               'Do not mark this model ready; inspect the source/version first.')
        checked.append(item['name'])
    # The HF identity marker is written ONLY after all required file bytes match.
    tmp = marker.with_suffix('.tmp')
    tmp.write_text(json.dumps(spec, indent=2))
    tmp.replace(marker)
    provenance = {'verified_against_hf_revision': manifest['revision'], 'checked_files': checked,
        'mode': 'verify_only_source_unspecified' if args.verify_only else 'ModelScope_weights_HF_pinned_small_files',
        'modelscope_requested_revision': None if args.verify_only else 'master',
        'tensor_execution_performed': False}
    (target / 'download_provenance.json').write_text(json.dumps(provenance, indent=2))
    print('Completed qwen: all required files match the pinned HF snapshot.', flush=True)


if __name__ == '__main__':
    main()
