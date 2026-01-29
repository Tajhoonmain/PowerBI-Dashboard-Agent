import { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useDashboard } from '@/contexts/DashboardContext';
import { Dataset, ColumnSchema } from '@/types/dashboard';
import Papa from 'papaparse';
import { cn } from '@/lib/utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function DatasetUpload() {
  const { addDataset } = useDashboard();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<{
    rowCount: number;
    schema: ColumnSchema[];
    fileName: string;
  } | null>(null);

  const detectColumnType = (values: any[]): { type: ColumnSchema['type']; confidence: number } => {
    const sample = values.filter(v => v != null && v !== '').slice(0, 100);
    
    if (sample.length === 0) return { type: 'string', confidence: 0.5 };

    const numericCount = sample.filter(v => !isNaN(Number(v))).length;
    const dateCount = sample.filter(v => !isNaN(Date.parse(v))).length;
    const boolCount = sample.filter(v => 
      v === 'true' || v === 'false' || v === true || v === false
    ).length;

    const numericRatio = numericCount / sample.length;
    const dateRatio = dateCount / sample.length;
    const boolRatio = boolCount / sample.length;

    if (boolRatio > 0.8) return { type: 'boolean', confidence: boolRatio };
    if (numericRatio > 0.8) return { type: 'number', confidence: numericRatio };
    if (dateRatio > 0.6) return { type: 'date', confidence: dateRatio };
    
    return { type: 'string', confidence: 1 - Math.max(numericRatio, dateRatio, boolRatio) };
  };

  const processFile = useCallback(async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setUploadProgress({ rowCount: 0, schema: [], fileName: file.name });

    // First, upload to backend
    try {
      // Validate file before upload
      console.log('[UPLOAD] File details:', {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      });

      if (!file || file.size === 0) {
        const errorMsg = file ? 'File is empty (0 bytes). Please select a valid CSV file.' : 'No file selected.';
        console.error('[UPLOAD] Validation failed:', errorMsg);
        setUploadError(errorMsg);
        setIsUploading(false);
        setUploadProgress(null);
        return;
      }

      // Verify file is readable
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        setUploadError('File is too large. Maximum size is 100MB.');
        setIsUploading(false);
        setUploadProgress(null);
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      
      console.log('[UPLOAD] FormData created, file appended. FormData size check:', formData.has('file'));

      console.log('[UPLOAD] Starting upload to:', `${API_BASE}/api/v1/datasets/upload`);
      console.log('[UPLOAD] File:', file.name, 'Size:', file.size, 'Type:', file.type);

      const uploadResponse = await fetch(`${API_BASE}/api/v1/datasets/upload`, {
        method: 'POST',
        body: formData,
      });

      console.log('[UPLOAD] Response status:', uploadResponse.status, uploadResponse.statusText);

      if (!uploadResponse.ok) {
        let errorMessage = 'Upload failed';
        try {
          const errorData = await uploadResponse.json();
          console.error('[UPLOAD] Error response:', errorData);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          const errorText = await uploadResponse.text();
          console.error('[UPLOAD] Error text:', errorText);
          errorMessage = errorText || uploadResponse.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      console.log('[UPLOAD] Upload successful');

      const backendDataset = await uploadResponse.json();
      console.log('[UPLOAD] Backend dataset:', { 
        id: backendDataset.id, 
        name: backendDataset.name, 
        rowCount: backendDataset.rowCount,
        columns: backendDataset.columns?.length,
        data: backendDataset.data?.length 
      });

      // Use backend data directly - it's already processed and validated
      if (!backendDataset.data || backendDataset.data.length === 0) {
        console.error('[UPLOAD] Backend returned empty data');
        setIsUploading(false);
        setUploadProgress(null);
        setUploadError('Backend processed file but returned no data. Please check your file format.');
        return;
      }

      // Update progress with schema info
      if (backendDataset.columns && backendDataset.columns.length > 0) {
        setUploadProgress(prev => prev ? { 
          ...prev, 
          schema: backendDataset.columns,
          rowCount: backendDataset.rowCount 
        } : null);
      }

      // Create dataset from backend response
      const dataset: Dataset = {
        id: backendDataset.id,
        name: backendDataset.name,
        data: backendDataset.data, // Use backend data (already limited to 100 rows)
        columns: backendDataset.columns, // Use backend-detected columns
        rowCount: backendDataset.rowCount,
        uploadedAt: new Date(backendDataset.uploadedAt || new Date()),
      };

      console.log('[UPLOAD] Adding dataset to context:', dataset.id);
      addDataset(dataset);
      setIsUploading(false);
      setUploadProgress(null);
    } catch (error) {
      console.error('Upload error:', error);
      setIsUploading(false);
      setUploadProgress(null);
      setUploadError(error instanceof Error ? error.message : 'Upload failed');
    }
  }, [addDataset]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
      processFile(file);
    } else {
      setUploadError('Please upload a CSV file');
    }
  }, [processFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  }, [processFile]);

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={cn(
        'relative p-8 rounded-xl border-2 border-dashed transition-all duration-300',
        'bg-gradient-to-br from-[#1a1f2e]/40 to-[#0a0e14]/40 backdrop-blur-sm',
        isDragging
          ? 'border-[#00d9ff] glow-cyan scale-[1.02]'
          : 'border-white/10 hover:border-[#00d9ff]/50'
      )}
    >
      <input
        type="file"
        accept=".csv,.xlsx,.xls,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        onChange={handleFileInput}
        disabled={isUploading}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        id="file-upload"
      />

      {uploadError && (
        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-sm text-red-400">{uploadError}</p>
        </div>
      )}

      {!isUploading && !uploadProgress ? (
        <div className="text-center space-y-4">
          <div className="inline-block p-6 rounded-2xl bg-[#00d9ff]/10 border border-[#00d9ff]/20 transition-transform duration-300 hover:scale-110">
            <Upload className="w-12 h-12 text-[#00d9ff]" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white mb-2">Upload Dataset</h3>
            <p className="text-sm text-white/60">
              Drag and drop your CSV file here, or click to browse
            </p>
          </div>
          <div className="flex items-center justify-center gap-2 text-xs text-white/40 font-mono">
            <FileText className="w-4 h-4" />
            <span>Supports .CSV, .XLSX files</span>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-[#00d9ff]/10 border border-[#00d9ff]/20 animate-pulse">
              <FileText className="w-8 h-8 text-[#00d9ff]" />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-white font-mono">{uploadProgress?.fileName}</h4>
              <p className="text-sm text-[#00d9ff] font-mono">
                {isUploading ? 'Uploading...' : 'Processing...'} {uploadProgress?.rowCount.toLocaleString()} rows
              </p>
            </div>
            {uploadProgress?.schema && uploadProgress.schema.length > 0 && (
              <CheckCircle className="w-6 h-6 text-green-400" />
            )}
          </div>

          {uploadProgress?.schema && uploadProgress.schema.length > 0 && (
            <div className="space-y-2">
              <h5 className="text-xs font-bold text-white/60 uppercase tracking-wider">
                Detected Schema
              </h5>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {uploadProgress.schema.slice(0, 9).map((col, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg glass border border-white/10 space-y-1"
                  >
                    <div className="text-sm font-mono text-white/90 truncate">{col.name}</div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[#00d9ff] font-bold uppercase">{col.type}</span>
                      <span className="text-white/40">
                        {Math.round(col.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              {uploadProgress.schema.length > 9 && (
                <p className="text-xs text-white/40 text-center">
                  + {uploadProgress.schema.length - 9} more columns
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
