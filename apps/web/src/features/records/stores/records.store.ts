import { defineStore } from "pinia";

import type { Project, RecordItem } from "@/shared/types/domain";
import * as projectsApi from "@/features/projects/api/projects.api";
import * as recordsApi from "../api/records.api";

export const useRecordsStore = defineStore("records", {
  state: () => ({
    items: [] as RecordItem[],
    project: null as Project | null,
    selectedRecord: null as RecordItem | null,
    loading: false,
  }),
  actions: {
    async load(projectId: number) {
      this.loading = true;
      try {
        const [project, records] = await Promise.all([
          projectsApi.getProject(projectId),
          recordsApi.listRecords(projectId),
        ]);
        this.project = project;
        this.items = records;
        this.selectedRecord = this.items[0] || null;
        return this.items;
      } finally {
        this.loading = false;
      }
    },
    async open(projectId: number, recordId: number) {
      if (!this.project || this.project.id !== projectId) {
        this.project = await projectsApi.getProject(projectId);
      }
      this.selectedRecord = await recordsApi.getRecord(projectId, recordId);
      return this.selectedRecord;
    },
    async create(
      projectId: number,
      payload: {
        record_name: string;
        record_department?: string;
        record_place?: string;
        record_host_name?: string;
        record_attendances?: number;
      },
    ) {
      const record = await recordsApi.createRecord(projectId, payload);
      this.items.unshift(record);
      this.selectedRecord = record;
      return record;
    },
    async addTextBox(recordId: number, textBoxContent: string) {
      const textBox = await recordsApi.addTextBox(recordId, textBoxContent);
      if (this.selectedRecord?.id === recordId) {
        this.selectedRecord.text_boxes.unshift(textBox);
      }
      return textBox;
    },
  },
});
