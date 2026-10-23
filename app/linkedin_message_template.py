from __future__ import annotations

from string import Formatter


DEFAULT_MESSAGE_TEMPLATE = """Hi {first_name},

I wanted to reach out regarding...
"""


def build_message(
    first_name: str,
    template: str | None = None,
    *,
    company: str = "",
) -> str:
    """
    STEP 3B — personalize a message.

    Supported variables:
        {first_name}
        {company}

    This function only returns text.
    It does NOT interact with LinkedIn.
    """

    cleaned_first_name = (
        str(
            first_name
            or ""
        )
        .strip()
    )

    if not cleaned_first_name:
        raise ValueError(
            "First name cannot be empty."
        )

    active_template = (
        template
        if template is not None
        else DEFAULT_MESSAGE_TEMPLATE
    )

    if not str(
        active_template
        or ""
    ).strip():
        raise ValueError(
            "Message template cannot be empty."
        )

    cleaned_company = str(company or "").strip()
    if template_uses_company(active_template) and not cleaned_company:
        raise ValueError("This recipient has no saved company name. Add it before using {company}.")

    try:
        message = (
            active_template
            .format(
                first_name=(
                    cleaned_first_name
                ),
                company=cleaned_company,
            )
        )

    except KeyError as exc:
        raise ValueError(
            "Unsupported template variable: "
            f"{exc}"
        ) from exc

    return message


def template_uses_company(template: str) -> bool:
    return any(field == "company" for _, field, _, _ in Formatter().parse(template))
