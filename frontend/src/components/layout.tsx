import React from 'react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <div className="min-h-screen bg-background text-foreground font-body relative">
            {/* Background Decor */}
            <div className="absolute inset-0 bg-dot-pattern opacity-40 pointer-events-none" />

            {/* Top Decor Blob */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-tertiary rounded-bl-full opacity-20 pointer-events-none transform translate-x-20 -translate-y-20" />

            {/* Bottom Decor Blob */}
            <div className="absolute bottom-0 left-0 w-80 h-80 bg-secondary rounded-tr-full opacity-10 pointer-events-none transform -translate-x-20 translate-y-20" />

            <header className="relative z-10 py-6 border-b-2 border-slate-200 bg-white/80 backdrop-blur-md sticky top-0">
                <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center shadow-pop text-white font-bold text-xl">
                            🩺
                        </div>
                        <h1 className="text-2xl font-heading font-extrabold tracking-tight">
                            Clinical <span className="text-accent">Risk</span> Insight
                        </h1>
                    </div>
                    <nav className="hidden md:flex gap-6 font-bold text-sm uppercase tracking-wide">
                        <a href="#upload" className="hover:text-accent transition-colors">Upload</a>
                        <a href="#dashboard" className="hover:text-accent transition-colors">Dashboard</a>
                        <a href="#drugs" className="hover:text-accent transition-colors">Drugs</a>
                    </nav>
                </div>
            </header>

            <main className="relative z-10 max-w-6xl mx-auto px-6 py-12">
                {children}
            </main>

            <footer className="py-8 text-center text-muted-foreground text-sm font-medium">
                <p>© 2026 Clinical Risk Insight Tool. For educational use only.</p>
            </footer>
        </div>
    );
};
