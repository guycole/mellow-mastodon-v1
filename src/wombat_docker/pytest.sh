#
# Title: pytest.sh
# Description: invoke pytest for mastodon app and validator
#
source venv/bin/activate
python -m pytest -q test_mastodon_app.py test_validator.py
#
