"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { getCase, explainCase, Case, Explanation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskBadge } from "@/components/RiskBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import { ArrowLeft, Sparkles, CheckCircle, AlertTriangle } from "lucide-react";
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
  const [loading, setLoading] = useState(true);
  const [explaining, setExplaining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCase(id);
      setCaseData(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
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
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">Case Details</h1>
          <p className="text-muted-foreground">Transaction ID: {caseData.id}</p>
        </div>
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
              <p className="text-sm font-medium text-muted-foreground">Customer Name</p>
              <p className="text-lg font-semibold">{caseData.customer_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Transaction Amount</p>
              <p className="text-lg font-semibold">${caseData.amount.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Country</p>
              <p className="text-lg font-semibold">{caseData.country}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <p className="text-lg">{new Date(caseData.created_at).toLocaleString()}</p>
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
              <p className="text-sm font-medium text-muted-foreground mb-2">Risk Score</p>
              <RiskBadge score={caseData.risk_score} />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">Status</p>
              <StatusBadge status={caseData.status} />
            </div>
            {caseData.model_version && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">AI Model</p>
                <p className="text-sm">{caseData.model_version}</p>
              </div>
            )}
            {caseData.tokens_used && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tokens Used</p>
                <p className="text-sm">{caseData.tokens_used.toLocaleString()}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Explanation */}
      {explanation && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle>AI Risk Explanation</CardTitle>
            </div>
            <CardDescription>
              Generated by {explanation.model_used} • Confidence: {(explanation.confidence * 100).toFixed(0)}% • 
              Time: {explanation.generation_time_ms}ms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Rationale */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Rationale</h3>
              <p className="text-muted-foreground whitespace-pre-wrap">{explanation.rationale}</p>
            </div>

            {/* Recommended Action */}
            <div>
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                Recommended Action
              </h3>
              <p className="text-muted-foreground whitespace-pre-wrap">{explanation.recommended_action}</p>
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
                  <p className="font-medium">{(explanation.confidence * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generation Time</p>
                  <p className="font-medium">{explanation.generation_time_ms}ms</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Generated At</p>
                  <p className="font-medium">{new Date(explanation.created_at).toLocaleTimeString()}</p>
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
            <h3 className="text-lg font-semibold mb-2">No AI Explanation Yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Click "Explain Risk" to generate an AI-powered analysis of this transaction
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

