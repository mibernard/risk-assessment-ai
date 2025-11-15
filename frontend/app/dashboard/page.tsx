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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, SortAsc, FileText, X, FolderOpen } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [queryName, setQueryName] = useState<string | number>("");
  const [queryCountry, setQueryCountry] = useState<string | number>("");
  const [risk, setRisk] = useState<string>("1000");
  const [riskCategory, setRiskCategory] = useState<string>("");
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

  const sortCases = (sort: string) => {
    const sortedCases = [...cases];
    if (sort === "amount") {
      sortedCases.sort((a, b) => b.amount - a.amount);
    } else if (sort === "date") {
      sortedCases.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    }
    setCases(sortedCases);
  };

  useEffect(() => {
    fetchCases();
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
            <div className="mt-4 flex md:mt-0 md:ml-4 gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setQueryName("");
                  setQueryCountry("");
                  setRisk("1000");
                  setStatus("all");
                  setRiskCategory("");
                }}
              >
                <X className="h-4 w-4 mr-2" />
                Clear Filters
              </Button>
              <Button asChild variant="outline">
                <Link href="/documents">
                  <FolderOpen className="h-4 w-4 mr-2" />
                  Documents
                </Link>
              </Button>
              <Button asChild>
                <Link href="/report">
                  <FileText className="h-4 w-4 mr-2" />
                  Generate Report
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && <LoadingState message="Loading cases..." rows={5} />}

        {error && <ErrorState message={error} onRetry={fetchCases} />}

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
          <div className="space-y-4">
            {/* Filters Card */}
            <Card>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <Filter className="h-5 w-5" />
                      Filters & Search
                    </h3>
                    <span className="text-sm text-muted-foreground">
                      {
                        cases.filter(
                          (caseItem) =>
                            caseItem.customer_name
                              .toLowerCase()
                              .includes(queryName.toString().toLowerCase()) &&
                            caseItem.country
                              .toLowerCase()
                              .includes(
                                queryCountry.toString().toLowerCase()
                              ) &&
                            (risk === "0.7"
                              ? caseItem.risk_score >= 0.7
                              : risk === "0.4"
                              ? caseItem.risk_score < 0.7 &&
                                caseItem.risk_score >= 0.4
                              : risk === "0"
                              ? caseItem.risk_score >= 0 &&
                                caseItem.risk_score < 0.4
                              : caseItem.risk_score >= 0) &&
                            (status === "all"
                              ? caseItem.status.includes("")
                              : caseItem.status === status)
                        ).length
                      }{" "}
                      results
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    {/* Search Name */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                        <Search className="h-4 w-4" />
                        Customer Name
                      </label>
                      <Input
                        placeholder="Search by name..."
                        value={queryName}
                        onChange={(e) => setQueryName(e.target.value)}
                        className="w-full"
                      />
                    </div>

                    {/* Search Country */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                        <Search className="h-4 w-4" />
                        Country
                      </label>
                      <Input
                        placeholder="Search by country..."
                        value={queryCountry}
                        onChange={(e) => setQueryCountry(e.target.value)}
                        className="w-full"
                      />
                    </div>

                    {/* Risk Level */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Risk Level
                      </label>
                      <Select value={risk} onValueChange={setRisk}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select risk level" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1000">All Risk Levels</SelectItem>
                          <SelectItem value="0">Low Risk (&lt; 0.4)</SelectItem>
                          <SelectItem value="0.4">
                            Medium Risk (0.4-0.7)
                          </SelectItem>
                          <SelectItem value="0.7">High Risk (≥ 0.7)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Risk Category */}
                    <div className="space y-2">
                      <label className="text-sm font-medium text-muted-foreground">Risk Category</label>
                      <Select value={riskCategory} onValueChange={setRiskCategory}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select risk category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Fraud">Fraud</SelectItem>
                          <SelectItem value="Money Laundering">Money Laundering</SelectItem>
                          <SelectItem value="Sanctions">
                            Sanctions
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Status */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Status
                      </label>
                      <Select value={status} onValueChange={setStatus}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Statuses</SelectItem>
                          <SelectItem value="new">New</SelectItem>
                          <SelectItem value="reviewing">Reviewing</SelectItem>
                          <SelectItem value="resolved">Resolved</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Sort */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                        <SortAsc className="h-4 w-4" />
                        Sort By
                      </label>
                      <Select onValueChange={sortCases} defaultValue="">
                        <SelectTrigger>
                          <SelectValue placeholder="Choose sorting..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="amount">
                            Amount (High to Low)
                          </SelectItem>
                          <SelectItem value="date">
                            Date (Newest First)
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Table Card */}
            <Card>
              <CardContent className="p-0">
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
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Category
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {/* this filtering is absolute cancer but it works */}
                      {cases
                        .filter(
                          (caseItem) =>
                            caseItem.customer_name
                              .toLowerCase()
                              .includes(queryName.toString().toLowerCase()) &&
                            caseItem.country
                              .toLowerCase()
                              .includes(
                                queryCountry.toString().toLowerCase()
                              ) &&
                            (risk === "0.7"
                              ? caseItem.risk_score >= 0.7
                              : risk === "0.4"
                              ? caseItem.risk_score < 0.7 &&
                                caseItem.risk_score >= 0.4
                              : risk === "0"
                              ? caseItem.risk_score >= 0 &&
                                caseItem.risk_score < 0.4
                              : caseItem.risk_score >= 0) &&
                            (status === "all"
                              ? caseItem.status.includes("")
                              : caseItem.status === status) &&
                            (riskCategory === ""
                              ? caseItem.category
                                  .toLowerCase()
                                  .includes("")
                              : caseItem.category === riskCategory)
                        )
                        .map((caseItem) => (
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
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {caseItem.category}
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
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
