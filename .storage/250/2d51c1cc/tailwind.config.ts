import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        routix: {
          purple: '#6B5DD3',
          'purple-light': '#8B7AFF',
          blue: '#7AA3FF',
        },
        text: {
          primary: '#2D2A4A',
          secondary: '#6B6B8D',
          muted: '#A0A0B8',
        },
      },
      backgroundImage: {
        'gradient-main': 'linear-gradient(135deg, #E0C3FC 0%, #D5E1FF 25%, #E8F4FF 50%, #FFE8F5 75%, #FFE5E5 100%)',
        'gradient-purple': 'linear-gradient(135deg, #6B5DD3 0%, #8B7AFF 100%)',
        'gradient-blue': 'linear-gradient(135deg, #7AA3FF 0%, #A8C5FF 100%)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      backdropBlur: {
        'xl': '20px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(31, 38, 135, 0.08)',
        'glass-hover': '0 12px 40px rgba(31, 38, 135, 0.12)',
        'button': '0 4px 15px rgba(107, 93, 211, 0.3)',
        'button-hover': '0 6px 20px rgba(107, 93, 211, 0.4)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
    },
  },
  plugins: [],
}

export default config