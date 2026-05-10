# Smart Task Manager — static frontend served by nginx

FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy only public assets (avoid leaking nginx.conf / Dockerfile via document root).
COPY frontend/*.html /usr/share/nginx/html/
COPY frontend/*.js /usr/share/nginx/html/
COPY frontend/*.css /usr/share/nginx/html/

EXPOSE 80
