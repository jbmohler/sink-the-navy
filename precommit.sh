docker run -it --rm -u 1000:1000 -v ${PWD}/frontend:/app -w /app node:20 npx prettier src/ --write --single-quote

flake8 backend
black backend
