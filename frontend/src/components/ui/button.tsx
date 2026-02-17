import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
        const baseStyles = "inline-flex items-center justify-center font-bold transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] active:scale-95 disabled:pointer-events-none disabled:opacity-50";

        // "Candy Button" style vs Secondary
        const variants = {
            primary: `
        bg-accent text-white border-2 border-foreground rounded-full
        shadow-[4px_4px_0px_0px_rgba(30,41,59,1)]
        hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[6px_6px_0px_0px_rgba(30,41,59,1)]
        active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0px_0px_rgba(30,41,59,1)]
      `,
            secondary: `
        bg-transparent text-foreground border-2 border-foreground rounded-full
        hover:bg-tertiary
      `,
            ghost: `
        bg-transparent text-foreground hover:bg-muted
      `
        };

        const sizes = {
            sm: "h-9 px-4 text-sm",
            md: "h-12 px-8 text-base",
            lg: "h-14 px-10 text-lg",
        };

        return (
            <button
                ref={ref}
                className={cn(baseStyles, variants[variant], sizes[size], className)}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button, cn };
