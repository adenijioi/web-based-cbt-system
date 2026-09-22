import io
import os
import sys

import pytest
from openpyxl import Workbook

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import Attempt, Course, Question, create_app, db


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-secret",
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture()
def client(app, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "testing-password")
    return app.test_client()


def token(client):
    client.get("/")
    with client.session_transaction() as sess:
        return sess["csrf_token"]


def login(client):
    return client.post("/admin/login", data={
        "csrf_token": token(client), "username": "admin", "password": "testing-password"
    }, follow_redirects=True)


def question_workbook(count=25):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Mark"])
    for i in range(count):
        sheet.append([f"Question {i}?", f"Answer {i}", f"Wrong B {i}", f"Wrong C {i}", f"Wrong D {i}", "A", 1])
    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return stream


def create_ready_course(app):
    with app.app_context():
        course = Course(title="Introduction to Python", code="CPT 101", is_active=True)
        db.session.add(course)
        db.session.flush()
        for i in range(25):
            db.session.add(Question(course_id=course.id, text=f"Question {i}?",
                                    options_json=f'["Answer {i}", "B{i}", "C{i}", "D{i}"]',
                                    correct_answer=f"Answer {i}", mark=1))
        db.session.commit()
        return course.id


def test_home_and_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json == {"status": "ok"}


def test_admin_login_and_create_course(client):
    response = login(client)
    assert b"Assessment dashboard" in response.data
    response = client.post("/admin/courses/create", data={
        "csrf_token": token(client), "title": "Data Structures", "code": "COM 202"
    }, follow_redirects=True)
    assert b"COM 202" in response.data


def test_excel_upload_and_activation(client, app):
    login(client)
    with app.app_context():
        course = Course(title="Programming", code="CPT 111")
        db.session.add(course)
        db.session.commit()
        course_id = course.id
    response = client.post(f"/admin/courses/{course_id}/upload", data={
        "csrf_token": token(client), "question_file": (question_workbook(), "questions.xlsx")
    }, content_type="multipart/form-data", follow_redirects=True)
    assert b"25 questions imported successfully" in response.data
    response = client.post(f"/admin/courses/{course_id}/toggle", data={"csrf_token": token(client)}, follow_redirects=True)
    assert b"Test activated" in response.data


def test_student_attempt_marking_and_duplicate_prevention(client, app):
    create_ready_course(app)
    response = client.post("/access-test", data={"csrf_token": token(client), "course_code": "CPT 101"})
    assert response.status_code == 302
    details = {"csrf_token": token(client), "full_name": "Test Student", "matric_number": "MAT/001",
               "phone_number": "08000000000", "email": "student@example.com", "exam_number": "EXAM/001"}
    response = client.post("/test/CPT%20101/details", data=details, follow_redirects=True)
    assert b"TIME REMAINING" in response.data
    with app.app_context():
        attempt = Attempt.query.one()
        public_id = attempt.public_id
        question_ids = __import__("json").loads(attempt.question_order_json)
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        answer_data = {f"question_{q.id}": q.correct_answer for q in questions}
    answer_data["csrf_token"] = token(client)
    response = client.post(f"/attempt/{public_id}/submit", data=answer_data, follow_redirects=True)
    assert b"100%" in response.data
    with client.session_transaction() as sess:
        sess.pop("attempt_public_id", None)
    response = client.post("/test/CPT%20101/details", data=details, follow_redirects=True)
    assert b"attempt already exists" in response.data


def test_result_excel_export(client, app):
    course_id = create_ready_course(app)
    login(client)
    response = client.get(f"/admin/courses/{course_id}/results.xlsx")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/vnd.openxmlformats")
