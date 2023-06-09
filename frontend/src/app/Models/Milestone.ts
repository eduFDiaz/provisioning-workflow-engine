export interface Milestone {
    correlationID:     string;
    workflow:          string;
    status:            string | ["not-started", "in-progress", "completed", "failed"];
    step:              string;
    milestoneName:     string;
    milestoneStepName: string;
    startTime:         string;
    endTime:           string;
    description:       string | "";
}