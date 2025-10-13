/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        aws: {
          orange: '#ff9900',
          dark: '#232f3e',
        },
        severity: {
          critical: '#d13212',
          high: '#ff9900',
          medium: '#1d8102',
          low: '#879596',
        }
      },
    },
  },
  plugins: [],
}
