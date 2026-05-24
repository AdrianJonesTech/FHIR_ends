import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPatients, Patient, initiateBlueButtonLogin } from '../api/fhirClient';
import { useAuth } from '../context/AuthContext';
import { Users, Search, LogOut, Activity, Calendar, User as UserIcon, Link as LinkIcon, CheckCircle } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<string | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPatients();
    
    // Check for connection status in URL
    const params = new URLSearchParams(window.location.search);
    const status = params.get('status');
    const detail = params.get('detail');
    if (status) {
      setConnectionStatus(status);
      if (status === 'error' && detail) {
        setErrorDetail(detail);
      }
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleBlueButtonConnect = async () => {
    try {
      const { url } = await initiateBlueButtonLogin();
      window.location.href = url;
    } catch (error) {
      console.error('Error initiating Blue Button login:', error);
      alert('Failed to connect to Blue Button. Please check backend configuration.');
    }
  };

  const fetchPatients = async (name?: string) => {
    setIsLoading(true);
    try {
      const bundle = await getPatients(name ? { name } : undefined);
      const patientList = bundle.entry?.map((e) => e.resource) || [];
      setPatients(patientList);
    } catch (error) {
      console.error('Error fetching patients:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPatients(searchTerm);
  };

  return (
    <div className="min-h-screen bg-black w-full text-gray-100">
      {/* Navbar */}
      <nav className="bg-gray-900 shadow-md border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-100">FHIR Central</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-300 mr-4">
                Welcome, <span className="font-semibold">{user?.username}</span>
              </div>
              <button
                onClick={logout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-300 bg-gray-900 hover:text-gray-100 focus:outline-none transition"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {connectionStatus === 'connected' && (
            <div className="mb-6 bg-green-900/30 border border-green-500/50 text-green-200 px-4 py-3 rounded-lg flex items-center">
              <CheckCircle className="h-5 w-5 mr-3 text-green-500" />
              <div>
                <p className="font-bold">Successfully connected to Blue Button 2.0!</p>
                <p className="text-sm">You can now access your Medicare claims data.</p>
              </div>
              <button 
                onClick={() => setConnectionStatus(null)}
                className="ml-auto text-green-500 hover:text-green-400"
              >
                &times;
              </button>
            </div>
          )}

          {connectionStatus === 'error' && (
            <div className="mb-6 bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg flex items-center">
              <Activity className="h-5 w-5 mr-3 text-red-500" />
              <div>
                <p className="font-bold">Connection to Blue Button failed</p>
                <p className="text-sm">Please ensure your Client ID and Secret are correctly configured in the backend.</p>
                {errorDetail && (
                  <div className="mt-2 p-2 bg-black/40 rounded border border-red-500/20 text-xs font-mono break-all">
                    Error Detail: {errorDetail}
                  </div>
                )}
              </div>
              <button 
                onClick={() => { setConnectionStatus(null); setErrorDetail(null); }}
                className="ml-auto text-red-500 hover:text-red-400 self-start"
              >
                &times;
              </button>
            </div>
          )}

          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 space-y-4 md:space-y-0">
            <div>
              <h1 className="text-2xl font-bold text-gray-100 flex items-center">
                <Users className="mr-2 h-6 w-6 text-blue-500" />
                Patient Directory
              </h1>
              <p className="text-sm text-gray-300 mt-1">
                View and manage patient health records
              </p>
            </div>

            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 w-full md:w-auto">
              <button
                onClick={handleBlueButtonConnect}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none transition"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                Connect Blue Button
              </button>

              <form onSubmit={handleSearch} className="relative w-full md:w-64">
                <input
                  type="text"
                  placeholder="Search by name..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-700 rounded-lg focus:ring-blue-500 focus:border-blue-500 bg-gray-900 text-gray-200"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-300" />
              </form>
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {patients.length > 0 ? (
                patients.map((patient) => (
                  <div
                    key={patient.id}
                    className="bg-gray-900 overflow-hidden shadow-lg rounded-lg border border-gray-800 hover:border-gray-700 transition duration-200 cursor-pointer"
                  >
                    <div className="px-4 py-5 sm:p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center flex-1">
                          <div className="flex-shrink-0 bg-blue-100 rounded-full p-3 dark:bg-blue-900/30">
                            <UserIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-300 truncate">
                                Patient ID: {patient.id}
                              </dt>
                              <dd className="flex items-baseline">
                                <div className="text-lg font-semibold text-gray-100">
                                  {patient.name?.[0]?.family}, {patient.name?.[0]?.given?.join(' ')}
                                </div>
                              </dd>
                            </dl>
                          </div>
                        </div>
                        {patient.id.startsWith('-') && (
                          <span className="bg-blue-900/40 text-blue-400 text-[10px] px-2 py-0.5 rounded-full border border-blue-500/30 uppercase font-bold tracking-wider ml-2">
                            Blue Button
                          </span>
                        )}
                      </div>
                      <div className="mt-4 border-t pt-4 border-gray-800 space-y-2">
                        <div className="flex items-center text-sm text-gray-300">
                          <Calendar className="mr-2 h-4 w-4" />
                          DOB: {patient.birthDate || 'N/A'}
                        </div>
                        <div className="flex items-center text-sm text-gray-300 capitalize">
                          <Activity className="mr-2 h-4 w-4" />
                          Gender: {patient.gender || 'Unknown'}
                        </div>
                      </div>
                    </div>
                    <div 
                      onClick={() => navigate(`/patient/${patient.id}`)}
                      className="bg-gray-800/50 px-4 py-4 sm:px-6 border-t border-gray-800 hover:bg-gray-800 transition cursor-pointer"
                    >
                      <div className="text-sm">
                        <span className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400">
                          View full record
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full text-center py-12 bg-gray-900 rounded-lg border-2 border-dashed border-gray-800">
                  <p className="text-gray-300">No patients found matching your search.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
