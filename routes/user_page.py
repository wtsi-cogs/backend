from datetime import date

from aiohttp_jinja2 import template

from db_helper import get_most_recent_group, get_projects_supervisor, get_user_id, get_student_projects, get_all_groups, get_projects_cogs
from permissions import get_permission_from_cookie, can_view_group


@template("user_page.jinja2")
async def user_page(request):
    """
    Get the page for the user.
    If they own projects, show them including legacy projects.
    If they are part of projects, show them.
    If they are in the process for signing up for projects, put them at the start

    :param request:
    :return:
    """
    cookies = request.cookies
    session = request.app["session"]
    most_recent = get_most_recent_group(session)
    user = get_user_id(session, cookies)
    rtn = {
        "can_edit": not most_recent.read_only,
        "deadlines": request.app["deadlines"],
        "display_projects_link": can_view_group(request, most_recent),
        "user": user
    }
    if user:
        rtn["first_option"] = user.first_option
        rtn["second_option"] = user.second_option
        rtn["third_option"] = user.third_option
    if get_permission_from_cookie(cookies, "create_projects"):
        rtn["series_list"] = get_projects_supervisor(request, int(cookies["user_id"]))
    if get_permission_from_cookie(cookies, "modify_project_groups"):
        rtn["group"] = {}
        for column in most_recent.__table__.columns:
            rtn["group"][column.key] = getattr(most_recent, column.key)
            if isinstance(rtn["group"][column.key], date):
                rtn["group"][column.key] = rtn["group"][column.key].strftime("%d/%m/%Y")
    if get_permission_from_cookie(cookies, "review_other_projects"):
        rtn["review_list"] = get_projects_cogs(session, cookies)
    if get_permission_from_cookie(cookies, "join_projects"):
        rtn["project_list"] = get_student_projects(session, cookies)
    if get_permission_from_cookie(cookies, "view_all_submitted_projects"):
        rtn["series_years"] = sorted({group.series for group in get_all_groups(session)}, reverse=True)
        rtn["rotations"] = sorted({group.part for group in get_all_groups(session) if group.series == most_recent.series}, reverse=True)
    rtn.update(cookies)
    return rtn
