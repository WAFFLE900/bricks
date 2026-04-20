import apiClient from "@/shared/api/client";
import type { RecordItem, TextBox } from "@/shared/types/domain";

export async function listRecords(projectId: number, includeTrashed = false) {
  const { data } = await apiClient.get<RecordItem[]>(`/projects/${projectId}/records`, {
    params: { include_trashed: includeTrashed },
  });
  return data;
}

export async function createRecord(
  projectId: number,
  payload: {
    record_name: string;
    record_department?: string;
    record_place?: string;
    record_host_name?: string;
    record_attendances?: number;
  },
) {
  const { data } = await apiClient.post<RecordItem>(`/projects/${projectId}/records`, payload);
  return data;
}

export async function getRecord(projectId: number, recordId: number) {
  const { data } = await apiClient.get<RecordItem>(`/projects/${projectId}/records/${recordId}`);
  return data;
}

export async function addTextBox(recordId: number, textBoxContent: string) {
  const { data } = await apiClient.post<TextBox>(`/records/${recordId}/text-boxes`, {
    textBox_content: textBoxContent,
  });
  return data;
}

