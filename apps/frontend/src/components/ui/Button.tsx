import { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "outline" | "ghost";
type Size = "md" | "lg";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-primary-container text-on-primary-container hover:opacity-90 shadow-[0_0_20px_rgba(0,255,157,0.15)]",
  secondary:
    "bg-white/5 border border-white/10 text-on-surface hover:bg-white/10",
  outline:
    "border border-outline-variant text-on-surface hover:border-primary-container hover:text-primary-container",
  ghost: "text-on-surface-variant hover:text-primary-container",
};

const sizeClasses: Record<Size, string> = {
  md: "px-6 py-2.5 rounded-lg font-label-md text-label-md",
  lg: "px-8 py-4 rounded-lg font-label-md text-label-md",
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
  iconPosition?: "left" | "right";
}

export function Button({
  variant = "primary",
  size = "md",
  icon,
  iconPosition = "right",
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-bold transition-all active:scale-95 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {icon && iconPosition === "left" && icon}
      {children}
      {icon && iconPosition === "right" && icon}
    </button>
  );
}
