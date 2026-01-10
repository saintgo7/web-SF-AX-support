export type DegreeType = 'PHD' | 'MASTER' | 'BACHELOR';
export type OrgType = 'UNIVERSITY' | 'COMPANY' | 'RESEARCH' | 'OTHER';
export type QualificationStatus = 'PENDING' | 'QUALIFIED' | 'DISQUALIFIED';

export interface Expert {
  id: string;
  user_id: string;
  degree_type?: DegreeType;
  degree_field?: string;
  career_years?: number;
  position?: string;
  org_name?: string;
  org_type?: OrgType;
  specialties?: string[];
  certifications?: Certification[];
  qualification_status: QualificationStatus;
  qualification_note?: string;
  created_at: string;
  updated_at: string;
}

export interface Certification {
  name: string;
  issuer?: string;
  date?: string;
}

export interface QualificationCheck {
  passed: boolean;
  reason: string;
}

export interface QualificationVerifyResponse {
  expert_id: string;
  qualification_status: QualificationStatus;
  verification_details: {
    degree: QualificationCheck;
    career: QualificationCheck;
    position: QualificationCheck;
    certification: QualificationCheck;
  };
  verified_at: string;
}
