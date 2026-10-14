from datetime import date


def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "EduTrack" in response.text
    assert "text/html" in response.headers["content-type"]


def test_create_student_success(client):
    payload = {
        "name": "Aarav Sharma",
        "date_of_birth": "2004-06-15",
        "email": "aarav.sharma@example.com",
        "phone": "+91 9123456789",
        "course": "B.Tech Information Technology",
        "address": "Bangalore, Karnataka",
        "enrollment_date": "2023-07-10",
    }
    response = client.post("/students/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Aarav Sharma"
    assert data["email"] == "aarav.sharma@example.com"
    assert "id" in data
    assert data["id"] > 0


def test_create_student_duplicate_email(client, sample_student):
    payload = {
        "name": "Duplicate User",
        "date_of_birth": "2003-05-20",
        "email": sample_student.email,  # duplicate
        "phone": "+91 9876543210",
        "course": "CSE",
    }
    response = client.post("/students/", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_student_future_dob_validation(client):
    payload = {
        "name": "Time Traveler",
        "date_of_birth": "2099-01-01",  # future date
        "email": "future@example.com",
    }
    response = client.post("/students/", json=payload)
    assert response.status_code == 422


def test_create_student_blank_name_validation(client):
    payload = {
        "name": "   ",
        "date_of_birth": "2002-01-01",
        "email": "test@example.com",
    }
    response = client.post("/students/", json=payload)
    assert response.status_code == 422


def test_list_students(client, sample_student):
    response = client.get("/students/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_student.name


def test_list_students_filter_by_course(client, sample_student):
    response = client.get("/students/?course=Computer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Computer" in data[0]["course"]

    # Filter with non-matching course
    response_empty = client.get("/students/?course=CivilEngineering")
    assert response_empty.status_code == 200
    assert len(response_empty.json()) == 0


def test_list_students_filter_by_name(client, sample_student):
    response = client.get("/students/?name=Augasta")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == sample_student.name


def test_list_students_filter_by_dob(client, sample_student):
    # DOB is 2003-05-20
    response = client.get("/students/?dob_after=2000-01-01")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response_none = client.get("/students/?dob_after=2025-01-01")
    assert response_none.status_code == 200
    assert len(response_none.json()) == 0


def test_get_single_student_success(client, sample_student):
    response = client.get(f"/students/{sample_student.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_student.id
    assert data["email"] == sample_student.email


def test_get_single_student_not_found(client):
    response = client.get("/students/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_replace_student_put(client, sample_student):
    update_payload = {
        "name": "Augasta Gloriya Updated",
        "date_of_birth": "2003-05-20",
        "email": "augasta.updated@example.com",
        "phone": "+91 9999988888",
        "course": "AI & ML",
        "address": "Coimbatore, Tamil Nadu",
        "enrollment_date": "2022-08-01",
    }
    response = client.put(f"/students/{sample_student.id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Augasta Gloriya Updated"
    assert data["course"] == "AI & ML"
    assert data["email"] == "augasta.updated@example.com"


def test_patch_student_partial(client, sample_student):
    patch_payload = {
        "course": "Cyber Security",
    }
    response = client.patch(f"/students/{sample_student.id}", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["course"] == "Cyber Security"
    # Unchanged fields persist
    assert data["name"] == sample_student.name
    assert data["email"] == sample_student.email


def test_delete_student(client, sample_student):
    response = client.delete(f"/students/{sample_student.id}")
    assert response.status_code == 204

    # Verify it is deleted
    get_res = client.get(f"/students/{sample_student.id}")
    assert get_res.status_code == 404


def test_delete_student_not_found(client):
    response = client.delete("/students/999999")
    assert response.status_code == 404
