from core import db
from core.models.assignments import Assignment, AssignmentStateEnum


def new_ungraded_assignment(teacher_id: int = 3) -> int:
    """
    Creates an ungraded assignment for a specified teacher and returns the id of the assignment.

    Parameters:
    - teacher_id (int): The ID of the teacher for whom the assignments are created.

    Returns:
    - assignment.id(int): the id of the assignment generated
    """

    # Create ungraded assignment
    grade = None

    # Create a new Assignment instance
    assignment = Assignment(
        teacher_id=teacher_id,
        student_id=3,
        grade=grade,
        content='test content',
        state=AssignmentStateEnum.SUBMITTED,
    )

    # Add the assignment to the database session
    db.session.add(assignment)

    # Commit changes to the database
    db.session.commit()

    return assignment.id


def get_submitted_assignment_id(teacher_id: int = 3):
    """
    Fetches the ID of the first assignment with a given teacher_id
    and a state of 'SUBMITTED'.

    Parameters:
    - teacher_id (int): The ID of the teacher whose assignments we are querying.

    Returns:
    - assignment.id (int): The ID of the matching assignment, or None if no match is found.
    """
    # Query the first assignment that matches the teacher_id and state
    assignment = Assignment.query.filter_by(
        teacher_id=teacher_id, 
        state=AssignmentStateEnum.GRADED
    ).first()
    print(f"assignment value:{assignment.id}")

    # Return the assignment ID if found, else return None
    return assignment.id if assignment else None


def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_success(client, h_teacher_3):
    """
    tests whether submitted assignments are graded successfully
    """
    
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_3
        , json={
            "id": new_ungraded_assignment(3),
            "grade": "A"
        }
    )
    assert response.status_code == 200


def test_teacher_regrade(client, h_teacher_3):
    """
    tests whether submitted assignments can be regraded
    """
    
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_3
        , json={
            "id": get_submitted_assignment_id(),
            "grade": "A"
        }
    )
    assert response.status_code == 400