import React from 'react'
import clsx from 'clsx'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, iconPosition = 'left', ...props }, ref) => {
    const baseStyles = 'w-full px-4 py-3 border rounded-lg bg-surface-0 text-surface-900 placeholder-surface-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200'
    
    const variants = {
      default: 'border-surface-200 focus:ring-primary-500 focus:border-primary-500',
      error: 'border-red-300 focus:ring-red-500 focus:border-red-500'
    }

    const inputStyles = clsx(
      baseStyles,
      error ? variants.error : variants.default,
      icon && iconPosition === 'left' && 'pl-11',
      icon && iconPosition === 'right' && 'pr-11',
      className
    )

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-surface-700 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-surface-400">{icon}</span>
            </div>
          )}
          <input
            className={inputStyles}
            ref={ref}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-surface-400">{icon}</span>
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
