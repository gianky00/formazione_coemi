import React from 'react';
import clsx from 'clsx';

const Badge = ({ children, variant = 'default', className }) => {
  const styles = {
    default: 'bg-gray-100 text-gray-800 border-gray-200',
    primary: 'bg-blue-100 text-blue-800 border-blue-200',
    success: 'bg-green-100 text-green-800 border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    danger: 'bg-red-100 text-red-800 border-red-200',
    purple: 'bg-purple-100 text-purple-800 border-purple-200',
  };

  return (
    <span
      className={clsx(
        "px-2.5 py-0.5 rounded-full text-xs font-medium border inline-flex items-center",
        styles[variant] || styles.default,
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
