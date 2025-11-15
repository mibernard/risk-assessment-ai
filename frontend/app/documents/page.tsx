"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  getDocuments,
  uploadDocument,
  deleteDocument,
  DocumentMetadata,
  DocumentUploadResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/LoadingState";
import { ErrorState } from "@/components/ErrorState";
import {
  FileText,
  Upload,
  Trash2,
  CheckCircle,
  Clock,
  FileIcon,
  ArrowLeft,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<DocumentUploadResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocuments();
      setDocuments(response.documents);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadSuccess(null);

    try {
      const result = await uploadDocument(file);
      setUploadSuccess(result);
      await fetchDocuments();
      
      // Clear success message after 5 seconds
      setTimeout(() => setUploadSuccess(null), 5000);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDelete = async (documentId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      await deleteDocument(documentId);
      await fetchDocuments();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  if (loading) {
    return (
      <div className="container mx-auto py-10">
        <LoadingState message="Loading documents..." />
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
          <h1 className="text-3xl font-bold">Compliance Documents</h1>
          <p className="text-muted-foreground">
            Manage compliance documents for AI-powered risk analysis using IBM Docling
          </p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.md,.txt"
            onChange={handleFileChange}
            className="hidden"
          />
          <Button onClick={handleUploadClick} disabled={uploading} className="gap-2">
            <Upload className="h-4 w-4" />
            {uploading ? "Uploading..." : "Upload Document"}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Alert */}
      {uploadSuccess && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-800">Upload Successful</AlertTitle>
          <AlertDescription className="text-green-700">
            {uploadSuccess.message} Extracted {uploadSuccess.chunks_extracted} text chunks.
          </AlertDescription>
        </Alert>
      )}

      {/* Info Card */}
      <Card className="mb-6 border-dashed">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            About Compliance Documents
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            Upload compliance documents (AML Policy, KYC Guidelines, Sanctions lists) to enhance
            AI-powered risk assessment with <strong>RAG (Retrieval Augmented Generation)</strong>.
          </p>
          <p className="flex items-center gap-2">
            <span className="font-semibold">Powered by:</span>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-mono">
              IBM Docling
            </span>
            <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-mono">
              IBM watsonx.ai
            </span>
          </p>
          <p className="text-xs">
            Supported formats: <strong>PDF, DOCX, Markdown, TXT</strong>
          </p>
        </CardContent>
      </Card>

      {/* Documents Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            Uploaded Documents ({documents.length})
          </h2>
        </div>

        {documents.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <FileIcon className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">No documents uploaded yet</p>
              <p className="text-sm text-muted-foreground mb-4">
                Upload your first compliance document to get started
              </p>
              <Button onClick={handleUploadClick} variant="outline" className="gap-2">
                <Upload className="h-4 w-4" />
                Upload Document
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {documents.map((doc) => (
              <Card key={doc.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <FileText className="h-5 w-5 text-primary flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base truncate">{doc.filename}</CardTitle>
                        <CardDescription className="text-xs">{doc.file_type}</CardDescription>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      className="h-8 w-8 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Status */}
                  <div className="flex items-center gap-2">
                    {doc.processed ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600 font-medium">Processed</span>
                      </>
                    ) : (
                      <>
                        <Clock className="h-4 w-4 text-yellow-600" />
                        <span className="text-sm text-yellow-600 font-medium">Processing...</span>
                      </>
                    )}
                  </div>

                  {/* Metadata */}
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div className="flex justify-between">
                      <span>File Size:</span>
                      <span className="font-medium">{formatFileSize(doc.size_bytes)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Text Chunks:</span>
                      <span className="font-medium">{doc.chunk_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Uploaded:</span>
                      <span className="font-medium text-xs">
                        {formatDateTime(doc.uploaded_at)}
                      </span>
                    </div>
                  </div>

                  {/* Docling Badge */}
                  {doc.processed && doc.chunk_count > 0 && (
                    <div className="pt-2 border-t">
                      <span className="text-xs text-muted-foreground">
                        Extracted with{" "}
                        <span className="font-semibold text-blue-600">IBM Docling</span>
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

