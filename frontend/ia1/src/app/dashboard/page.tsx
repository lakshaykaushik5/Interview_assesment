"use client"

import { Button } from "@/components/ui/button";
import { signOut } from "next-auth/react";
import { useNavbarContext } from "../states/NavbarContext";
import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, CheckCircle, AlertCircle, CloudCog } from "lucide-react";
import { useRouter } from "next/navigation";


export default function Page() {
    const router = useRouter()
    const { setOnNavbarClick } = useNavbarContext();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [showInterviewStartButton, setShowInterviewStartButton] = useState(false)

    useEffect(() => {
        const logOutHandler = () => {
            signOut({ callbackUrl: "/" });
        };
        setOnNavbarClick(() => logOutHandler);
    }, [setOnNavbarClick]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            console.log(e.target.files[0], " target files")
            setSelectedFile(e.target.files[0]);
            setUploadStatus('idle');
            setProgress(0);
        }
    };

    const handleStartInterview = ()=>{
        console.log(" am i here")
        router.push("/Interview")
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedFile) {
            alert('Please select a file first');
            return;
        }

        setUploading(true);
        setUploadStatus('idle');
        setProgress(0);

        try {
            // Simulate progress
            const progressInterval = setInterval(() => {
                setProgress((prev) => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    return prev + 10;
                });
            }, 200);

            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', selectedFile);

            console.log(formData, " | Form Data |")

            // Replace this with your actual upload endpoint
            const response = await fetch('http://localhost:4001/v1/upload-pdf/', {
                method: 'POST',
                body: formData,
            });

            clearInterval(progressInterval);
            setProgress(100);

            if (response.ok) {
                setUploadStatus('success');
                setShowInterviewStartButton(true)
            } else {
                throw new Error('Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus('error');
            setProgress(0);
            setShowInterviewStartButton(false)

        } finally {
            setUploading(false);
        }
    };

    const getStatusIcon = () => {
        switch (uploadStatus) {
            case 'success':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'error':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            default:
                return <FileText className="h-4 w-4 text-gray-500" />;
        }
    };

    const getStatusMessage = () => {
        switch (uploadStatus) {
            case 'success':
                return 'Resume uploaded successfully!';
            case 'error':
                return 'Upload failed. Please try again.';
            default:
                return selectedFile ? `Selected: ${selectedFile.name}` : 'No file selected';
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            {showInterviewStartButton == false ? <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid w-full items-center gap-3">
                            <Label htmlFor="resume">Upload Your Resume</Label>
                            <Input
                                id="resume"
                                type="file"
                                onChange={handleFileChange}
                                accept=".pdf,.doc,.docx"
                                disabled={uploading}
                            />
                        </div>

                        {/* File status */}
                        {selectedFile && (
                            <div className="flex items-center gap-2 text-sm">
                                {getStatusIcon()}
                                <span className={
                                    uploadStatus === 'success' ? 'text-green-600' :
                                        uploadStatus === 'error' ? 'text-red-600' :
                                            'text-gray-600'
                                }>
                                    {getStatusMessage()}
                                </span>
                            </div>
                        )}

                        {/* Progress bar */}
                        {uploading && (
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span>Uploading...</span>
                                    <span>{progress}%</span>
                                </div>
                                <Progress value={progress} className="w-full" />
                            </div>
                        )}

                        {/* Submit button */}
                        <Button
                            type="submit"
                            className="w-full"
                            disabled={!selectedFile || uploading}
                        >
                            {uploading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload className="h-4 w-4 mr-2" />
                                    Upload Resume
                                </>
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>
                :
                <Card className="w-full max-w-md">
                    <CardContent className="pt-6">
                        <div className="grid w-full items-center gap-3">
                            Start the Interview
                        </div>

                        {/* Submit button */}
                        <Button
                            type="submit"
                            className="w-full"
                            onClick={handleStartInterview}
                        // disabled={!selectedFile || uploading}
                        >
                            Continue
                        </Button>
                    </CardContent>
                </Card>}
        </div>
    );
}
