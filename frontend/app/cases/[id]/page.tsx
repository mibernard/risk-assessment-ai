"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import {
  getCase,
  getExplanation,
  getRiskScore,
  explainCase,
  calculateRiskScore,
  analyzeCompliance,
  Case,
  Explanation,
  RiskScore,
  ComplianceAnalysis,
  RiskCategory,
  getRiskCategory,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RiskBadge } from "@/components/RiskBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import {
  ArrowLeft,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Calculator,
  FileSearch,
  Shield,
  FileText,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface CaseDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function CaseDetailPage({ params }: CaseDetailPageProps) {
  const { id } = use(params);
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [riskAnalysis, setRiskAnalysis] = useState<{
    score: RiskScore;
    explanation: Explanation;
  } | null>(null);
  const [complianceAnalysis, setComplianceAnalysis] =
    useState<ComplianceAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzingRisk, setAnalyzingRisk] = useState(false);
  const [analyzingCompliance, setAnalyzingCompliance] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [riskCategory, setRiskCategory] = useState<RiskCategory | null>(null);
  const router = useRouter();

  const fetchCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCase(id);
      setCaseData(data);

      // Try to fetch previously generated AI analysis
      if (data.explanation_generated) {
        try {
          const [explanationData, riskScoreData] = await Promise.all([
            getExplanation(id).catch(() => null),
            getRiskScore(id).catch(() => null),
          ]);

          if (explanationData && riskScoreData) {
            setRiskAnalysis({
              score: riskScoreData,
              explanation: explanationData,
            });
          }
        } catch (err) {
          console.debug("No stored analysis found");
        }
      }
    } catch (err) {
      setError((err as Error).message);
    }

    // try to fetch risk category
    try {
      const riskCategoryData = await getRiskCategory(id);
      if (riskCategoryData) {
        setRiskCategory(riskCategoryData);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [id]);

  const handleAnalyzeRisk = async () => {
    if (!caseData) return;

    setAnalyzingRisk(true);
    setError(null);
    try {
      // Run both AI analyses in parallel
      const [riskScoreData, explanationData] = await Promise.all([
        calculateRiskScore(caseData.id),
        explainCase(caseData.id),
      ]);

      setRiskAnalysis({
        score: riskScoreData,
        explanation: explanationData,
      });

      // Update case with new risk score and mark explanation as generated
      setCaseData({
        ...caseData,
        risk_score: riskScoreData.risk_score,
        explanation_generated: true,
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAnalyzingRisk(false);
    }
  };

  const handleAnalyzeCompliance = async () => {
    if (!caseData) return;

    setAnalyzingCompliance(true);
    setError(null);
    try {
      const complianceData = await analyzeCompliance(caseData.id, true);
      setComplianceAnalysis(complianceData);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAnalyzingCompliance(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-10">
        <LoadingState message="Loading case details..." />
      </div>
    );
  }

  if (error && !caseData) {
    return (
      <div className="container mx-auto py-10">
        <ErrorState message={error} onRetry={fetchCase} />
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="container mx-auto py-10">
        <ErrorState message="Case not found" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/dashboard")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">Case Details</h1>
          <p className="text-muted-foreground">Transaction ID: {caseData.id}</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleAnalyzeCompliance}
            disabled={analyzingCompliance}
            variant="outline"
            className="gap-2"
          >
            <FileSearch className="h-4 w-4" />
            {analyzingCompliance ? "Analyzing..." : "Check Compliance (RAG)"}
          </Button>
          <Button
            onClick={handleAnalyzeRisk}
            disabled={analyzingRisk}
            className="gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {analyzingRisk ? "Analyzing..." : "AI Risk Analysis"}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Case Information */}
      <div className="grid gap-6 md:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Customer Information</CardTitle>
            <CardDescription>Transaction details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Customer Name
              </p>
              <p className="text-lg font-semibold">{caseData.customer_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Transaction Amount
              </p>
              <p className="text-lg font-semibold">
                ${caseData.amount.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Country
              </p>
              <p className="text-lg font-semibold">{caseData.country}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Created At
              </p>
              <p className="text-lg">
                {new Date(caseData.created_at).toLocaleString()}
              </p>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm font-medium text-muted-foreground mb-3">
                AML Indicators
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Account Age</p>
                  <p className="text-lg font-semibold">
                    {caseData.account_age_days} days
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {caseData.account_age_days < 30
                      ? "⚠️ New account"
                      : caseData.account_age_days < 180
                      ? "✓ Established"
                      : "✓ Well established"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">
                    Transaction Velocity
                  </p>
                  <p className="text-lg font-semibold">
                    {caseData.transaction_count_30d} / 30d
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {caseData.transaction_count_30d >= 7
                      ? "⚠️ High velocity"
                      : caseData.transaction_count_30d >= 4
                      ? "⚠️ Elevated"
                      : "✓ Normal"}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Assessment</CardTitle>
            <CardDescription>Current status and risk level</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Risk Score
              </p>
              <RiskBadge score={caseData.risk_score} />
            </div>
            {riskCategory && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">
                  Risk Category
                </p>
                <p className="font-semibold mb-2">
                  {riskCategory.risk_category}
                </p>
                <p className="text-sm text-muted-foreground">
                  {riskCategory.reasoning}
                </p>
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Status
              </p>
              <StatusBadge status={caseData.status} />
            </div>
            {caseData.model_version && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  AI Model
                </p>
                <p className="text-sm">{caseData.model_version}</p>
              </div>
            )}
            {caseData.tokens_used && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Tokens Used
                </p>
                <p className="text-sm">
                  {caseData.tokens_used.toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Compliance Analysis - RAG-powered with IBM Docling */}
      {complianceAnalysis && (
        <Card className="mb-6 border-blue-200 bg-blue-50/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <CardTitle>Compliance Analysis (RAG)</CardTitle>
            </div>
            <CardDescription>
              AI-powered analysis using {complianceAnalysis.model_used} with IBM
              Docling • Time: {complianceAnalysis.generation_time_ms}ms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Compliance Status */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Compliance Status</h3>
              <div className="flex items-center gap-3">
                {complianceAnalysis.compliance_status === "COMPLIANT" && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-md">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-semibold">COMPLIANT</span>
                  </div>
                )}
                {complianceAnalysis.compliance_status === "REVIEW_REQUIRED" && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-md">
                    <AlertTriangle className="h-5 w-5" />
                    <span className="font-semibold">REVIEW REQUIRED</span>
                  </div>
                )}
                {complianceAnalysis.compliance_status === "NON_COMPLIANT" && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-800 rounded-md">
                    <AlertTriangle className="h-5 w-5" />
                    <span className="font-semibold">NON-COMPLIANT</span>
                  </div>
                )}
                <span className="text-sm text-muted-foreground">
                  Confidence: {(complianceAnalysis.confidence * 100).toFixed(0)}
                  %
                </span>
              </div>
            </div>

            {/* Violations */}
            {complianceAnalysis.violations.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 text-red-700">
                  Potential Violations
                </h3>
                <ul className="space-y-2">
                  {complianceAnalysis.violations.map((violation, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-red-700">{violation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Relevant Regulations */}
            <div>
              <h3 className="text-lg font-semibold mb-2">
                Relevant Regulations
              </h3>
              <ul className="space-y-2">
                {complianceAnalysis.relevant_regulations.map(
                  (regulation, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <FileText className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-muted-foreground">
                        {regulation}
                      </span>
                    </li>
                  )
                )}
              </ul>
            </div>

            {/* Recommendation */}
            <div className="bg-white rounded-lg p-4 border">
              <h3 className="text-lg font-semibold mb-2">Recommendation</h3>
              <p className="text-muted-foreground">
                {complianceAnalysis.recommendation}
              </p>
            </div>

            {/* Source Documents */}
            {complianceAnalysis.documents_used.length > 0 && (
              <div className="pt-4 border-t">
                <h3 className="text-sm font-semibold mb-2">
                  Source Documents (RAG)
                </h3>
                <div className="flex flex-wrap gap-2">
                  {complianceAnalysis.documents_used.map((doc, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-mono"
                    >
                      {doc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="pt-4 border-t">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Tokens Consumed</p>
                  <p className="font-medium">
                    {complianceAnalysis.tokens_consumed}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generation Time</p>
                  <p className="font-medium">
                    {complianceAnalysis.generation_time_ms}ms
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generated At</p>
                  <p className="font-medium">
                    {new Date(
                      complianceAnalysis.created_at
                    ).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comprehensive AI Risk Analysis */}
      {riskAnalysis && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle>AI Risk Analysis</CardTitle>
            </div>
            <CardDescription>
              Generated by {riskAnalysis.score.model_used} • Confidence:{" "}
              {(riskAnalysis.explanation.confidence * 100).toFixed(0)}%
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Risk Score */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Risk Score</h3>
              <div className="flex items-center gap-4">
                <div className="text-4xl font-bold">
                  {(riskAnalysis.score.risk_score * 100).toFixed(0)}%
                </div>
                <RiskBadge score={riskAnalysis.score.risk_score} />
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Risk Level:{" "}
                <span className="font-semibold">
                  {riskAnalysis.score.risk_level}
                </span>
              </p>
            </div>

            {/* Reasoning */}
            <div>
              <h3 className="text-lg font-semibold mb-2">AI Reasoning</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {riskAnalysis.score.reasoning}
              </p>
            </div>

            {/* Detailed Analysis */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Detailed Analysis</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {riskAnalysis.explanation.rationale}
              </p>
            </div>

            {/* Recommended Action */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-blue-900">
                <CheckCircle className="h-5 w-5 text-blue-600" />
                Recommended Action
              </h3>
              <p className="text-blue-800">
                {riskAnalysis.explanation.recommended_action}
              </p>
            </div>

            {/* Metadata */}
            <div className="pt-4 border-t">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Total Tokens</p>
                  <p className="font-medium">
                    {riskAnalysis.score.tokens_consumed +
                      riskAnalysis.explanation.tokens_consumed}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Confidence</p>
                  <p className="font-medium">
                    {(riskAnalysis.explanation.confidence * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generation Time</p>
                  <p className="font-medium">
                    {riskAnalysis.score.generation_time_ms +
                      riskAnalysis.explanation.generation_time_ms}
                    ms
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Model</p>
                  <p className="font-medium text-xs">
                    {riskAnalysis.score.model_used}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Prompt to generate AI analysis */}
      {!riskAnalysis && !caseData.explanation_generated && (
        <Card className="border-dashed mb-6">
          <CardContent className="flex flex-col items-center justify-center py-10">
            <Sparkles className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No AI Analysis Yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Click "AI Risk Analysis" to generate a comprehensive AI-powered
              assessment
            </p>
            <Button onClick={handleAnalyzeRisk} disabled={analyzingRisk}>
              <Sparkles className="h-4 w-4 mr-2" />
              {analyzingRisk ? "Analyzing..." : "Generate AI Analysis"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
