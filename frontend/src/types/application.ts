export type ApplicationStatus = 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED';

export interface Application {
  id: string;
  user_id: string;
  expert_id: string;
  status: ApplicationStatus;
  submission_date?: string;
  review_note?: string;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDraft {
  // Additional fields for application form
  personal_statement?: string;
  experience_description?: string;
  motivation?: string;
  documents?: Document[];
}

export interface Document {
  id: string;
  name: string;
  url: string;
  type: 'CV' | 'CERTIFICATE' | 'PORTFOLIO' | 'OTHER';
  uploaded_at: string;
}
