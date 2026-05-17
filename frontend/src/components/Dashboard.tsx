import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPatients, Patient } from '../api/fhirClient';
import { useAuth } from '../context/AuthContext';
import { Users, Search, LogOut, Activity, Calendar, User as UserIcon } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPatients();
  }, []);

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
                      <div className="flex items-center">
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
