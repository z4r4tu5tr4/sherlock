"""Sherlock Project Controllers and Routes."""
from flask import Blueprint, request, g, jsonify, abort, make_response

from sherlock import db, auth
from sherlock.data.model import Project, Scenario, Cycle, CycleHistory
from sherlock.data.model import ProjectSchema
from sherlock.helpers.util import count_cycle_stats
from sherlock.helpers.util import load_cycle_history, get_last_cycle
from sherlock.helpers.string_operations import check_none_and_blank

project = Blueprint('projects', __name__)


@project.url_value_preprocessor
@auth.login_required
def get_project(endpoint, values):
    """Blueprint Object Query."""
    if 'project_id' in values:
        project_id = values.pop('project_id')
        g.project = Project.query.filter_by(id=project_id).first()

        if g.project is None:
            abort(make_response(jsonify(message='PROJECT_NOT_FOUND'), 400))


@project.route('/show/<int:project_id>', methods=['GET'])
@auth.login_required
def get_project_details():
    """Show Project Details."""
    schema = ProjectSchema(many=False)
    project = schema.dump(g.project).data
    return make_response(jsonify(project))


@project.route('/show_cycle_details/<int:project_id>', methods=['GET'])
@auth.login_required
def get_project_last_cycle():
    project_cycle = get_last_cycle(Cycle, g.project.id)

    if project_cycle is not None:
        current_c_history = load_cycle_history(project_cycle, CycleHistory)
        current_c_stats = count_cycle_stats(current_c_history)
        return make_response(jsonify(get_cycle="YES",
                                     current_c_stats))
    else:
        return make_response(jsonify(get_cycle="NO"))


@project.route('/new', methods=['POST'])
@auth.login_required
def new():
    """POST endpoint for new projects.

    Param:
         { name: required,
           is_private: required (boolean),
           owner: required,
           type_of_project: required
         }
    """
    project_name = request.json.get('project_name')
    is_private = request.json.get('is_private')
    project_owner = request.json.get('project_owner')
    type_of_project = request.json.get('type_of_project')

    check_none_and_blank(project_name, 'project_name')
    check_none_and_blank(is_private, 'is_private')
    check_none_and_blank(project_owner, 'project_owner')
    check_none_and_blank(type_of_project, 'type_of_project')

    new_project = Project(name=project_name,
                          is_private=is_private,
                          owner=project_owner,
                          type_of_project=type_of_project)
    db.session.add(new_project)
    db.session.commit()

    return make_response(jsonify(message='PROJECT_CREATED'))


@project.route('/edit/<int:project_id>', methods=[ 'POST'])
@auth.login_required
def edit():
    """POST endpoint for editing existing users.

    Param:
         { name: not required,
           is_private: not required (boolean),
           owner: not required,
           type_of_project: not required
         }
    """
    edited_project = g.project

    project_name = request.json.get('project_name')
    is_private = request.json.get('is_private')
    project_owner = request.json.get('project_owner')
    type_of_project = request.json.get('type_of_project')

    if project_name:
        check_none_and_blank(project_name, 'project_name')
        edited_project.name = project_name

    if is_private:
        check_none_and_blank(is_private, 'is_private')
        edited_project.is_private = is_private

    if project_owner:
        check_none_and_blank(project_owner, 'project_owner')
        edited_project.owner = project_owner

    if type_of_project:
        check_none_and_blank(type_of_project, 'type_of_project')
        edited_project.type_of_project = type_of_project

    db.session.add(edited_project)
    db.session.commit()
    return make_response(jsonify(message='PROJECT_EDITED'))
