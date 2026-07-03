import { InputHTMLAttributes, TextareaHTMLAttributes, SelectHTMLAttributes, ReactNode } from "react";

interface FieldWrapperProps {
  label?: string;
  hint?: string;
  children: ReactNode;
}

function FieldWrapper({ label, hint, children }: FieldWrapperProps) {
  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label className="font-label-sm text-label-sm text-on-surface-variant">
          {label}
        </label>
      )}
      {children}
      {hint && (
        <p className="text-[10px] text-on-surface-variant/60">{hint}</p>
      )}
    </div>
  );
}

const fieldClasses =
  "w-full bg-black/20 border border-white/10 rounded-lg py-3 px-4 text-on-surface placeholder:text-on-surface-variant/40 font-body-md text-body-md focus:outline-none focus:border-primary-container focus:ring-0 transition-all";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
}

export function Input({ label, hint, className = "", ...props }: InputProps) {
  return (
    <FieldWrapper label={label} hint={hint}>
      <input className={`${fieldClasses} ${className}`} {...props} />
    </FieldWrapper>
  );
}

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
}

export function Textarea({
  label,
  hint,
  className = "",
  ...props
}: TextareaProps) {
  return (
    <FieldWrapper label={label} hint={hint}>
      <textarea className={`${fieldClasses} ${className}`} {...props} />
    </FieldWrapper>
  );
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: string;
}

export function Select({
  label,
  hint,
  className = "",
  children,
  ...props
}: SelectProps) {
  return (
    <FieldWrapper label={label} hint={hint}>
      <select className={`${fieldClasses} appearance-none ${className}`} {...props}>
        {children}
      </select>
    </FieldWrapper>
  );
}
