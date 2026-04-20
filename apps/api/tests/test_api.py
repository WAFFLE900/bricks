from __future__ import annotations


def _register_and_login(
    client,
    *,
    user_email: str = "jane@example.com",
    user_name: str = "Jane",
    user_password: str = "super-secret",
):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "user_email": user_email,
            "user_password": user_password,
            "user_name": user_name,
        },
    )
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_and_survey_flow(client):
    headers = _register_and_login(client)

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["user_email"] == "jane@example.com"

    survey_response = client.post(
        "/api/v1/auth/survey",
        headers=headers,
        json={
            "user_purpose": ["project-management", "meeting-notes"],
            "user_identity": "founder",
            "user_otherTool": ["Notion", "Trello"],
        },
    )
    assert survey_response.status_code == 200
    assert survey_response.json()["user_identity"] == "founder"
    assert survey_response.json()["user_purpose_list"] == ["project-management", "meeting-notes"]


def test_profile_password_and_social_link_flow(client):
    headers = _register_and_login(client)

    profile_response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "user_name": "Jane Designer",
            "user_identity": "designer",
            "user_purpose": ["knowledge-base"],
            "user_otherTool": ["Notion", "Asana"],
        },
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["user_name"] == "Jane Designer"
    assert profile_response.json()["user_other_tool_list"] == ["Notion", "Asana"]

    link_response = client.get("/api/v1/users/me/social-accounts/google/link-url?redirect=/profile", headers=headers)
    assert link_response.status_code == 200
    assert "accounts.google.com" in link_response.json()["auth_url"]
    assert "state=" in link_response.json()["auth_url"]

    change_password_response = client.post(
        "/api/v1/users/me/password",
        headers=headers,
        json={
            "current_password": "super-secret",
            "new_password": "new-password-123",
        },
    )
    assert change_password_response.status_code == 200
    assert change_password_response.json()["has_password"] is True

    old_login_response = client.post(
        "/api/v1/auth/login",
        json={
            "user_email": "jane@example.com",
            "user_password": "super-secret",
        },
    )
    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/api/v1/auth/login",
        json={
            "user_email": "jane@example.com",
            "user_password": "new-password-123",
        },
    )
    assert new_login_response.status_code == 200


