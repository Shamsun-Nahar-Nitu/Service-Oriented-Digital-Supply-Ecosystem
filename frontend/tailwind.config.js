/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#F1F3F8',
          100: '#DDE1EC',
          200: '#B9C0D6',
          300: '#8D97B6',
          400: '#5F6B93',
          500: '#404B73',
          600: '#2C3559',
          700: '#1F2645',
          800: '#141A33',
          900: '#0C1024',
          950: '#070A17',
        },
        ember: {
          50: '#FFF4ED',
          100: '#FFE4D3',
          200: '#FFC5A3',
          300: '#FF9E6B',
          400: '#FF7A3D',
          500: '#FF5A1F',
          600: '#ED3F0A',
          700: '#C42E05',
          800: '#9C260C',
          900: '#7E220F',
        },
        gold: {
          50: '#FFF9EB',
          100: '#FFEFC3',
          200: '#FFDD85',
          300: '#FFC547',
          400: '#FFB020',
          500: '#F79300',
          600: '#D97300',
          700: '#B45400',
        },
        canvas: {
          DEFAULT: '#F5F6F8',
          soft: '#FBFBFC',
          raised: '#FFFFFF',
        },
        success: {
          50: '#EAFBF4',
          100: '#CDF4E3',
          500: '#1AA179',
          600: '#0F8163',
          700: '#0B6650',
        },
        danger: {
          50: '#FDEEEC',
          100: '#FAD6D1',
          500: '#E3413D',
          600: '#C22E2B',
          700: '#9E2523',
        },
      },
      fontFamily: {
        display: ['"Sora"', 'system-ui', 'sans-serif'],
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(12, 16, 36, 0.06), 0 1px 1px rgba(12, 16, 36, 0.04)',
        raised: '0 8px 24px -8px rgba(12, 16, 36, 0.18)',
        popover: '0 12px 32px -8px rgba(12, 16, 36, 0.28)',
      },
      borderRadius: {
        xl: '0.875rem',
        '2xl': '1.25rem',
      },
      keyframes: {
        'slide-up': {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'slide-up': 'slide-up 0.2s ease-out',
        'fade-in': 'fade-in 0.15s ease-out',
      },
    },
  },
  plugins: [],
}
