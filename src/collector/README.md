## Collector Blueprint For Other Projects

This collector is based on the same structure as slug and keeps the same config-first
pipeline contract while adding mastodon-specific peaker extraction from rtl_power
CSV files.

### Core Design

1. Uses Pydantic models to define payload sections: equipment, geoLoc, job, and timeStamp.
2. Uses an abstract collector interface (`get_peakers`, `execute`) to standardize implementation.
3. Reads runtime configuration from YAML (`config.yaml` by default).
4. Reads `/tmp/<base_name>.csv`, discovers peakers, and writes one JSON file to `freshDir`.
5. Preserves schema validation through `JsonHelper` before writing output.

### Execution Flow

1. Load YAML config.
2. Instantiate typed model objects from config fields.
3. Derive job metadata (`mode`, `project`, `task`) from receiver task suffix.
4. Parse CSV and discover peakers.
5. Build mastodon payload model.
6. Serialize validated JSON to `<freshDir>/<base_name>.json`.

### Required Configuration Contract

The collector expects these keys in `config.yaml`:

1. `crateName`
2. `freshDir`
3. `equipment.hostName`
4. `equipment.hostType`
5. `geoLoc.altitude`
6. `geoLoc.latitude`
7. `geoLoc.longitude`
8. `geoLoc.siteName`
9. `receiver.antenna`
10. `receiver.receiverId`
11. `receiver.task`
12. `receiver.type`

### Task to Mode Mapping

1. `*-bs1-pk1` -> `bigsearch01`
2. `*-wx1-pk1` -> `noaa-wx01`
3. otherwise -> `unknown`

### Testing With Pytest

Run tests from this directory:

```bash
source venv/bin/activate
python -m pytest -q test_collector.py
```
