from aiohttp.web import Request, Response
from ._format import JSONResonse, HTTPError, get_post

from cogs.common.constants import ROTATION_TEMPLATE_IDS
from cogs.mail import sanitise


async def get_all(request: Request) -> Response:
    """
    Get a list of templates

    :param request:
    :return:
    """
    db = request.app["db"]
    emails = db.get_all_templates()
    return JSONResonse(links={email.name: f"/api/emails/{email.name}" for email in emails},
                       items=[email.serialise() for email in emails])


async def get(request: Request) -> Response:
    """
    Get a specific template

    :param request:
    :return:
    """
    db = request.app["db"]
    template_name = request.match_info["email_name"]

    if template_name not in ROTATION_TEMPLATE_IDS:
        raise HTTPError(status=404,
                        message="Invalid email template name")

    email = db.get_template_by_name(template_name)
    return JSONResonse(links={"parent": "/api/emails"},
                       data=email.serialise())


async def edit(request: Request) -> Response:
    """
    Set the contents of a specific email template

    :param request:
    :return:
    """
    db = request.app["db"]
    template_name = request.match_info["email_name"]

    if template_name not in ROTATION_TEMPLATE_IDS:
        raise HTTPError(status=404,
                        message="Invalid email template name")

    template_data = await get_post(request, {"subject": str,
                                             "data": str})

    template = db.get_template_by_name(template_name)
    template.subject = template_data.subject
    template.content = sanitise(template_data.data)
    db.commit()
    return JSONResonse(status=204)