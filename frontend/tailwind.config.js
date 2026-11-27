/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./hooks/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        x: {
          bg: "#090D12",
          surface: "#151C25",
          border: "#202A36",
          blue: "#1D9BF0",
          positive: "#16A36A",
          negative: "#D65353",
          neutral: "#71767B",
        },
        brand: "#1D9BF0",
      },
    },
  },
  plugins: [],
};
