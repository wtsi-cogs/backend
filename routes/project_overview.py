from aiohttp import web
from aiohttp_jinja2 import template

from db_helper import get_most_recent_group, get_group, get_series, get_user_id, get_group_projects
from permissions import can_view_group


@template('group_overview.jinja2')
async def group_overview(request):
    """
    Find the correct group and send it to the user.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    most_recent = get_most_recent_group(session)
    if "group_series" in request.match_info:
        series = int(request.match_info["group_series"])
        part = int(request.match_info["group_part"])
        group = get_group(session, series, part)
    else:
        group = most_recent
    if group is None:
        return web.Response(status=404, text="No projects found")
    elif group is most_recent:
        if not can_view_group(request, group):
            return web.Response(status=403, text="Cannot view rotation")
    return {"project_list": get_group_projects(request, group),
            "user": get_user_id(session, request.cookies)}


@template('group_list_overview.jinja2')
async def series_overview(request):
    """
    Find the correct series as well as all groups in that series.

    :param request:
    :return Response:
    """
    session = request.app["session"]
    series = int(request.match_info["group_series"])
    groups = get_series(session, series)
    projects = (get_group_projects(request, group) for group in groups if can_view_group(request, group))
    return {"series_list": projects,
            "user": get_user_id(session, request.cookies)}

