"""
Sherlock Scenario Controllers and Routes.

For new Test Scenarios, it also create Test Cases
"""
from flask import Blueprint, request, url_for, redirect, g, render_template
from flask import flash, jsonify
from flask_babel import gettext
from flask_login import login_required

from sherlock import db
from sherlock.data.model import Scenario, Project, Case, TestCaseSchema
from sherlock.forms.scenario import new_scenario_form
from sherlock.helpers.string_operations import empty_items_in_dict

scenario = Blueprint('scenarios', __name__)


@scenario.url_value_preprocessor
def get_scenario(endpoint, values):
    """Blueprint Object Query."""
    if 'project_id' in values:
        p_query = Project.query.filter_by(id=values.pop('project_id'))
        g.project = p_query.first_or_404()
        if 'scenario_id' in values:
            s_query = Scenario.query.filter_by(
                id=values.pop('scenario_id'))
            g.scenario = s_query.first_or_404()



@scenario.route('/get_cases_for_scenario/<int:scenario_id>', methods=['GET'])
@login_required
def get_tst_cases():
    """Docstring."""
    tst_cases = Case.query.filter_by(scenario_id=g.scenario.id).all()
    tst_schema = TestCaseSchema(many=True)
    result = tst_schema.dump(tst_cases)
    return jsonify(result)


@scenario.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """POST endpoint for new scenarios.

    Param:
        name(required)
        scenario_name(required).
    """
    form = new_scenario_form()

    if form.validate_on_submit() and request.method == 'POST':
        dict = request.form.to_dict()
        dict.pop('csrf_token')
        scenario_name = dict.pop('tst_scenario')

        if empty_items_in_dict(dict):
                flash(gettext('Test Cases cannot be blank'), 'danger')
        else:
            new_scenario = Scenario(name=scenario_name,
                                    project_id=g.project.id)
            db.session.add(new_scenario)
            db.session.commit()

            first_tst_case = Case(name=dict['tst_case'],
                                  scenario_id=new_scenario.id)
            db.session.add(first_tst_case)

            for i in range(0, dict.__len__()):
                if 'tst_case[{}]'.format(i) in dict:
                    new_case = Case(name=dict['tst_case[{}]'.format(i)],
                                    scenario_id=new_scenario.id)
                    db.session.add(new_case)
                else:
                    break
            db.session.commit()
            flash(gettext('Scenarios and Cases created!'), 'Success')
            return redirect(url_for('projects.show', project_id=g.project.id))

    return render_template("scenario/new.html", form=form)


@scenario.route('/edit/<int:scenario_id>', methods=['POST'])
@login_required
def edit():
    """POST endpoint for editing existing scenarios.

    Param:
        name
    """
    if request.method == 'POST':
        scenario = g.scenario
        scenario.name = request.get_json().get('scenario_name')
        db.session.add(scenario)
        db.session.commit()
        flash(gettext('Scenario edited!'), 'Success')

        return jsonify({"status": "ok",
                        "scenario_id": scenario.id,
                        "scenario_name": scenario.name})
    elif request.method == 'GET':
        return redirect(url_for('projects.show', project_id=g.project.id))


@login_required
@scenario.route('/edit/', methods=['GET'])
def edit_all():
    scenarios = Scenario.query.filter_by(project_id=g.project.id)
    if scenarios.count() == 0:
        flash(gettext('You dont have any test scenario and case to edit'),
                      'info')
        return redirect(url_for('projects.show', project_id=g.project.id))
    else:
        g.scenarios = scenarios

    return render_template("scenario/edit.html")
