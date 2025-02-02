#!/bin/bash
mkdir -p static/{css,js}

# Download htmx
curl -L https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js -o static/js/htmx.min.js

# Download TailwindCSS
curl -L https://cdn.tailwindcss.com/3.4.1 -o static/css/tailwind.min.css