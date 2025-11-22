/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'japan': '#BC002D',
        'china': '#DE2910',
        'usa': '#002868',
        'germany': '#000000',
        'taiwan': '#000095',
      },
    },
  },
  plugins: [],
}



