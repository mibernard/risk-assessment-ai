/**
 * API Client for Risk Assessment Backend
 *
 * Provides typed functions for all API endpoints.
 * See docs/API_CONTRACT.md for full specifications.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ===================================
// Type Definitions
// ===================================

export interface Case {
  id: string;
  customer_name: string;
  amount: number;
  country: string;
  risk_score: number;
  status: "new" | "reviewing" | "resolved";
  created_at: string;
  explanation_generated?: boolean;
  model_version?: string;
  tokens_used?: number;
  category?: string | "Unknown";
  account_age_days: number; // AML indicator: days since account opened
  transaction_count_30d: number; // AML indicator: transaction velocity
}

export interface Explanation {
  case_id: string;
  confidence: number;
  rationale: string;
  recommended_action: string;
  model_used: string;
  tokens_consumed: number;
  generation_time_ms: number;
  created_at: string;
}

export interface RiskCategory {
  case_id: string;
  risk_category: string;
  reasoning: string;
  model_used: string;
  tokens_consumed: number;
  generation_time_ms: number;
  created_at: string;
}

export interface RiskScore {
  case_id: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  reasoning: string;
  model_used: string;
  tokens_consumed: number;
  generation_time_ms: number;
  created_at: string;
}

export interface DocumentMetadata {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  uploaded_at: string;
  processed: boolean;
  chunk_count: number;
}

export interface DocumentListResponse {
  documents: DocumentMetadata[];
  total_count: number;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: string;
  chunks_extracted: number;
  message: string;
}

export interface ComplianceAnalysis {
  case_id: string;
  compliance_status: "COMPLIANT" | "NON_COMPLIANT" | "REVIEW_REQUIRED";
  violations: string[];
  relevant_regulations: string[];
  recommendation: string;
  confidence: number;
  documents_used: string[];
  model_used: string;
  tokens_consumed: number;
  generation_time_ms: number;
  created_at: string;
}

export interface StatusDistribution {
  new: number;
  reviewing: number;
  resolved: number;
}

export interface Report {
  summary: string;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  avg_risk: number;
  total_cases: number;
  total_amount: number;
  status_distribution: StatusDistribution;
  period_start: string;
  period_end: string;
}

export interface HealthCheck {
  status: "healthy" | "unhealthy";
  database: "connected" | "disconnected";
  watsonx_api: "available" | "unavailable";
  token_budget_remaining: number;
}

export interface TokenUsage {
  total_budget_usd: number;
  spent_usd: number;
  remaining_usd: number;
  tokens_used: number;
  requests_count: number;
  percentage_used: number;
}

// ===================================
// API Functions
// ===================================

/**
 * Fetch all cases
 * GET /cases
 */
