import React from 'react';
import { Upload, AlertCircle } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import axios from 'axios';
import type { ExtractedData } from '../types';

interface UploadSectionProps {
    onDataExtracted: (data: ExtractedData, filename: string) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onDataExtracted }) => {
    const [file, setFile] = React.useState<File | null>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            if (f.type !== 'application/pdf') {
                setError("Please upload a PDF file.");
                return;
            }
            setFile(f);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post('/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Ensure data fits the expected shape before passing it up
            if (res.data && res.data.extracted_data) {
                onDataExtracted(res.data.extracted_data, res.data.filename);
            } else {
                throw new Error("Invalid response format from server");
            }

        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.error || "Upload failed. Please check the backend connection.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="upload" className="mb-12">
            <Card className="p-8 border-2 border-slate-200 bg-white text-center shadow-lg">
                <div className="flex flex-col items-center justify-center gap-4">
                    <div className="bg-blue-50 p-4 rounded-full border-2 border-blue-100 mb-2">
                        <Upload className="w-8 h-8 text-blue-500" />
                    </div>

                    <h2 className="text-2xl font-bold">Upload Patient Report</h2>
                    <p className="text-muted-foreground max-w-md mx-auto mb-6">
                        Select a PDF medical report to analyze.
                    </p>

                    <div className="flex flex-col items-center gap-4 w-full max-w-xs">
                        <div className="relative w-full">
                            <input
                                type="file"
                                id="pdf-upload"
                                accept=".pdf"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                            />
                            <Button variant="secondary" className="w-full pointer-events-none">
                                {file ? file.name : "Select PDF File"}
                            </Button>
                        </div>

                        {file && (
                            <Button onClick={handleUpload} disabled={isLoading} className="w-full animate-popIn">
                                {isLoading ? "Analyzing..." : "Upload & Analyze"}
                            </Button>
                        )}
                    </div>

                    {error && (
                        <div className="mt-6 text-red-500 font-bold bg-red-50 px-4 py-3 rounded border border-red-200 flex items-center gap-2 animate-shake">
                            <AlertCircle size={16} /> {error}
                        </div>
                    )}
                </div>
            </Card>
        </section>
    );
};
