import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="p-8 bg-red-50 text-red-900 h-screen flex flex-col items-center justify-center">
                    <h1 className="text-3xl font-bold mb-4">Something went wrong.</h1>
                    <pre className="bg-white p-4 rounded border border-red-200 shadow-sm max-w-2xl overflow-auto">
                        {this.state.error?.toString()}
                    </pre>
                </div>
            );
        }

        return this.props.children;
    }
}
