docker run -d ^
  --name my-nginx ^
  --network jupyter-bridge-net ^
  -p 80:80 ^
  -v %cd%\nginx.conf:/etc/nginx/conf.d/default.conf ^
  nginx:latest
