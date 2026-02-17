import React from 'react';
import { cn } from './button'; // reusing cn from button for now, should move to utils

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'featured';
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "bg-white border-2 border-slate-900 rounded-xl transition-all duration-300",
                    variant === 'default' && "shadow-[8px_8px_0px_0px_#E2E8F0] hover:rotate-[-1deg] hover:scale-[1.02]",
                    variant === 'featured' && "shadow-[8px_8px_0px_0px_#F472B6] hover:rotate-[1deg] hover:scale-[1.02]",
                    className
                )}
                {...props}
            />
        );
    }
);
Card.displayName = "Card";

export { Card };
