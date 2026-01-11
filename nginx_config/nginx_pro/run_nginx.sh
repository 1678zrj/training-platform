docker run -d \
  --name my-nginx \
  --network jupyter-bridge-net \
  -p 80:80 \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf \
  -v $(pwd)/frontend/dist:/usr/share/nginx/html \
  nginx:latest