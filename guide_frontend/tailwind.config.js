/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        intelleo: {
          bg: '#F0F8FF',      // AliceBlue
          text: '#1F2937',    // Gray-800
          primary: '#1E3A8A', // Blue-900 (Sidebar/Nav)
          accent: '#1D4ED8',  // Blue-700 (Buttons/Highlights)
          border: '#E5E7EB',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
