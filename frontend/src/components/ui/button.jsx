import React from 'react';

export const Button = ({ 
  children, 
  variant = 'default', 
  className = '', 
  ...props 
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'outline':
        return 'border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50';
      case 'destructive':
        return 'bg-red-600 text-white hover:bg-red-700';
      case 'ghost':
        return 'bg-transparent hover:bg-gray-100';
      case 'link':
        return 'bg-transparent text-blue-600 hover:underline';
      default:
        return 'bg-blue-600 text-white hover:bg-blue-700';
    }
  };

  return (
    <button
      className={`px-4 py-2 rounded-md font-medium text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 ${getVariantClasses()} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};