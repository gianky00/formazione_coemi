import React from 'react';

const Step = ({ number, title, children }) => {
  return (
    <div className="flex gap-4 mb-8 last:mb-0 relative">
      {/* Line connecting steps */}
      <div className="absolute top-8 left-4 bottom-[-32px] w-0.5 bg-gray-200 last:hidden"></div>

      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-intelleo-accent text-white flex items-center justify-center font-bold text-sm shadow-md z-10">
        {number}
      </div>
      <div className="flex-1 pt-1">
        <h4 className="text-base font-bold text-gray-900 mb-2">{title}</h4>
        <div className="text-gray-600 text-sm leading-relaxed">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Step;
