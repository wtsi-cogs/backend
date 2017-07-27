from db import Project, User
from aiohttp import web
from aiohttp_jinja2 import template
from project import get_most_recent_group, get_group, get_series
from permissions import is_user


@template('group_overview.jinja2')
async def group_overview(request):
    """
    Find the correct group and send it to the user.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    if "group_series" in request.match_info:
        series = request.match_info["group_series"]
        part = request.match_info["group_part"]
        group = get_group(session, series, part)
    else:
        group = get_most_recent_group(session)
    if group is None:
        return web.Response(status=404, text="No projects found")
    return {"project_list": get_projects(request, group)}


@template('group_list_overview.jinja2')
async def series_overview(request):
    """
    Find the correct series as well as all groups in that series.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    series = request.match_info["group_series"]
    groups = get_series(session, series)
    projects = (get_projects(request, group) for group in groups)
    return {"series_list": projects}


def get_projects(request, group):
    """
    Return a list of all the projects in a ProjectGroup

    :param request:
    :param group:
    :return:
    """
    session = request.app["session"]
    cookies = request.cookies
    projects = session.query(Project).filter_by(group_id=group.id).all()
    for project in projects:
        project.read_only = group.read_only or not is_user(cookies, project.supervisor)
    return projects
