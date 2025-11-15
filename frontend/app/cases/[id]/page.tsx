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
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null);
  const [complianceAnalysis, setComplianceAnalysis] =
    useState<ComplianceAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [explaining, setExplaining] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [riskCategory, setRiskCategory] = useState<RiskCategory | null>(null);
  const router = useRouter();

  const fetchCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCase(id);
      setCaseData(data);

      // If explanation was previously generated, fetch it
      if (data.explanation_generated) {
        try {
          const explanationData = await getExplanation(id);
          if (explanationData) {
            setExplanation(explanationData);
          }
        } catch (err) {
          console.error("Failed to fetch stored explanation:", err);
        }
      }

      // Try to fetch previously calculated risk score
      try {
        const riskScoreData = await getRiskScore(id);
        if (riskScoreData) {
          setRiskScore(riskScoreData);
        }
      } catch (err) {
        // Risk score might not exist yet, that's okay
        console.debug("No stored risk score found");
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
    }
    catch (err) {
      setError((err as Error).message);
    }
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [id]);

  const handleExplainRisk = async () => {
    if (!caseData) return;

    setExplaining(true);
    setError(null);
    try {
      const explanationData = await explainCase(caseData.id);
      setExplanation(explanationData);
      // Update case to mark explanation as generated
      setCaseData({ ...caseData, explanation_generated: true });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setExplaining(false);
    }
  };

  const handleCalculateRisk = async () => {
    if (!caseData) return;

    setCalculating(true);
    setError(null);
    try {
      const riskData = await calculateRiskScore(caseData.id);
      setRiskScore(riskData);
      // Update case with new risk score
      setCaseData({ ...caseData, risk_score: riskData.risk_score });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setCalculating(false);
    }
  };

  const handleAnalyzeCompliance = async () => {
    if (!caseData) return;

    setAnalyzing(true);
    setError(null);
    try {
      const complianceData = await analyzeCompliance(caseData.id, true);
      setComplianceAnalysis(complianceData);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAnalyzing(false);
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
            disabled={analyzing}
            variant="outline"
            className="gap-2"
          >
            <FileSearch className="h-4 w-4" />
            {analyzing ? "Analyzing..." : "Compliance Analysis"}
          </Button>
          <Button
            onClick={handleCalculateRisk}
            disabled={calculating}
            variant="outline"
            className="gap-2"
          >
            <Calculator className="h-4 w-4" />
            {calculating ? "Calculating..." : "Calculate Risk Score"}
          </Button>
          <Button
            onClick={handleExplainRisk}
            disabled={explaining || caseData.explanation_generated}
            className="gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {explaining
              ? "Analyzing..."
              : caseData.explanation_generated
              ? "Explanation Generated"
              : "Explain Risk"}
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
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Assessment</CardTitle>
            <CardDescription>Current status and risk level</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col gap-2">
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Risk Score
              </p>
              <p>
                Risk Category: <span className="font-semibold">{riskCategory ? riskCategory.risk_category : "Nothing in risk_category"}</span>
              </p>
              <p>
                <span className="font-semibold">Reasoning:</span> {riskCategory ? riskCategory.reasoning : "Nothing in reasoning"}
              </p>
              <RiskBadge score={caseData.risk_score} />
            </div>
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

      {/* AI Risk Score */}
      {riskScore && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Calculator className="h-5 w-5 text-primary" />
              <CardTitle>AI Risk Score</CardTitle>
            </div>
            <CardDescription>
              Calculated by {riskScore.model_used} • Time:{" "}
              {riskScore.generation_time_ms}ms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Risk Score */}
            <div>
              <h3 className="text-lg font-semibold mb-3">
                Calculated Risk Score
              </h3>
              <div className="flex items-center gap-4">
                <div className="text-4xl font-bold">
                  {(riskScore.risk_score * 100).toFixed(0)}%
                </div>
                <RiskBadge score={riskScore.risk_score} />
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Risk Level:{" "}
                <span className="font-semibold">{riskScore.risk_level}</span>
              </p>
            </div>

            {/* Reasoning */}
            <div>
              <h3 className="text-lg font-semibold mb-2">AI Reasoning</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {riskScore.reasoning}
              </p>
            </div>

            {/* Metadata */}
            <div className="pt-4 border-t">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Tokens Consumed</p>
                  <p className="font-medium">{riskScore.tokens_consumed}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generation Time</p>
                  <p className="font-medium">
                    {riskScore.generation_time_ms}ms
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generated At</p>
                  <p className="font-medium">
                    {new Date(riskScore.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Explanation */}
      {explanation && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle>AI Risk Explanation</CardTitle>
            </div>
            <CardDescription>
              Generated by {explanation.model_used} • Confidence:{" "}
              {(explanation.confidence * 100).toFixed(0)}% • Time:{" "}
              {explanation.generation_time_ms}ms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Rationale */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Rationale</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {explanation.rationale}
              </p>
            </div>

            {/* Recommended Action */}
            <div>
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                Recommended Action
              </h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {explanation.recommended_action}
              </p>
            </div>

            {/* Metadata */}
            <div className="pt-4 border-t">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Tokens Consumed</p>
                  <p className="font-medium">{explanation.tokens_consumed}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Confidence</p>
                  <p className="font-medium">
                    {(explanation.confidence * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generation Time</p>
                  <p className="font-medium">
                    {explanation.generation_time_ms}ms
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generated At</p>
                  <p className="font-medium">
                    {new Date(explanation.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Prompt to generate explanation */}
      {!explanation && !caseData.explanation_generated && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-10">
            <Sparkles className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              No AI Explanation Yet
            </h3>
            <p className="text-muted-foreground text-center mb-4">
              Click "Explain Risk" to generate an AI-powered analysis of this
              transaction
            </p>
            <Button onClick={handleExplainRisk} disabled={explaining}>
              {explaining ? "Analyzing..." : "Generate Explanation"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
