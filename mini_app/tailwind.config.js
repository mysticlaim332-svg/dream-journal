/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        dream: {
          bg:      '#0B0C1E',   // deep space background
          surface: '#13142A',   // card surface
          card:    '#1C1E38',   // elevated card
          border:  '#2A2D50',   // subtle border
          purple:  '#7B6DE8',   // primary accent
          teal:    '#4ECDC4',   // secondary accent
          gold:    '#F7B731',   // dream highlight
          text:    '#E8E8F5',   // main text
          muted:   '#8888AA',   // muted text
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
