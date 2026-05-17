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

export interface BundleEntry {
  fullUrl?: string;
  resource: Patient;
}

export interface Bundle {
  resourceType: 'Bundle';
  type: string;
  total?: number;
  entry: BundleEntry[];
}

export const getPatients = async (params?: any) => {
  const response = await fhirClient.get<Bundle>('/fhir/Patient', { params });
  return response.data;
};

export const getPatient = async (id: string) => {
  const response = await fhirClient.get<Patient>(`/fhir/Patient/${id}`);
  return response.data;
};

export default fhirClient;
