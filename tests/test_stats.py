def test_stats_summary_endpoint(client, sample_student):
    response = client.get("/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert data["total_students"] >= 1
    assert "courses" in data
    assert "top_courses" in data
    assert "avg_age" in data


def test_stats_dashboard_html(client, sample_student):
    response = client.get("/stats/dashboard")
    assert response.status_code == 200
    assert "EduTrack Stats Dashboard" in response.text
    assert "text/html" in response.headers["content-type"]
