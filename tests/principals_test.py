from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core import db
from tests.conftest import h_principal


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


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


def test_get_staff(client, h_principal):
    """
    added test to fetch the list of teachers for the principal.
    """
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200
    
    data = response.json['data']
    assert isinstance(data, list)

    for teacher in data:
        assert 'id' in teacher
        assert 'user_id' in teacher
        assert 'created_at' in teacher
        assert 'updated_at' in teacher


def test_ungraded_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': new_ungraded_assignment(),
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 400