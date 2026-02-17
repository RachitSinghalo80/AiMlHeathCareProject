import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone'; // Oops, need to install this or implement manual drag/drop
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { ExtractedData } from '../types';

interface UploadSectionProps {
    onDataExtracted: (data: ExtractedData, filename: string) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onDataExtracted }) => {
    const [isDragOver, setIsDragOver] = React.useState(false);
    const [file, setFile] = React.useState<File | null>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (f: File) => {
        if (f.type !== 'application/pdf') {
            setError("Please upload a PDF file.");
            return;
        }
        setFile(f);
        setError(null);
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
            onDataExtracted(res.data.extracted_data, res.data.filename);
        } catch (err: any) {
            setError(err.response?.data?.error || "Upload failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="upload" className="mb-16">
            <div className="text-center mb-8">
                <h2 className="text-3xl md:text-4xl mb-4 font-black">Upload Medical Report</h2>
                <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                    Start by uploading a patient's lab report (PDF) to extract health data and assess clinical risks.
                </p>
            </div>

            <div className="max-w-2xl mx-auto">
                <Card className="p-8 border-dashed border-4 border-slate-300 shadow-none hover:shadow-none bg-slate-50 relative overflow-hidden group">

                    <input
                        type="file"
                        id="file-upload"
                        accept=".pdf"
                        className="hidden"
                        onChange={handleFileChange}
                    />

                    <div
                        className={`flex flex-col items-center justify-center py-12 transition-colors ${isDragOver ? 'bg-blue-50' : ''}`}
                        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                        onDragLeave={() => setIsDragOver(false)}
                        onDrop={handleDrop}
                    >
                        <div className="bg-white rounded-full p-6 border-2 border-slate-900 shadow-pop mb-6 group-hover:scale-110 transition-transform duration-300">
                            <Upload className="w-8 h-8 text-accent" />
                        </div>

                        <h3 className="text-xl font-bold mb-2">Drag & Drop PDF</h3>
                        <p className="text-muted-foreground mb-6">or click to browse</p>

                        <label htmlFor="file-upload">
                            <Button as="span" className="cursor-pointer" onClick={() => document.getElementById('file-upload')?.click()}>
                                Choose File
                            </Button>
                        </label>
                    </div>

                    <AnimatePresence>
                        {file && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="absolute inset-0 bg-white z-10 flex flex-col items-center justify-center p-8"
                            >
                                <div className="flex flex-col items-center">
                                    <FileText className="w-16 h-16 text-secondary mb-4" />
                                    <p className="font-bold text-lg mb-1">{file.name}</p>
                                    <p className="text-sm text-muted-foreground mb-6">{(file.size / 1024 / 1024).toFixed(2)} MB</p>

                                    <div className="flex gap-4">
                                        <Button variant="secondary" onClick={() => setFile(null)}>Change</Button>
                                        <Button onClick={handleUpload} disabled={isLoading}>
                                            {isLoading ? "Extracting..." : "Analyze Report"}
                                        </Button>
                                    </div>

                                    {error && (
                                        <div className="mt-4 flex items-center gap-2 text-red-500 font-bold bg-red-50 px-4 py-2 rounded-lg border border-red-200">
                                            <AlertCircle size={20} />
                                            {error}
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </Card>
            </div>
        </section>
    );
};
