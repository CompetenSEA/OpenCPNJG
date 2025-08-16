from pathlib import Path
import pytest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from convert_charts import cm93_to_s57  # noqa:E402


def test_cm93_adapter(tmp_path: Path) -> None:
    cm93 = Path(__file__).with_name('cm93_fixture.cm93')
    out = tmp_path / 'out.000'
    if not cm93.exists():
        with pytest.raises(NotImplementedError) as exc:
            cm93_to_s57(str(cm93), str(out))
        assert 'CM93 conversion requires' in str(exc.value)
        pytest.skip('CM93 fixture not available')
    cm93_to_s57(str(cm93), str(out))
    assert out.exists()
