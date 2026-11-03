import json
from pathlib import Path

from app.workers.converters.csv_to_json import convert

def test_csv_to_json_writes_records(tmp_path: Path):
    input_path = tmp_path / "sample.csv"
    output_path = tmp_path / "sample.json"

    input_path.write_text("name,age\nAlice,30\nBob,25\n", encoding="utf-8")

    convert(str(input_path), str(output_path))

    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data == [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
