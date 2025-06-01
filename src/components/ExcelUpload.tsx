import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Download, Upload, X } from 'lucide-react';
import React, { useState } from 'react';
import { toast } from 'sonner';

interface ExcelUploadProps {
  departmentId: number;
  onUploadComplete?: (result: any) => void;
}

interface UploadResult {
  success: boolean;
  total_rows: number;
  processed: number;
  failed: number;
  errors: string[];
  created_exams: Array<{
    id: number;
    course_code: string;
    instructor: string;
    difficulty: string;
  }>;
  scheduling?: {
    success: boolean;
    message: string;
    scheduled_count?: number;
    failed_count?: number;
  };
}

export function ExcelUpload({ departmentId, onUploadComplete }: ExcelUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [autoSchedule, setAutoSchedule] = useState(true);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadResult(null);
    }
  };

  const validateFile = async () => {
    if (!file) return;

    setValidating(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/excel/validate', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.valid) {
        toast.success(`✅ Dosya doğrulandı! ${result.total_rows} satır bulundu.`);
        if (result.warnings && result.warnings.length > 0) {
          result.warnings.forEach((warning: string) => {
            toast.warning(warning);
          });
        }
      } else {
        toast.error(result.message);
        if (result.details) {
          toast.error(result.details, { duration: 8000 });
        }
      }
    } catch (error) {
      toast.error('Validation failed. Please try again.');
    } finally {
      setValidating(false);
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('department_id', departmentId.toString());
    formData.append('auto_schedule', autoSchedule.toString());

    try {
      const response = await fetch('/api/excel/upload', {
        method: 'POST',
        body: formData,
      });

      const result: UploadResult = await response.json();
      setUploadResult(result);

      if (result.success) {
        toast.success(`Successfully processed ${result.processed} exams!`);
        onUploadComplete?.(result);
      } else {
        toast.error(`Upload failed: ${result.message || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch('/api/excel/template');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sinav_verileri_template.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Template downloaded successfully!');
      } else {
        toast.error('Failed to download template');
      }
    } catch (error) {
      toast.error('Failed to download template');
    }
  };

  const clearFile = () => {
    setFile(null);
    setUploadResult(null);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'very_hard': return 'bg-red-500';
      case 'hard': return 'bg-orange-500';
      case 'normal': return 'bg-blue-500';
      case 'easy': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Template Download */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Excel Template
          </CardTitle>
          <CardDescription>
            Download the Excel template to see the required format for exam data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={downloadTemplate} variant="outline" className="w-full">
            <Download className="h-4 w-4 mr-2" />
            Download Template
          </Button>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Excel File
          </CardTitle>
          <CardDescription>
            Upload your Excel file containing exam data. The file will be processed and exams will be created automatically.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Input */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            {file && (
              <Button onClick={clearFile} variant="ghost" size="sm">
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Auto Schedule Option */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="auto-schedule"
              checked={autoSchedule}
              onChange={(e) => setAutoSchedule(e.target.checked)}
              className="rounded border-gray-300"
            />
            <label htmlFor="auto-schedule" className="text-sm font-medium">
              Automatically schedule exams after upload
            </label>
          </div>

          {/* Action Buttons */}
          {file && (
            <div className="flex gap-2">
              <Button
                onClick={validateFile}
                variant="outline"
                disabled={validating}
                className="flex-1"
              >
                {validating ? 'Validating...' : 'Validate File'}
              </Button>
              <Button
                onClick={uploadFile}
                disabled={uploading}
                className="flex-1"
              >
                {uploading ? 'Uploading...' : 'Upload & Process'}
              </Button>
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="space-y-2">
              <Progress value={50} className="w-full" />
              <p className="text-sm text-gray-600 text-center">
                Processing Excel file...
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Results */}
      {uploadResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {uploadResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
              Upload Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {uploadResult.total_rows}
                </div>
                <div className="text-sm text-gray-600">Total Rows</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {uploadResult.processed}
                </div>
                <div className="text-sm text-gray-600">Processed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {uploadResult.failed}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
            </div>

            {/* Scheduling Results */}
            {uploadResult.scheduling && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Scheduling:</strong> {uploadResult.scheduling.message}
                  {uploadResult.scheduling.scheduled_count !== undefined && (
                    <span className="ml-2">
                      ({uploadResult.scheduling.scheduled_count} scheduled, {uploadResult.scheduling.failed_count} failed)
                    </span>
                  )}
                </AlertDescription>
              </Alert>
            )}

            {/* Created Exams */}
            {uploadResult.created_exams.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Created Exams:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {uploadResult.created_exams.map((exam) => (
                    <div key={exam.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <span className="font-medium">{exam.course_code}</span>
                        <span className="text-gray-600 ml-2">{exam.instructor}</span>
                      </div>
                      <Badge className={getDifficultyColor(exam.difficulty)}>
                        {exam.difficulty}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Errors */}
            {uploadResult.errors.length > 0 && (
              <div>
                <h4 className="font-medium mb-2 text-red-600">Errors:</h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {uploadResult.errors.map((error, index) => (
                    <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      {error}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
