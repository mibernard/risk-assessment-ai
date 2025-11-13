"use client";

/**
 * Dashboard Page
 * 
 * Displays all flagged banking transactions in a table.
 * Users can click on rows to view case details.
 */

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getCases, formatCurrency, formatDateTime, type Case } from "@/lib/api";
import { RiskBadge } from "@/components/RiskBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";

export default function DashboardPage() {
  const router = useRouter();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [queryName, setQueryName] = useState<string | number>("");
  const [queryCountry, setQueryCountry] = useState<string | number>("");
  const [risk, setRisk] = useState<string>("1000");
  const [status, setStatus] = useState<string>("all");

  const fetchCases = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCases();
      setCases(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cases");
    } finally {
      setLoading(false);
    }
  };

  const sortCases = (sort : string) => {
    const sortedCases = [...cases];
    if (sort === "amount") {
      sortedCases.sort((a, b) => b.amount - a.amount);
    } else if (sort === "date") {
      sortedCases.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }
    setCases(sortedCases);
  }

  useEffect(() => {
    fetchCases();
    sortCases("");
  }, []);

  const handleRowClick = (caseId: string) => {
    router.push(`/cases/${caseId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                Risk Assessment Dashboard
              </h1>
              <div className="flex gap-2">
                <p className="mt-1 text-sm text-gray-500">
                  Flagged banking transactions requiring review
                </p>
              </div>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <Link
                href="/report"
                className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Generate Report
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && <LoadingState message="Loading cases..." rows={5} />}

        {error && (
          <ErrorState message={error} onRetry={fetchCases} />
        )}

        {!loading && !error && cases.length === 0 && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No cases found
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              No flagged transactions to display.
            </p>
          </div>
        )}

        {!loading && !error && cases.length > 0 && (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex gap-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Flagged Transactions ({cases.length})
              </h3>
              <input className="border rounded-md w-50 px-2" placeholder="Search Name" value={queryName} onChange={(e) => setQueryName(e.target.value)}/>
              <input className="border rounded-md w-50 px-2" placeholder="Search Country" value={queryCountry} onChange={(e) => setQueryCountry(e.target.value)}/>
              <div className="flex px-2 gap-2">
                <label>Select Risk:</label>
                  <select className="border rounded-md px-2" id="riskDropDown" name="riskSelection" onChange={(e) => setRisk(e.target.value)}>
                    <option value={1000}>All</option>
                    <option value={0}>Low Risk</option>
                    <option value={0.4}>Medium Risk</option>
                    <option value={0.7}>High Risk</option>
                  </select>
              </div>
              <div className="flex px-2 gap-2">
                <label>Select Status:</label>
                  <select className="border rounded-md px-2" id="statusDropDown" name="statusSelection" onChange={(e) => setStatus(e.target.value)}>
                    <option value="all">All</option>
                    <option value="new">New</option>
                    <option value="reviewing">Reviewing</option>
                    <option value="resolved">Resolved</option>
                  </select>
              </div>
              <div className="flex px-2 gap-2">
                <label>Sort by:</label>
                  <select className="border rounded-md px-2" id="sortDropDown" name="sortSelection" onChange={(e) => sortCases(e.target.value)}>
                    <option value="n/a"></option>
                    <option value="amount">Amount</option>
                    <option value="date">Date</option>
                  </select>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Customer
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Amount
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Country
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Risk Score
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Status
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  { /* this filtering is absolute cancer but it works */}
                  {cases.filter((caseItem) => (caseItem.customer_name.toLowerCase().includes(queryName.toString().toLowerCase()) && caseItem.country.toLowerCase().includes(queryCountry.toString().toLowerCase()) && (risk === "0.7" ? caseItem.risk_score >= 0.7 : (risk === "0.4" ? caseItem.risk_score < 0.7 && caseItem.risk_score >= 0.4 : (risk === "0" ? caseItem.risk_score >= 0 && caseItem.risk_score < 0.4 : caseItem.risk_score >= 0))) && (status === "all" ? caseItem.status.includes("") : caseItem.status === status))).map((caseItem) => (
                    <tr
                      key={caseItem.id}
                      onClick={() => handleRowClick(caseItem.id)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {caseItem.customer_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(caseItem.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {caseItem.country}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <RiskBadge score={caseItem.risk_score} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <StatusBadge status={caseItem.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(caseItem.created_at)}
                      </td>
                    </tr>
                  ))}
                  
                  {/*}
                  {cases.map((caseItem) => (
                    <tr
                      key={caseItem.id}
                      onClick={() => handleRowClick(caseItem.id)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {caseItem.customer_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(caseItem.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {caseItem.country}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <RiskBadge score={caseItem.risk_score} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <StatusBadge status={caseItem.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(caseItem.created_at)}
                      </td>
                    </tr>
                  ))}
                  */}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

