## Mastodon Collector Notes

This collector reads rtl_power CSV files from /tmp, discovers signal peakers, and writes schema-validated JSON files into freshDir.

### Runtime Contract

1. Input CSV path: /tmp/<base_name>.csv
2. Output JSON path: <freshDir>/<base_name>.json
3. Configuration source: config.yaml (or optional CLI path)

### Expected Config Keys

1. crateName
2. freshDir
3. equipment.hostName
4. equipment.hostType
5. geoLoc.altitude
6. geoLoc.latitude
7. geoLoc.longitude
8. geoLoc.siteName
9. receiver.antenna
10. receiver.receiverId
11. receiver.task
12. receiver.type

### Task to Mode Mapping

1. *-bs1-pk1 -> bigsearch01
2. *-wx1-pk1 -> noaa-wx01
3. otherwise -> unknown

### Testing

Run tests from this directory:

```bash
source venv/bin/activate
python -m pytest -q test_collector.py
```
