"""Authorized Llama download: HF small files, ModelScope weights, pinned checks."""
import argparse
import json
import os
from pathlib import Path
import time
from download_qwen import file_matches


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    root, kit = Path(os.environ['EXP_ROOT']), Path(os.environ['KIT'])
    spec = json.loads((kit / 'models.json').read_text())['llama']
    manifest = json.loads((here / 'llama-pinned-manifest.json').read_text())
    assert (manifest['repo'], manifest['revision']) == (spec['repo'], spec['revision'])
    target = root / 'models' / spec['directory']
    target.mkdir(parents=True, exist_ok=True)
    marker = target / 'experiment_download.json'
    def invalidate_marker():
        if marker.exists():
            marker.replace(target / f'experiment_download.unverified-{time.time_ns()}.json')
    if not args.verify_only:
        from huggingface_hub import get_hf_file_metadata, hf_hub_url, hf_hub_download
        from huggingface_hub.errors import GatedRepoError, LocalTokenNotFoundError
        print('Checking authorized HF access to the pinned Llama config...', flush=True)
        try:
            get_hf_file_metadata(hf_hub_url(spec['repo'], 'config.json', revision=spec['revision']),
                                 token=True, timeout=60)
        except (GatedRepoError, LocalTokenNotFoundError) as exc:
            raise SystemExit('Llama access not confirmed. Configure a read token from an approved '
                             'account for Llama-3.1-8B-Instruct, then retry. No mirror weights '
                             'were requested. Error type: ' + type(exc).__name__)
        print('HF file access confirmed.', flush=True)
        if marker.exists() and any(not file_matches(target / f['name'], f) for f in manifest['files']):
            invalidate_marker()
        for item in manifest['files']:
            if item['name'].endswith('.safetensors') or file_matches(target / item['name'], item):
                continue
            print('Fetching authorized pinned small file:', item['name'], flush=True)
            hf_hub_download(spec['repo'], item['name'], revision=spec['revision'],
                            local_dir=str(target), token=True, etag_timeout=60)
            assert file_matches(target / item['name'], item), 'Small-file checksum mismatch: '+item['name']
        needed = [f['name'] for f in manifest['files'] if f['name'].endswith('.safetensors')
                  and not file_matches(target / f['name'], f)]
        if needed:
            from modelscope.hub.snapshot_download import snapshot_download
            print('Fetching weights from ModelScope:', manifest['modelscope_repo'], flush=True)
            snapshot_download(model_id=manifest['modelscope_repo'], revision='master',
                local_dir=str(target), cache_dir=str(root / 'cache' / 'modelscope'),
                allow_patterns=needed, max_workers=1)
    checked = []
    for item in manifest['files']:
        print('Verifying:', item['name'], flush=True)
        if not file_matches(target / item['name'], item):
            invalidate_marker()
            raise RuntimeError(item['name']+': missing or differs from pinned HF snapshot. Do not start inference.')
        checked.append(item['name'])
    temp = marker.with_suffix('.tmp')
    temp.write_text(json.dumps(spec, indent=2)); temp.replace(marker)
    (target / 'download_provenance.json').write_text(json.dumps({
        'verified_against_hf_revision': spec['revision'], 'checked_files': checked,
        'mode': 'verify_only_source_unspecified' if args.verify_only else 'authorized_HF_small_files_ModelScope_weights',
        'modelscope_repo': manifest['modelscope_repo'],
        'modelscope_requested_revision': None if args.verify_only else 'master',
        'tensor_execution_performed': False}, indent=2))
    print('Completed llama: all required files match the pinned HF snapshot.', flush=True)


if __name__ == '__main__':
    main()
