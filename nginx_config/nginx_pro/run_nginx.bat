docker run -d ^
  --name nginx-pro ^
  --network jupyter-bridge-net ^
  -p 80:80 ^
  --add-host=host.docker.internal:host-gateway ^
  -v "D:\mycode\python\training-platform\nginx_config\nginx_pro\nginx.conf:/etc/nginx/conf.d/default.conf" ^
  -v "D:\mycode\python\training-platform\frontend\dist:/usr/share/nginx/html" ^
  nginx:latest
