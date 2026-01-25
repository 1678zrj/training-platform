docker run -d ^
  --name my-nginx2 ^
  --network jupyter-bridge-net ^
  -p 80:80 ^
  --add-host=host.docker.internal:host-gateway ^
  -v %cd%\nginx.conf:/etc/nginx/conf.d/default.conf ^
  -v %cd%\..\..\backend\media:/data/media ^
  nginx:latest
