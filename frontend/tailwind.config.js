/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'primary': '#eead2b',
        'background-light': '#fcfaf8',
        'background-dark': '#121212',
        'text-light': '#1b170d',
        'text-dark': '#f3efe7',
        'surface-light': '#f3efe7',
        'surface-dark': '#1e1e1e',
        'muted': '#9ca3af',
      },
    },
  },
  plugins: [],
}