def test_project_and_search_flow(client):
    headers = _register_and_login(client)

    create_response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"project_name": "Rewrite Bricks", "project_type": "Roadmap"},
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    list_response = client.get("/api/v1/projects?status=active", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["current_user_permission"] == "owner"

    search_response = client.get("/api/v1/search/projects?q=rewrite&status=active", headers=headers)
    assert search_response.status_code == 200
    assert search_response.json()["items"][0]["id"] == project_id

    state_response = client.patch(
        f"/api/v1/projects/{project_id}/state",
        headers=headers,
        json={"state": "end"},
    )
    assert state_response.status_code == 200
    assert state_response.json()["project_ended"] is True

    trash_response = client.patch(
        f"/api/v1/projects/{project_id}/trash",
        headers=headers,
        json={"in_trash": True},
    )
    assert trash_response.status_code == 200
    assert trash_response.json()["project_trashcan"] is True


def test_record_text_box_and_tag_flow(client):
    headers = _register_and_login(client)
    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"project_name": "Meeting Hub", "project_type": "Ops"},
    ).json()

    record_response = client.post(
        f"/api/v1/projects/{project['id']}/records",
        headers=headers,
        json={
            "record_name": "Sprint Sync",
            "record_department": "Product",
            "record_attendances": 4,
            "record_place": "Room A",
            "record_host_name": "Jane",
        },
    )
    assert record_response.status_code == 201
    record_id = record_response.json()["id"]

    text_box_response = client.post(
        f"/api/v1/records/{record_id}/text-boxes",
        headers=headers,
        json={"textBox_content": "Ship the Vite rewrite first."},
    )
    assert text_box_response.status_code == 201
    text_box_id = text_box_response.json()["id"]

    tag_response = client.post("/api/v1/tags", headers=headers, json={"tag_name": "priority"})
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["id"]

    attach_response = client.post(
        f"/api/v1/text-boxes/{text_box_id}/tags",
        headers=headers,
        json={"tag_id": tag_id},
    )
    assert attach_response.status_code == 200
    assert attach_response.json()["tag_name"] == "priority"

    detail_response = client.get(f"/api/v1/projects/{project['id']}/records/{record_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["text_boxes"][0]["tags"] == ["priority"]

    trash_response = client.patch(
        f"/api/v1/records/{record_id}/trash",
        headers=headers,
        json={"in_trash": True},
    )
    assert trash_response.status_code == 200
    assert trash_response.json()["record_trashcan"] is True


def test_project_collaboration_permissions_and_notifications_flow(client):
    owner_headers = _register_and_login(
        client,
        user_email="owner@example.com",
        user_name="Owner",
    )
    editor_headers = _register_and_login(
        client,
        user_email="editor@example.com",
        user_name="Editor",
    )
    viewer_headers = _register_and_login(
        client,
        user_email="viewer@example.com",
        user_name="Viewer",
    )

    project_response = client.post(
        "/api/v1/projects",
        headers=owner_headers,
        json={"project_name": "Collab Hub", "project_type": "Shared"},
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    editor_invite_response = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=owner_headers,
        json={"user_email": "editor@example.com", "permission": "edit"},
    )
    assert editor_invite_response.status_code == 201
    assert editor_invite_response.json()["member_count"] == 2

    viewer_invite_response = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=owner_headers,
        json={"user_email": "viewer@example.com", "permission": "view"},
    )
    assert viewer_invite_response.status_code == 201
    assert viewer_invite_response.json()["member_count"] == 3

    viewer_user_id = next(
        member["user_id"]
        for member in viewer_invite_response.json()["members"]
        if member["user_email"] == "viewer@example.com"
    )

    editor_projects_response = client.get("/api/v1/projects?status=active", headers=editor_headers)
    assert editor_projects_response.status_code == 200
    assert editor_projects_response.json()[0]["current_user_permission"] == "edit"

    viewer_projects_response = client.get("/api/v1/projects?status=active", headers=viewer_headers)
    assert viewer_projects_response.status_code == 200
    assert viewer_projects_response.json()[0]["current_user_permission"] == "view"

    viewer_notifications_response = client.get("/api/v1/notifications", headers=viewer_headers)
    assert viewer_notifications_response.status_code == 200
    assert viewer_notifications_response.json()[0]["notification_type"] == "project_invite"

    forbidden_record_response = client.post(
        f"/api/v1/projects/{project_id}/records",
        headers=viewer_headers,
        json={"record_name": "Viewer should fail"},
    )
    assert forbidden_record_response.status_code == 403

    editor_record_response = client.post(
        f"/api/v1/projects/{project_id}/records",
        headers=editor_headers,
        json={"record_name": "Editor can write"},
    )
    assert editor_record_response.status_code == 201
    record_id = editor_record_response.json()["id"]

    viewer_record_list_response = client.get(f"/api/v1/projects/{project_id}/records", headers=viewer_headers)
    assert viewer_record_list_response.status_code == 200
    assert viewer_record_list_response.json()[0]["id"] == record_id

    permission_update_response = client.patch(
        f"/api/v1/projects/{project_id}/members/{viewer_user_id}",
        headers=owner_headers,
        json={"permission": "edit"},
    )
    assert permission_update_response.status_code == 200

    viewer_notification_types = {
        item["notification_type"] for item in client.get("/api/v1/notifications", headers=viewer_headers).json()
    }
    assert "project_invite" in viewer_notification_types
    assert "project_permission_updated" in viewer_notification_types

    allowed_record_response = client.post(
        f"/api/v1/projects/{project_id}/records",
        headers=viewer_headers,
        json={"record_name": "Viewer can write now"},
    )
    assert allowed_record_response.status_code == 201

    read_all_response = client.post("/api/v1/notifications/read-all", headers=viewer_headers)
    assert read_all_response.status_code == 204

    notifications_after_read = client.get("/api/v1/notifications", headers=viewer_headers)
    assert notifications_after_read.status_code == 200
    assert all(item["is_read"] is True for item in notifications_after_read.json())

    mention_response = client.post(
        f"/api/v1/records/{record_id}/text-boxes",
        headers=editor_headers,
        json={"textBox_content": "請 @Viewer 協助整理下一步與待辦事項。"},
    )
    assert mention_response.status_code == 201

    notifications_after_mention = client.get("/api/v1/notifications", headers=viewer_headers)
    assert notifications_after_mention.status_code == 200
    assert notifications_after_mention.json()[0]["notification_type"] == "text_box_mention"
