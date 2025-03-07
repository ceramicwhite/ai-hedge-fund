import React from 'react';

export const Card = ({ className, ...props }) => {
  return (
    <div className={`bg-white border rounded-lg shadow-sm ${className || ''}`} {...props} />
  );
};

export const CardHeader = ({ className, ...props }) => {
  return (
    <div className={`p-4 ${className || ''}`} {...props} />
  );
};

export const CardTitle = ({ className, ...props }) => {
  return (
    <h3 className={`text-lg font-semibold ${className || ''}`} {...props} />
  );
};

export const CardDescription = ({ className, ...props }) => {
  return (
    <p className={`text-sm text-gray-500 ${className || ''}`} {...props} />
  );
};

export const CardContent = ({ className, ...props }) => {
  return (
    <div className={`p-4 pt-0 ${className || ''}`} {...props} />
  );
};

export const CardFooter = ({ className, ...props }) => {
  return (
    <div className={`p-4 border-t ${className || ''}`} {...props} />
  );
};