export async function getCases(): Promise<Case[]> {
  const response = await fetch(`${API_URL}/cases`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch cases: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch single case by ID
 * GET /cases/{id}
 */
export async function getCase(id: string): Promise<Case> {
  const response = await fetch(`${API_URL}/cases/${id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Case not found");
    }
    throw new Error(`Failed to fetch case: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch stored explanation for a case
 * GET /cases/{id}/explanation
 */
export async function getExplanation(
  caseId: string
): Promise<Explanation | null> {
  const response = await fetch(`${API_URL}/cases/${caseId}/explanation`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) {
    // No explanation generated yet
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch explanation: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Generate AI explanation for a case
 * POST /explain
 */
export async function explainCase(caseId: string): Promise<Explanation> {
  const response = await fetch(`${API_URL}/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ case_id: caseId }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Case not found");
    }
    if (response.status === 429) {
      throw new Error("Token budget exceeded");
    }
    if (response.status === 503) {
      throw new Error("AI service unavailable");
    }
    throw new Error(`Failed to generate explanation: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch stored risk score for a case
 * GET /cases/{id}/risk-score
 */
export async function getRiskScore(caseId: string): Promise<RiskScore | null> {
  const response = await fetch(`${API_URL}/cases/${caseId}/risk-score`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) {
    // No risk score calculated yet
    return null;
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch risk score: ${response.statusText}`);
  }

  return response.json();
}

export async function getRiskCategory(
  caseId: string
): Promise<RiskCategory | null> {
  const response = await fetch(`${API_URL}/risk-categorize/${caseId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) {
    // No risk category calculated yet
    return null;
  }
  if (!response.ok) {
    throw new Error(`Failed to fetch risk category`);
  }

  return response.json();
}

/**
 * Calculate AI risk score for a case
 * POST /calculate-risk
 */
export async function calculateRiskScore(caseId: string): Promise<RiskScore> {
  const response = await fetch(`${API_URL}/calculate-risk`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ case_id: caseId }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Case not found");
    }
    if (response.status === 429) {
      throw new Error("Token budget exceeded");
    }
    if (response.status === 503) {
      throw new Error("AI service unavailable");
    }
    throw new Error(`Failed to calculate risk score: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Generate compliance report
 * POST /report
 */
export async function generateReport(options?: {
  case_ids?: string[];
  include_ai_summary?: boolean;
}): Promise<Report> {
  const response = await fetch(`${API_URL}/report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(options || {}),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate report: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check API health
 * GET /health
 */
export async function getHealth(): Promise<HealthCheck> {
  const response = await fetch(`${API_URL}/health`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to check health: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get token usage statistics
 * GET /admin/tokens
 */
export async function getTokenUsage(): Promise<TokenUsage> {
  const response = await fetch(`${API_URL}/admin/tokens`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch token usage: ${response.statusText}`);
  }

  return response.json();
}

// ===================================
// Document Management
// ===================================

/**
 * Get list of all uploaded compliance documents
 */
export async function getDocuments(): Promise<DocumentListResponse> {
  const response = await fetch(`${API_URL}/documents`);

  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Upload a compliance document (PDF, DOCX, MD)
 */
export async function uploadDocument(
  file: File
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    if (response.status === 400) {
      const error = await response.json();
      throw new Error(error.detail || "Invalid file type");
    }
    throw new Error(`Failed to upload document: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Delete a compliance document
 */
export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Document not found");
    }
    throw new Error(`Failed to delete document: ${response.statusText}`);
  }
}

/**
 * Analyze transaction compliance using RAG (Retrieval Augmented Generation)
 */
export async function analyzeCompliance(
  caseId: string,
  useDocuments: boolean = true
): Promise<ComplianceAnalysis> {
  const response = await fetch(`${API_URL}/analyze-compliance`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ case_id: caseId, use_documents: useDocuments }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Case not found");
    }
    if (response.status === 429) {
      throw new Error("Token budget exceeded");
    }
    if (response.status === 503) {
      throw new Error("AI service unavailable");
    }
    throw new Error(`Failed to analyze compliance: ${response.statusText}`);
  }

  return response.json();
}

// ===================================
// Utility Functions
// ===================================

/**
 * Format currency amount
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

/**
 * Format date/time
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

/**
 * Get risk level label and color
 */
export function getRiskLevel(score: number): {
  label: string;
  color: string;
  textColor: string;
} {
  if (score >= 0.7) {
    return {
      label: "High Risk",
      color: "bg-red-100",
      textColor: "text-red-700",
    };
  }
  if (score >= 0.4) {
    return {
      label: "Medium Risk",
      color: "bg-yellow-100",
      textColor: "text-yellow-700",
    };
  }
  return {
    label: "Low Risk",
    color: "bg-green-100",
    textColor: "text-green-700",
  };
}

/**
 * Get status badge color
 */
export function getStatusColor(status: Case["status"]): {
  color: string;
  textColor: string;
} {
  switch (status) {
    case "new":
      return { color: "bg-red-100", textColor: "text-red-700" };
    case "reviewing":
      return { color: "bg-yellow-100", textColor: "text-yellow-700" };
    case "resolved":
      return { color: "bg-green-100", textColor: "text-green-700" };
    default:
      return { color: "bg-gray-100", textColor: "text-gray-700" };
  }
}
