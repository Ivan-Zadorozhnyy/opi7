import json
from datetime import datetime, timedelta
from main import calculate_daily_average


def test_get_report(client):
    # Setup
    report_name = 'daily_usage'
    date_from = (datetime.now() - timedelta(days=7)).date().isoformat()
    date_to = datetime.now().date().isoformat()

    response = client.get(f"/api/report/{report_name}?from={date_from}&to={date_to}")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'dailyAverage' in data
    assert isinstance(data['dailyAverage'], float)
    assert 'users' in data
    assert isinstance(data['users'], list)


def test_calculate_daily_average():
    assert calculate_daily_average(1800, 2) == 900
    assert calculate_daily_average(86400, 1) == 86400
    assert calculate_daily_average(0, 10) == 0
    assert calculate_daily_average(5000, 0) == 0
