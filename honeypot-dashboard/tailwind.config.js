/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0D12',
        surface: '#12161D',
        surface2: '#171C25',
        border: '#232A35',
        ink: '#E4E9F0',
        muted: '#7C8798',
        amber: '#FFB020',
        critical: '#FF4557',
        safe: '#3DDC97',
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
