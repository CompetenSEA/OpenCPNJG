import json
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import dict_builder


def test_build_from_schema(tmp_path: Path) -> None:
    schema = {
        'objects': [
            {'id': 99, 'objl': 'FOO', 'label': ['BAR']},
        ],
        'lights': {'123': 'abc'},
    }
    schema_path = tmp_path / 'schema.yml'
    schema_path.write_text(yaml.safe_dump(schema), encoding='utf-8')
    out = tmp_path / 'dict.json'
    dict_builder.build(output=out, schema=schema_path)
    data = json.loads(out.read_text())
    assert data['objects']['99']['name'] == 'FOO'
    assert data['objects']['99']['label'] == ['BAR']
    assert data['lights']['123'] == 'abc'
