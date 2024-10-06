from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.teachers import Teacher

from .schema import StaffSchema
principal_staff_resources = Blueprint('principal_staff_resources', __name__)


@principal_staff_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of teachers"""
    principals_staff = Teacher.query.all()
    principals_staff_dump = StaffSchema().dump(principals_staff, many=True)
    return APIResponse.respond(data=principals_staff_dump)
