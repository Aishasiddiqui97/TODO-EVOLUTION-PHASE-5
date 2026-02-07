/**
 * WebSocket Status Banner Component
 * Shows a helpful banner when WebSocket service is not running
 */
'use client'

import { motion, AnimatePresence } from 'framer-motion'

interface WebSocketStatusBannerProps {
  connected: boolean
  reconnecting: boolean
  error?: string
}

export function WebSocketStatusBanner({ connected, reconnecting, error }: WebSocketStatusBannerProps) {
  // Don't show banner if connected
  if (connected) return null

  // Show reconnecting state
  if (reconnecting) {
    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          style={{
            position: 'fixed',
            top: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9999,
            background: 'rgba(255, 165, 0, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '2px solid #ffa500',
            borderRadius: '12px',
            padding: '16px 24px',
            boxShadow: '0 4px 20px rgba(255, 165, 0, 0.3)',
            maxWidth: '500px',
            width: '90%'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '20px',
              height: '20px',
              border: '3px solid #fff',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <div>
              <div style={{ fontWeight: 'bold', color: '#fff', marginBottom: '4px' }}>
                🔄 Reconnecting to real-time sync...
              </div>
              <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.9)' }}>
                Attempting to restore connection
              </div>
            </div>
          </div>
          <style jsx>{`
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}</style>
        </motion.div>
      </AnimatePresence>
    )
  }

  // Show error state with helpful instructions
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -50 }}
        style={{
          position: 'fixed',
          top: '80px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 9999,
          background: 'rgba(255, 0, 110, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '2px solid #ff006e',
          borderRadius: '12px',
          padding: '20px 24px',
          boxShadow: '0 4px 20px rgba(255, 0, 110, 0.3)',
          maxWidth: '600px',
          width: '90%'
        }}
      >
        <div style={{ color: '#fff' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <span style={{ fontSize: '24px' }}>🔴</span>
            <div>
              <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '4px' }}>
                Real-time sync unavailable
              </div>
              <div style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.9)' }}>
                WebSocket service is not running
              </div>
            </div>
          </div>
          
          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            fontSize: '13px',
            marginTop: '12px'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>💡 Quick Fix:</div>
            <ol style={{ margin: '0', paddingLeft: '20px', lineHeight: '1.6' }}>
              <li>Open a new Command Prompt</li>
              <li>Run: <code style={{
                background: 'rgba(255, 255, 255, 0.2)',
                padding: '2px 6px',
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>start-websocket-fixed.bat</code></li>
              <li>Wait for "Application startup complete"</li>
              <li>Refresh this page</li>
            </ol>
          </div>

          <div style={{
            marginTop: '12px',
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.8)',
            fontStyle: 'italic'
          }}>
            Note: Chat will still work, but you won't see real-time updates
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
