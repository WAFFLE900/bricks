export interface User {
  id: number;
  user_email: string;
  user_name: string;
  user_google_id?: string | null;
  user_facebook_id?: string | null;
  user_purpose?: string | null;
  user_identity?: string | null;
  user_otherTool?: string | null;
  user_avatar?: string | null;
  user_purpose_list?: string[];
  user_other_tool_list?: string[];
  has_password?: boolean;
  has_google_account?: boolean;
  has_facebook_account?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type OAuthProvider = "google" | "facebook";

export interface OAuthUrlResponse {
  auth_url: string;
}

export type ProjectMemberPermission = "view" | "edit";
export type ProjectUserPermission = "owner" | "view" | "edit";

export interface ProjectMember {
  user_id: number;
  user_name: string;
  user_email: string;
  role: "owner" | "member";
  permission: ProjectMemberPermission;
  can_edit: boolean;
  joined_at: string;
}

export interface Project {
  id: number;
  project_name: string;
  project_type?: string | null;
  project_image?: string | null;
  project_trashcan: boolean;
  project_ended: boolean;
  project_edit: boolean;
  project_visible: boolean;
  project_comment: boolean;
  project_creation_date: string;
  project_edit_date: string;
  owner_name: string;
  owner_email: string;
  current_user_permission: ProjectUserPermission;
  can_edit_content: boolean;
  can_manage_members: boolean;
  member_count: number;
  members: ProjectMember[];
}

export interface TextBox {
  id: number;
  textBox_content?: string | null;
  updated_at?: string | null;
  tags: string[];
}

export interface RecordItem {
  id: number;
  record_name: string;
  record_date?: string | null;
  record_department?: string | null;
  record_attendances?: number | null;
  record_place?: string | null;
  record_host_name?: string | null;
  record_trashcan: boolean;
  created_at: string;
  updated_at: string;
  tags: string[];
  text_boxes: TextBox[];
}

export type NotificationType = "project_invite" | "project_permission_updated" | "text_box_mention";

export interface ProjectNotification {
  id: number;
  notification_type: NotificationType;
  notification_title: string;
  notification_body: string;
  is_read: boolean;
  created_at: string;
  project_id: number;
  project_name: string;
  actor_name: string;
}
