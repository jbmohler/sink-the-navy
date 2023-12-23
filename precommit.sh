docker run -it --rm -u 1000:1000 -v ${PWD}/frontend:/app -w /app node:18 npx prettier src/ --write --single-quote

black backend
