# ---------- build stage ----------------------------------------------
FROM python:3.11 AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y curl g++ gcc git make
RUN pip install --no-cache-dir tree_sitter
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && npm install -g tree-sitter-cli node-gyp node-gyp-build node-addon-api

# Clone grammar repos (add more as needed)
RUN git clone --depth 1 https://github.com/tree-sitter/tree-sitter-c.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-css.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-html.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-json.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-typescript.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-javascript.git && \
    git clone --depth 1 https://github.com/tree-sitter/tree-sitter-c-sharp.git
    
# Ensure JS grammar is importable as a directory (for typescript/tsx)
RUN mkdir -p /build/tree-sitter-javascript/grammar && \
    cp /build/tree-sitter-javascript/grammar.js /build/tree-sitter-javascript/grammar/index.js

# Add package.json so Node can resolve the grammar directory as a module
RUN echo '{"name": "tree-sitter-javascript-grammar", "main": "index.js"}' > /build/tree-sitter-javascript/grammar/package.json

# Symlink so Node can resolve require('tree-sitter-javascript/grammar')
RUN mkdir -p /build/node_modules/tree-sitter-javascript && \
    ln -s /build/tree-sitter-javascript/grammar /build/node_modules/tree-sitter-javascript/grammar

# Generate all grammars from /build so relative imports work for typescript/tsx
WORKDIR /build
RUN tree-sitter generate tree-sitter-c/grammar.js
RUN tree-sitter generate tree-sitter-css/grammar.js
RUN tree-sitter generate tree-sitter-html/grammar.js
RUN tree-sitter generate tree-sitter-json/grammar.js
RUN tree-sitter generate tree-sitter-javascript/grammar.js
RUN tree-sitter generate tree-sitter-typescript/typescript/grammar.js
RUN tree-sitter generate tree-sitter-typescript/tsx/grammar.js
RUN tree-sitter generate tree-sitter-c-sharp/grammar.js

# Build the shared library
RUN gcc -fPIC \
    -I./tree-sitter-c/src \
    -I./tree-sitter-css/src \
    -I./tree-sitter-html/src \
    -I./tree-sitter-json/src \
    -I./tree-sitter-javascript/src \
    -I./tree-sitter-typescript/typescript/src \
    -I./tree-sitter-typescript/tsx/src \
    -I./tree-sitter-c-sharp/src \
    -shared \
    tree-sitter-c/src/parser.c \
    tree-sitter-css/src/parser.c tree-sitter-css/src/scanner.c \
    tree-sitter-html/src/parser.c tree-sitter-html/src/scanner.c \
    tree-sitter-json/src/parser.c \
    tree-sitter-javascript/src/parser.c tree-sitter-javascript/src/scanner.c \
    tree-sitter-typescript/typescript/src/parser.c tree-sitter-typescript/typescript/src/scanner.c \
    tree-sitter-typescript/tsx/src/parser.c tree-sitter-typescript/tsx/src/scanner.c \
    tree-sitter-c-sharp/src/parser.c tree-sitter-c-sharp/src/scanner.c \
    -o /build/my-languages.so

# ---------- runtime stage ----------------------------------------------
FROM python:3.11

WORKDIR /srv
COPY --from=builder /build/my-languages.so /srv/my-languages.so
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt
COPY app.py .

ENV TS_LIB=/srv/my-languages.so
EXPOSE 9000
CMD ["python", "app.py"]
