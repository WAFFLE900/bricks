"""Mention extraction and notification.

Extracted from the REST record routes so both the synchronous PATCH path and the
collaboration persistence loop derive mentions the same way, keeping notification
behaviour identical no matter which writer materialises ``textBox_content`` (A4/A5).
"""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.models.entities import Notification, Project, Record, User

MENTION_SUFFIX_PATTERN = r"(?=$|[\s,.;:!?，。；：！？、)\]}）】])"


def project_users(project: Project) -> list[User]:
    members = [project.user]
    members.extend(item.user for item in project.memberships)
    return members


def mention_aliases(user: User) -> list[str]:
    aliases = [user.user_name.strip(), user.user_email.strip()]
    email_prefix = user.user_email.split("@", 1)[0].strip()
    if email_prefix:
        aliases.append(email_prefix)

    deduped: list[str] = []
    seen = set()
    for alias in aliases:
        normalized = alias.casefold()
        if not alias or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(alias)
    return deduped


def extract_mentioned_users(content: str | None, project: Project) -> list[User]:
    if not content:
        return []

    mentioned: list[User] = []
    seen_user_ids: set[int] = set()

    for user in project_users(project):
        for alias in mention_aliases(user):
            pattern = rf"@{re.escape(alias)}{MENTION_SUFFIX_PATTERN}"
            if re.search(pattern, content, flags=re.IGNORECASE):
                if user.id not in seen_user_ids:
                    mentioned.append(user)
                    seen_user_ids.add(user.id)
                break

    return mentioned


def build_excerpt(content: str | None) -> str:
    if not content:
        return ""
    return re.sub(r"\s+", " ", content).strip()[:80]


def notify_new_mentions(
    db: Session,
    *,
    actor: User,
    project: Project,
    record: Record,
    content: str | None,
    previous_content: str | None = None,
) -> None:
    current_mentions = {user.id: user for user in extract_mentioned_users(content, project) if user.id != actor.id}
    previous_mentions = {user.id for user in extract_mentioned_users(previous_content, project)}
    new_user_ids = set(current_mentions) - previous_mentions
    if not new_user_ids:
        return

    excerpt = build_excerpt(content)
    for user_id in new_user_ids:
        user = current_mentions[user_id]
        db.add(
            Notification(
                recipient_user_id=user.id,
                actor_user_id=actor.id,
                project_id=project.id,
                notification_type="text_box_mention",
                notification_title=f"{actor.user_name} 在會議記錄提及了你",
                notification_body=f"專案《{project.project_name}》／《{record.record_name}》：{excerpt}",
            )
        )
