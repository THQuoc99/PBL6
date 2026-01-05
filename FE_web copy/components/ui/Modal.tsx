import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import React from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string | React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export default function Modal({ open, onClose, title, children, footer }: ModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/50"
            onClick={onClose}
          />
          {/* Use a full-screen flex container so the modal centers reliably */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="w-full max-w-4xl max-h-[90vh] rounded-2xl border border-gray-200 bg-white shadow-lg flex flex-col"
            >
              {/* Header - fixed */}
              <div className="flex items-start justify-between p-6 pb-4 border-b border-gray-100">
                <div className="flex-1">
                  {typeof title === 'string' ? (
                    <h2 className="text-lg font-semibold">{title}</h2>
                  ) : (
                    title
                  )}
                </div>
                <button
                  onClick={onClose}
                  className="rounded-lg border border-gray-200 p-1 hover:bg-gray-50 ml-4 flex-shrink-0"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Content - scrollable */}
              <div className="flex-1 overflow-y-auto px-6 py-4">
                {children}
              </div>

              {/* Footer - fixed */}
              {footer && (
                <div className="border-t border-gray-100 p-6 pt-4">
                  <div className="flex justify-end gap-2">{footer}</div>
                </div>
              )}
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}