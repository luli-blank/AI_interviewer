export interface JobPosition {
  jobName: string;
  jobDesc: string;
  companyName?: string;
  companyDesc?: string;
}

export interface ResumeData {
  resumeText: string;
  fileName?: string;
}

export interface InterviewSessionData {
  position: {
    name: string;
    description: string;
    company?: string;
    companyInfo?: string;
  };
  resume: {
    text: string;
    fileName?: string;
  };
}
