"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { generateReport, Report } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import { ArrowLeft, FileText, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function ReportPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const reportData = await generateReport({ include_ai_summary: true });
      setReport(reportData);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="container mx-auto py-10">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">Compliance Report</h1>
          <p className="text-muted-foreground">Generate AI-powered risk assessment summary</p>
        </div>
        <Button onClick={handleGenerateReport} disabled={loading} className="gap-2">
          <FileText className="h-4 w-4" />
          {loading ? "Generating..." : "Generate Report"}
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <div className="mb-6">
          <LoadingState message="Generating report with AI analysis..." />
        </div>
      )}

      {/* Report Display */}
      {report && !loading && (
        <div className="space-y-6">
          {/* Report Period */}
          <Card>
            <CardHeader>
              <CardTitle>Report Period</CardTitle>
              <CardDescription>Analysis timeframe and overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">From</p>
                  <p className="font-semibold">{formatDate(report.period_start)}</p>
                </div>
                <span className="text-muted-foreground">→</span>
                <div>
                  <p className="text-muted-foreground">To</p>
                  <p className="font-semibold">{formatDate(report.period_end)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Key Metrics */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{report.total_cases}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Analyzed transactions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(report.total_amount)}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Transaction volume
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Risk</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(report.avg_risk * 100).toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Mean risk score
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Risk Cases</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{report.high_risk_count}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Require immediate attention
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Risk Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Breakdown by risk level</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">High Risk</span>
                    <span className="text-sm text-muted-foreground">{report.high_risk_count}</span>
                  </div>
                  <div className="w-full bg-red-100 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{
                        width: `${(report.high_risk_count / report.total_cases) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {((report.high_risk_count / report.total_cases) * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Medium Risk</span>
                    <span className="text-sm text-muted-foreground">{report.medium_risk_count}</span>
                  </div>
                  <div className="w-full bg-yellow-100 rounded-full h-2">
                    <div
                      className="bg-yellow-500 h-2 rounded-full"
                      style={{
                        width: `${(report.medium_risk_count / report.total_cases) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {((report.medium_risk_count / report.total_cases) * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Low Risk</span>
                    <span className="text-sm text-muted-foreground">{report.low_risk_count}</span>
                  </div>
                  <div className="w-full bg-green-100 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{
                        width: `${(report.low_risk_count / report.total_cases) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {((report.low_risk_count / report.total_cases) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Case Status</CardTitle>
              <CardDescription>Current workflow distribution</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">
                    {report.status_distribution.new}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">New</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-600">
                    {report.status_distribution.reviewing}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Reviewing</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {report.status_distribution.resolved}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">Resolved</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Summary */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary" />
                <CardTitle>AI-Generated Summary</CardTitle>
              </div>
              <CardDescription>Executive overview powered by IBM watsonx.ai</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
                {report.summary}
              </p>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <Button variant="outline" onClick={() => router.push("/dashboard")}>
              Back to Dashboard
            </Button>
            <Button onClick={() => window.print()} className="gap-2">
              <FileText className="h-4 w-4" />
              Print Report
            </Button>
          </div>
        </div>
      )}

      {/* Initial State - No Report Yet */}
      {!report && !loading && !error && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-20">
            <FileText className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Report Generated</h3>
            <p className="text-muted-foreground text-center mb-6 max-w-md">
              Click "Generate Report" to create an AI-powered compliance report with risk
              analysis and recommendations
            </p>
            <Button onClick={handleGenerateReport} size="lg" className="gap-2">
              <FileText className="h-5 w-5" />
              Generate Report
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

