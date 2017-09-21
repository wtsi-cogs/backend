from datetime import datetime, date
from typing import Dict, Union

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp_jinja2 import template

from db import ProjectGroup
from db_helper import get_most_recent_group, get_series, get_navbar_data
from permissions import view_only
from scheduling.deadlines import schedule_deadline


@template("group_create.jinja2")
@view_only("create_project_groups")
async def group_create(request: Request) -> Union[Dict, Response]:
    """
    Show the form for creating a new group
    This view should only be allowed if the user has 'create_project_groups'

    :param request:
    :return:
    """
    most_recent = get_most_recent_group(request.app["session"])
    series, part = get_new_series_part(most_recent)
    if most_recent.student_choice >= date.today():
        return web.Response(status=403, text="Can't create rotation now, current one is still in student choice phase")
    return {"group": {"part": part},
            "deadlines": request.app["deadlines"],
            "cur_option": "create_rotation",
            **get_navbar_data(request)}


@view_only("create_project_groups")
async def on_create(request: Request) -> Response:
    """
    Create a new project group
    This view should only be allowed if the user has 'create_project_groups'

    :param request:
    :return:
    """
    session = request.app["session"]
    most_recent = get_most_recent_group(session)
    series, part = get_new_series_part(most_recent)
    post = await request.post()
    deadlines = {key: datetime.strptime(value, "%d/%m/%Y") for key, value in post.items()}
    assert len(deadlines) == len(request.app["deadlines"]), "Not all the deadlines were set"
    group = ProjectGroup(series=series,
                         part=part,
                         read_only=False,
                         can_finalise=False,
                         **deadlines)
    session.add(group)
    most_recent.read_only = True
    session.commit()
    for id, time in deadlines.items():
        schedule_deadline(request.app, group, id, time)
    return web.Response(status=200, text="/")


@view_only("create_project_groups")
async def on_modify(request: Request) -> Response:
    """
    Modify the most recent project group
    This view should only be allowed if the user has 'create_project_groups'

    :param request:
    :return:
    """
    session = request.app["session"]
    part = int(request.match_info["group_part"])
    most_recent = get_most_recent_group(session)
    series = get_series(session, series=most_recent.series)
    group = next(group for group in series if group.part == part)
    post = await request.post()
    for key, value in post.items():
        time = datetime.strptime(value, "%d/%m/%Y")
        setattr(group, key, time)
        if time > datetime.now():
            schedule_deadline(request.app, group, key, time)
        if key == "student_choice":
            group.student_choosable = time > datetime.now()
    session.commit()
    return web.Response(status=200, text="/")

def get_new_series_part(group: ProjectGroup):
    series = group.series + group.part // 3
    part = (group.part % 3) + 1
    return series, part