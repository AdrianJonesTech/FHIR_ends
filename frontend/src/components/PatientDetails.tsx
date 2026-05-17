import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPatient, Patient, getObservations, Observation } from '../api/fhirClient';
import { 
  Activity, ArrowLeft, Calendar, User as UserIcon, Shield, Globe, Tag, 
  History, Info, LineChart as ChartIcon, List
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';

const PatientDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'clinical'>('summary');

  useEffect(() => {
    if (id) {
      fetchData(id);
    }
  }, [id]);

  const fetchData = async (patientId: string) => {
    setIsLoading(true);
    try {
      const [patientData, obsData] = await Promise.all([
        getPatient(patientId),
        getObservations(patientId)
      ]);
      setPatient(patientData);
      setObservations(obsData.entry?.map(e => e.resource as Observation) || []);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load patient record.');
    } finally {
      setIsLoading(false);
    }
  };

  const getChartData = (obsCode: string) => {
    return observations
      .filter(obs => obs.code.coding.some(c => c.code === obsCode) && obs.valueQuantity)
      .map(obs => ({
        date: obs.effectiveDateTime ? new Date(obs.effectiveDateTime).toLocaleDateString() : 'N/A',
        value: obs.valueQuantity?.value,
        unit: obs.valueQuantity?.unit
      }))
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  };

  const vitalsToChart = [
    { code: '8867-4', name: 'Heart Rate', color: '#ef4444' },
    { code: '8302-2', name: 'Body Height', color: '#3b82f6' },
    { code: '2339-0', name: 'Glucose', color: '#10b981' },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-gray-100">
        <p className="text-xl text-red-400 mb-4">{error || 'Patient not found'}</p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center px-4 py-2 bg-gray-900 border border-gray-700 rounded-md hover:bg-gray-800 transition"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black w-full text-gray-100">
      <nav className="bg-gray-900 shadow-md border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button 
                onClick={() => navigate('/dashboard')}
                className="mr-4 p-2 text-gray-300 hover:text-gray-100 transition"
              >
                <ArrowLeft className="h-6 w-6" />
              </button>
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-100">FHIR Central</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-100 flex items-center">
              Patient Record: {patient.id}
            </h1>
            <p className="text-gray-400 mt-2">Comprehensive view of FHIR Patient Resource</p>
          </div>
          
          <div className="flex bg-gray-900 p-1 rounded-lg border border-gray-800">
            <button
              onClick={() => setActiveTab('summary')}
              className={`flex items-center px-4 py-2 rounded-md transition ${
                activeTab === 'summary' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Info className="mr-2 h-4 w-4" />
              Summary
            </button>
            <button
              onClick={() => setActiveTab('clinical')}
              className={`flex items-center px-4 py-2 rounded-md transition ${
                activeTab === 'clinical' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <History className="mr-2 h-4 w-4" />
              Clinical History
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Summary Card (Always visible for context) */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden shadow-xl">
              <div className="p-6">
                <div className="flex justify-center mb-6">
                  <div className="bg-blue-900/30 p-6 rounded-full border border-blue-500/30">
                    <UserIcon className="h-16 w-16 text-blue-500" />
                  </div>
                </div>
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-100">
                    {patient.name?.[0]?.family}, {patient.name?.[0]?.given?.join(' ')}
                  </h2>
                  <p className="text-gray-400 text-sm mt-1">ID: {patient.id}</p>
                </div>

                <div className="mt-8 space-y-4">
                  <div className="flex items-center text-gray-300 p-3 bg-gray-800/50 rounded-lg">
                    <Calendar className="mr-3 h-5 w-5 text-blue-400" />
                    <div>
                      <p className="text-xs text-gray-500 uppercase font-semibold">Birth Date</p>
                      <p>{patient.birthDate || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="flex items-center text-gray-300 p-3 bg-gray-800/50 rounded-lg">
                    <Activity className="mr-3 h-5 w-5 text-blue-400" />
                    <div>
                      <p className="text-xs text-gray-500 uppercase font-semibold">Gender</p>
                      <p className="capitalize">{patient.gender || 'Unknown'}</p>
                    </div>
                  </div>
                  <div className="flex items-center text-gray-300 p-3 bg-gray-800/50 rounded-lg">
                    <Tag className="mr-3 h-5 w-5 text-blue-400" />
                    <div>
                      <p className="text-xs text-gray-500 uppercase font-semibold">Resource Type</p>
                      <p>{patient.resourceType}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 shadow-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Shield className="mr-2 h-5 w-5 text-green-500" />
                Security & Privacy
              </h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                This record is protected by standard HIPAA-compliant security measures. 
                Any access is logged and audited according to hospital policy.
              </p>
            </div>
          </div>

          {/* Right Column: Tab Content */}
          <div className="lg:col-span-2 space-y-6">
            {activeTab === 'summary' ? (
              <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl overflow-hidden">
                <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
                  <h3 className="text-lg font-semibold flex items-center text-gray-100">
                    <Globe className="mr-2 h-5 w-5 text-blue-400" />
                    Raw FHIR Resource (JSON)
                  </h3>
                  <span className="px-2 py-1 text-xs font-mono bg-blue-900/40 text-blue-300 rounded border border-blue-500/20">
                    application/fhir+json
                  </span>
                </div>
                <div className="p-0">
                  <pre className="p-6 text-sm font-mono text-blue-200 overflow-auto max-h-[600px] bg-black/50 scrollbar-thin scrollbar-thumb-gray-800">
                    {JSON.stringify(patient, null, 2)}
                  </pre>
                </div>
                <div className="bg-gray-800/50 px-6 py-4 border-t border-gray-800">
                  <p className="text-xs text-gray-400">
                    FHIR R4 Standard Compliance: This resource follows the official Fast Healthcare Interoperability Resources (R4) specification.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Visual Trends */}
                <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl p-6">
                  <h3 className="text-lg font-semibold mb-6 flex items-center text-gray-100">
                    <ChartIcon className="mr-2 h-5 w-5 text-blue-400" />
                    Vitals & Trends
                  </h3>
                  
                  <div className="grid grid-cols-1 gap-8">
                    {vitalsToChart.map(vital => {
                      const data = getChartData(vital.code);
                      if (data.length === 0) return null;
                      
                      return (
                        <div key={vital.code} className="h-64 w-full">
                          <p className="text-sm font-medium text-gray-300 mb-2">{vital.name}</p>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                              <XAxis 
                                dataKey="date" 
                                stroke="#9ca3af" 
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                              />
                              <YAxis 
                                stroke="#9ca3af" 
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                label={{ value: data[0]?.unit, angle: -90, position: 'insideLeft', fill: '#9ca3af', fontSize: 10 }}
                              />
                              <Tooltip 
                                contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
                                itemStyle={{ color: vital.color }}
                              />
                              <Line 
                                type="monotone" 
                                dataKey="value" 
                                stroke={vital.color} 
                                strokeWidth={3}
                                dot={{ fill: vital.color, r: 4 }}
                                activeDot={{ r: 6, strokeWidth: 0 }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      );
                    })}
                    {observations.filter(o => o.valueQuantity).length === 0 && (
                      <div className="text-center py-12 text-gray-500">
                        <ChartIcon className="mx-auto h-12 w-12 opacity-20 mb-4" />
                        <p>No trend data available for this patient.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Observations Table */}
                <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
                    <h3 className="text-lg font-semibold flex items-center text-gray-100">
                      <List className="mr-2 h-5 w-5 text-blue-400" />
                      All Observations
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="bg-gray-800/50 text-gray-400 text-xs uppercase tracking-wider">
                          <th className="px-6 py-3 font-semibold">Date</th>
                          <th className="px-6 py-3 font-semibold">Observation</th>
                          <th className="px-6 py-3 font-semibold">Value</th>
                          <th className="px-6 py-3 font-semibold">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-800">
                        {observations.map((obs) => (
                          <tr key={obs.id} className="hover:bg-gray-800/30 transition">
                            <td className="px-6 py-4 text-sm text-gray-300">
                              {obs.effectiveDateTime ? new Date(obs.effectiveDateTime).toLocaleDateString() : 'N/A'}
                            </td>
                            <td className="px-6 py-4">
                              <p className="text-sm font-medium text-gray-100">{obs.code.coding[0]?.display || 'Unknown'}</p>
                              <p className="text-xs text-gray-500">{obs.category?.[0]?.coding?.[0]?.code || 'General'}</p>
                            </td>
                            <td className="px-6 py-4 text-sm font-mono text-blue-400">
                              {obs.valueQuantity 
                                ? `${obs.valueQuantity.value} ${obs.valueQuantity.unit || ''}`
                                : obs.valueString || 'N/A'}
                            </td>
                            <td className="px-6 py-4">
                              <span className="px-2 py-1 text-xs rounded-full bg-green-900/30 text-green-400 border border-green-500/20 capitalize">
                                {obs.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                        {observations.length === 0 && (
                          <tr>
                            <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                              No observation records found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PatientDetails;
