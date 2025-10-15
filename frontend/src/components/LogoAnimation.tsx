'use client'

import { motion } from 'framer-motion'
import { useEffect } from 'react'

interface LogoAnimationProps {
  onComplete: () => void
}

export default function LogoAnimation({ onComplete }: LogoAnimationProps) {
  useEffect(() => {
    // Trigger onComplete after animation duration
    const timer = setTimeout(onComplete, 2000)
    return () => clearTimeout(timer)
  }, [onComplete])

  return (
    <motion.div
      initial={{ opacity: 1, scale: 1 }}
      animate={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 2, ease: 'easeInOut' }}
      className="flex flex-col items-center justify-center"
    >
      <div className="text-center">
        <h1 className="text-6xl md:text-8xl font-bold text-blue-600 mb-4">
          RYX
        </h1>
        <p className="text-xl md:text-2xl text-gray-600">
          Billing Software
        </p>
      </div>
    </motion.div>
  )
}
