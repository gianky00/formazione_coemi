import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import PropTypes from 'prop-types';

const GuideCard = ({ children, className, title, icon: Icon, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay, duration: 0.4 }}
      className={clsx("card", className)}
    >
      {(title || Icon) && (
        <div className="flex items-center gap-3 mb-4 border-b border-gray-100 pb-3">
          {Icon && (
            <div className="p-2 bg-blue-50 text-intelleo-accent rounded-lg">
              <Icon size={20} />
            </div>
          )}
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
        </div>
      )}
      <div className="text-gray-600 leading-relaxed">
        {children}
      </div>
    </motion.div>
  );
};

GuideCard.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  title: PropTypes.string,
  icon: PropTypes.elementType,
  delay: PropTypes.number,
};

export default GuideCard;
