import { Milestone } from "./Milestone";

export interface Workflow { 
    workflowName: string;
    milestones: Milestone[];
    status: string | ["not-started", "in-progress", "completed", "failed"];
}