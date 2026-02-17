import React from 'react';
import { cn } from './button';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, label, ...props }, ref) => {
        return (
            <div className="w-full">
                {label && (
                    <label className="block text-sm font-bold uppercase tracking-wide mb-1 text-foreground">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={cn(
                        "flex h-12 w-full rounded-lg border-2 border-slate-300 bg-white px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:border-accent focus-visible:shadow-[4px_4px_0px_0px_#8B5CF6] transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50",
                        className
                    )}
                    {...props}
                />
            </div>
        );
    }
);
Input.displayName = "Input";

export { Input };
