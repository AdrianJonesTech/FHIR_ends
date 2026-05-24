import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const fhirClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface HumanName {
  family?: string;
  given: string[];
}

export interface Patient {
  resourceType: 'Patient';
  id: string;
  name: HumanName[];
  birthDate?: string;
  gender?: string;
}

export interface Observation {
  resourceType: 'Observation';
  id: string;
  status: string;
  category?: any[];
  code: {
    coding: {
      system?: string;
      code?: string;
      display?: string;
    }[];
    text?: string;
  };
  subject: {
    reference: string;
  };
  effectiveDateTime?: string;
  valueQuantity?: {
    value: number;
    unit?: string;
    system?: string;
    code?: string;
  };
  valueCodeableConcept?: any;
  valueString?: string;
}

export interface BundleEntry {
  fullUrl?: string;
  resource: any; // Can be Patient or Observation
}

export interface Bundle {
  resourceType: 'Bundle';
  type: string;
  total?: number;
  entry: BundleEntry[];
}

export interface Coverage {
  resourceType: 'Coverage';
  id: string;
  status: string;
  type?: any;
  beneficiary: { reference: string };
  payor: any[];
}

export interface ExplanationOfBenefit {
  resourceType: 'ExplanationOfBenefit';
  id: string;
  status: string;
  type: any;
  use: string;
  patient: { reference: string };
  created: string;
  insurer: any;
  provider: any;
  outcome: string;
  total?: any[];
}

export const getPatients = async (params?: any) => {
  const response = await fhirClient.get<Bundle>('/fhir/Patient', { params });
  return response.data;
};

export const getPatient = async (id: string) => {
  const response = await fhirClient.get<Patient>(`/fhir/Patient/${id}`);
  return response.data;
};

export const getObservations = async (patientId: string) => {
  const response = await fhirClient.get<Bundle>(`/fhir/Observation`, {
    params: { patient: patientId }
  });
  return response.data;
};

export const getCoverages = async (patientId: string) => {
  const response = await fhirClient.get<Bundle>(`/fhir/Coverage`, {
    params: { beneficiary: patientId }
  });
  return response.data;
};

export const getEOBs = async (patientId: string) => {
  const response = await fhirClient.get<Bundle>(`/fhir/ExplanationOfBenefit`, {
    params: { patient: patientId }
  });
  return response.data;
};

export const initiateBlueButtonLogin = async () => {
  const response = await fhirClient.get<{ url: string }>('/api/oauth/login');
  return response.data;
};

export default fhirClient;
