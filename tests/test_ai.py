def test_ai_status(client):
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_online" in data
    assert "recommended_model" in data


def test_ai_ask_when_empty_db(client):
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert data["records_consulted"] == 0
    assert "no student records" in data["answer"].lower()


def test_ai_ask_count_question(client, sample_student):
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert data["records_consulted"] >= 1
    assert "1" in data["answer"] or "student" in data["answer"].lower()


def test_ai_ask_born_after_question(client, sample_student):
    # sample_student was born in 2003
    response = client.post("/ai/ask", json={"question": "List students born after 2000"})
    assert response.status_code == 200
    data = response.json()
    assert "Augasta Gloriya" in data["answer"]


def test_ai_ask_youngest_question(client, sample_student):
    response = client.post("/ai/ask", json={"question": "Who is the youngest student?"})
    assert response.status_code == 200
    data = response.json()
    assert "Augasta Gloriya" in data["answer"]
