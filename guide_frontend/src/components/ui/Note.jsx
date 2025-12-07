import React from 'react';
import { Info, AlertTriangle, CheckCircle, Lightbulb } from 'lucide-react';
import clsx from 'clsx';
import PropTypes from 'prop-types';

const Note = ({ type = 'info', children, title }) => {
  const styles = {
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: Info,
      iconColor: 'text-blue-600'
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: AlertTriangle,
      iconColor: 'text-yellow-600'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: CheckCircle,
      iconColor: 'text-green-600'
    },
    tip: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-800',
      icon: Lightbulb,
      iconColor: 'text-purple-600'
    }
  };

  const config = styles[type] || styles.info;
  const Icon = config.icon;

  return (
    <div className={clsx("p-4 rounded-lg border flex gap-3 my-4", config.bg, config.border)}>
      <div className={clsx("shrink-0 mt-0.5", config.iconColor)}>
        <Icon size={20} />
      </div>
      <div className="flex-1">
        {title && <h5 className={clsx("font-semibold mb-1", config.text)}>{title}</h5>}
        <div className={clsx("text-sm leading-relaxed opacity-90", config.text)}>
          {children}
        </div>
      </div>
    </div>
  );
};

Note.propTypes = {
  type: PropTypes.oneOf(['info', 'warning', 'success', 'tip']),
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
};

export default Note;
